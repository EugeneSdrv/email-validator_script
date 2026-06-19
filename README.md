# Email Validator Script

Приложение на Python для валидации и нормализации email адресов с использованием внешнего API сервиса. Полученные результаты сохраняются в CSV файл для последующей обработки.

## Описание

Приложение выполняет следующие функции:

- **Отправка запросов** к внешнему API через библиотеку `httpx`
- **Валидация данных** с помощью `pydantic` моделей
- **Преобразование email адресов** (нормализация, исправление опечаток)
- **Сохранение результатов** в файл `email.csv` в корне проекта
- **Анализ качества** преобразований через поля `type` и `qc`
---

## Основные требования

```
- Python 3.13+
- Git
```
---
## Установка зависимостей 


1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/EugeneSdrv/email-validator_script.git
   cd email-validator_script
   ```

2. **Установите зависимости вручную**

   Для установки вручную необходимо наличие uv(менеджер пакетов).

   ```bash
   uv add httpx pydantic python3.13
   ```

3. **Или используйте pyproject.toml:**
   ```bash
   uv sync pyproject.toml
   ```
---
## 🚀 Установка и запуск с помощью Docker

### Требования
- Docker 20.10+

### Быстрый старт

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/EugeneSdrv/email-validator_script.git
   cd email-validator_script
   ```

2. **Соберите образ**
   ```bash
   docker build -t email-validator_script:latest .
   ```

3. **Запустите контейнер**
   ```bash
   docker run --rm email-validator_script:latest
   ```

## Структура проекта

```
email-validator_script/
├── .gitignore              # Файл для исключения файлов из версионирования
├── python-version.txt      # Версия Python для проекта
├── Dockerfile              # Конфигурация docker-образа проекта
├── result_email.csv        # Выходной файл (создаётся автоматически)
├── main.py                 # Основной файл приложения
├── pyproject.toml          # Конфигурация и зависимости проекта
├── README.md               # Документация проекта
└── uv.lock                 # Блокировка версий зависимостей
```
___

## Лицензия

MIT License
___

## Поддержка

Для сообщения об ошибках или предложений по улучшению создавайте Issues в репозитории.
___

## Версия
**0.0.2**
___
