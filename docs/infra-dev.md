# Инфраструктура: Dev-окружение

Документ описывает, как разворачивать и поддерживать локальное окружение для разработки CRM BFF.

---

## 1. Требования

- Python 3.12+
- Docker Desktop / Docker Engine 24+
- Make (опционально), Node.js 18+ (для Tailwind)
- VS Code / PyCharm, Poetry или pip-tools (по желанию)

---

## 2. Переменные окружения

Создайте файл `.env` в корне (используйте `.env.example` как шаблон):

```
POSTGRES_DB=crm_dev
POSTGRES_USER=crm_dev
POSTGRES_PASSWORD=crm_dev
REDIS_URL=redis://redis:6379/0
BACKEND_API_URL=http://crm_backend:8000/api/v1
FRONTEND_URL=http://localhost:8000
DJANGO_SECRET_KEY=local-secret
```

Frontend/Backend используют разные `.env` (например, `crm_backend/.env`, `crm_frontend/.env`). Ссылки на backend указывайте внутреконтейнерные (`http://crm_backend:8000`).

---

## 3. Docker Compose (dev)

Базовый файл `docker-compose.yml` содержит сервисы:

- `backend`: Django + Gunicorn (или runserver для удобства).
- `frontend`: Django + runserver / Gunicorn.
- `postgres`: Volume `pgdata`.
- `redis`: in-memory.
- `celery`, `celery-beat` (по мере необходимости).
- `nginx`: reverse proxy (optional для dev, но полезно для parity).

Команды:

```bash
docker compose up --build
docker compose run --rm backend python manage.py migrate
docker compose run --rm frontend python manage.py migrate
```

---

## 4. Локальные инструменты

- **pre-commit**: `pre-commit install`.
- **pytest**: `docker compose run --rm backend pytest`.
- **Tailwind**: `docker compose run --rm frontend npm run dev:css`.
- **Fixtures**: `docker compose run --rm backend python manage.py loaddata fixtures/dev_seed.json`.

---

## 5. Observability (dev)

- Логи выводятся в консоль (`docker compose logs -f`).
- Локальный Sentry можно заменить на console logging.
- Health-checkи доступны по `/healthz` (backend) и `/status/` (frontend).

---

## 6. Reset окружения

```bash
docker compose down -v       # удалить контейнеры и volume'ы
docker compose up --build    # пересобрать
```

Если нужно очистить локальные миграции/кеши, удалите `crm_backend/db.sqlite3` (если используется), либо переразверните Postgres volume.
