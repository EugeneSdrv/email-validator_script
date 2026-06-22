import sys
import csv
from datetime import datetime, timezone
import time
import logging
from pathlib import Path

import httpx
from pydantic import BaseModel, ValidationError

TOKEN: str = ""
SECRET: str = ""
email: list[str] = ["serega@yandex/ru"]

logger = logging.getLogger(__name__)

if len(sys.argv) > 1:
    email = [sys.argv[1]]
    logger.info(f"Получен email: {email}")
else:
    logger.error("Ошибка: укажите email как параметр")

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
    with open('data/email_results.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=adapters[0].keys())
        writer.writeheader()
        writer.writerows(adapters)

def send_request(email_in: list) -> httpx.Response | None:
    max_retries = 3
    base_delay = 1.0
    status_forcelist = (429, 500, 502, 503, 504)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {TOKEN}",
        "X-Secret": SECRET,
    }
    for attempt in range(max_retries + 1):
        try:
            response = httpx.post(
                url='https://cleaner.dadata.ru/api/v1/clean/email',
                headers=headers,
                json=email_in,
                timeout=10
            )
            if response.status_code in status_forcelist and attempt < max_retries:
                delay = base_delay + (attempt * 0.5)
                time.sleep(delay)
                continue
            return response
        except (httpx.NetworkError, httpx.TimeoutException) as e:
            if attempt == max_retries:
                raise e
    return None

def process_email_data_to_csv_record(raw_email_info):
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
    adapters_vars = [process_email_data_to_csv_record(raw_email) for raw_email in raw_email_info_data if raw_email is not None]
    if adapters_vars:
        Path('data').mkdir(exist_ok=True)
        save_email_info_to_csv(adapters_vars)

if __name__ == "__main__":
    main()
