import csv
from datetime import datetime, timezone
import json
import logging

import httpx
from pydantic import BaseModel, ValidationError

token = "e41ee64c1c4e326d207e0362ae20bb46d76bb969"
secret = "81cac1d4980ab5242094483cf15a7c6381891006"
email = ["serega@yandex/ru"]


class ResponseIn(BaseModel):
    source: str
    email: str
    local: str
    domain: str
    type: str
    qc: int

class ToCSVAdapterError(Exception):
    def __init__(self, field, possible_values, value):
        self.field = field
        self.value = value
        self.values = ", ".join(map(str, possible_values.keys()))

    def __str__(self):
        return f"Поле '{self.field}' может содержать только значения: {self.values} \nполученное значение: {self.value}"

class ToCSVAdapter:
    verification_description_by_code = {
        0: "Корректное значение соответствует общепринятым правилам",
        1: "Некорректное значение. Не соответствует общепринятым правилам",
        2: "Пустое или заведомо «мусорное» значение",
        3: "«Одноразовый» адрес. Домены 10minutemail.com, getairmail.com, temp-mail.ru и аналогичные",
        4: "Исправлены опечатки",
    }
    email_type = {
        "PERSONAL": "личный",  # (@mail.ru, @yandex.ru)
        "CORPORATE": "корпоративный",  # (@myshop.ru)
        "ROLE": "ролевой",  # (info@, support@)
        "DISPOSABLE": "одноразовый",  # (@temp-mail.ru)
    }

    def __init__(self, response_data):
        self.email = response_data.email
        self.domain = response_data.domain
        if self._validate_field(field=response_data.type, cls_field_name="email_type"):
            setattr(self, "email_type", self.email_type[response_data.type])
        if self._validate_field(field=response_data.qc, cls_field_name="verification_description_by_code"):
            setattr(self, "verification_description", self.verification_description_by_code[response_data.qc])

    def _validate_field(self, field, cls_field_name: str):
        possible_values = getattr(self, cls_field_name)
        if field not in possible_values:
            raise ToCSVAdapterError(cls_field_name, possible_values, field)
        else:
            return True

def save_email_info_to_csv(adapters):
    with open('email.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=adapters[0].keys())
        writer.writeheader()
        writer.writerows(adapters)



def send_request(email_in: list) -> httpx.Response | None:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {token}",
        "X-Secret": secret,
    }
    # TODO: обработать ошибки недоступности API, возможно добавить ретраи
    try:
        return httpx.post(
            url='https://cleaner.dadata.ru/api/v1/clean/email',
            headers=headers,
            json=email_in,
        )
    except:
        raise


def process_email_data_to_csv_record(raw_email_info):
    logger = logging.getLogger(__name__)
    try:
        email_info_data: ResponseIn = ResponseIn.model_validate(raw_email_info)
        return vars(ToCSVAdapter(email_info_data))
    except (ValidationError, ToCSVAdapterError) as e:
        logger.warning(
            f"Ошибка валидации входящих данных {raw_email_info}: \n{e}",
            extra={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "raw_data": raw_email_info,
                "validation_errors": e,
            }
        )

def main():
    response = send_request(email)
    raw_email_info_data = response.json()
    adapters_vars = [process_email_data_to_csv_record(raw_email_info) for raw_email_info in raw_email_info_data]
    if adapters_vars[0]:
        save_email_info_to_csv(adapters_vars)


if __name__ == "__main__":
    main()
