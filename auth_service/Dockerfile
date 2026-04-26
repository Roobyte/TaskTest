FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --with dev --no-interaction --no-ansi

COPY app/ app/
COPY tests/ tests/
COPY pytest.ini .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
