FROM python:3.13-slim
LABEL authors="EugenSdrv"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /script

COPY uv.lock pyproject.toml /script/

RUN uv venv
RUN uv sync --frozen --no-cache

ENV PATH="/script/.venv/bin:$PATH"

COPY main.py /script

CMD ["python", "/script/main.py"]

