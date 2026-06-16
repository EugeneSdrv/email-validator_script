import csv
import json

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


class ToCSVAdapter:
    verification_description_by_code = {
        0: "Корректное значение соответствует общепринятым правилам",
        2: "Пустое или заведомо «мусорное» значение",
        3: "«Одноразовый» адрес. Домены 10minutemail.com, getairmail.com, temp-mail.ru и аналогичные",
        1: "Некорректное значение. Не соответствует общепринятым правилам",
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
        if field not in getattr(self, cls_field_name):
            # TODO: динамически генерировать исключение связанное с ошибкой валидации конкретного поля
            # TODO: понять какой тип ошибки будет и убедиться, что мы ее обрабатываем
            raise ValidationError
        else:
            return True


def save_email_info_to_csv(adapters):
    with open('email.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=adapters[0].keys())
        writer.writeheader()
        writer.writerows(adapters)



def sent_request(email_in: str) -> Response:
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



def main():
    raw_email_info_data = load_response()
    # raw_email_info_data = sent_response(email)
    # TODO: обрабатывать ошибки с неверным форматом входящих данных
    try:
        for raw_email_info in raw_email_info_data:
            # TODO: возможно стоит выделить валидацию и обработку ошибок в отдельную функцию как в отправке запроса
            email_info_data : ResponseIn = ResponseIn.model_validate(raw_email_info)
            # TODO: сохранять в csv нужно список словарей а не один объект!!!
            save_email_info_to_csv(email_info_data)
            return email_info_data
    except ValidationError:
        # TODO: сохранить лог о том что не прошла обработка валидации, поэтому ... (либо - ретраи, либо - просто
        #  продолжать и сохранять почту, как необработанную)
        # raise  # не нужно райзить, а наоборот обрабатывать ошибку и продолжать выполнение программы
        # возможно можно райзануть HttpException с 4хх кодом ,например, данную строку не удалось обработать.
        # И сохранять логи, что данные по ней приходят невалидные (по структуре, что вряд ли может быть)
        pass


if __name__ == "__main__":
    main()
