# Auth & User Microservices

Проект состоит из двух FastAPI микросервисов:
- `user_service` — регистрация и проверка пользователя в PostgreSQL
- `auth_service` — выдача/проверка JWT и logout через blacklist в Redis

## Быстрый запуск после `git clone`

1) Перейти в директорию проекта:

```bash
cd TestsTask
```

2) Создать `.env` из шаблона:

Linux/macOS:
```bash
cp .env.example .env
```

Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

3) Запустить сервисы:

```bash
docker compose up -d --build
```

4) Проверить, что все контейнеры поднялись:

```bash
docker compose ps
```

Ожидаемые сервисы: `user-db`, `user-service`, `auth-redis`, `auth-service`.

## Полезные URL

- User health: `http://localhost:8000/health`
- User docs: `http://localhost:8000/docs`
- Auth docs: `http://localhost:8001/docs`

## Запуск тестов

```bash
docker compose run --rm auth-service python -m pytest
docker compose run --rm user-service python -m pytest
```

## Остановка

```bash
docker compose down
```

С удалением volume (сброс БД/Redis):

```bash
docker compose down -v
```

## Переменные окружения

Все обязательные переменные описаны в `.env.example`.

Почему именно такие значения:
- `POSTGRES_HOST=user-db`, `REDIS_HOST=auth-redis`, `USER_SERVICE_URL=http://user-service:8000` — это имена сервисов в сети `docker compose`.
- `DATABASE_URL` с `127.0.0.1:5435` используется для доступа с хоста, потому что в `docker-compose.yml` проброшен порт `5435:5432`.
- `AUTH_SECRET_KEY` должен быть длинным случайным секретом.
