# Tech Cheatsheet

Краткие шпаргалки по стеку проекта CRM BFF.

---

## Django / DRF

- Создание проекта: `django-admin startproject crm_backend`.
- Разделение настроек: `settings/base.py`, `settings/dev.py`, `settings/prod.py` (используем переменную `DJANGO_SETTINGS_MODULE`).
- Миграции: `python manage.py makemigrations`, `python manage.py migrate`.
- Admin-user: `python manage.py createsuperuser`.
- DRF ViewSet шаблон:

```python
class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ClientFilter
    search_fields = ["name", "email", "phone", "company"]
    ordering_fields = ["name", "created_at"]
```

- SimpleJWT:
  - `SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(minutes=5), "ROTATE_REFRESH_TOKENS": True, "BLACKLIST_AFTER_ROTATION": True}`
  - Refresh-токены складываем в Redis blacklist.
- Документация API: `drf-spectacular` (`SPECTACULAR_SETTINGS["SERVE_INCLUDE_SCHEMA"] = False`).

## PostgreSQL

- Docker init: `docker compose exec postgres psql -U postgres -c '\l'`.
- Расширения:
  - `CREATE EXTENSION IF NOT EXISTS citext;`
  - `CREATE EXTENSION IF NOT EXISTS pg_trgm;`
- Бэкап: `pg_dump -h localhost -U postgres crm_db > backup.sql`.
- Индексы: `GIN` по `pg_trgm` для поиска клиентов.

## Celery + Redis

- Запуск: `celery -A config worker -l info`, beat: `celery -A config beat -l info`.
- Паттерн задачи:

```python
@shared_task(bind=True, autoretry_for=(RequestException,), retry_backoff=True, max_retries=3)
def send_deal_notification(self, deal_id: uuid.UUID):
    deal = Deal.objects.get(pk=deal_id)
    send_mail(..., html_message=render_to_string("emails/deal.html", {"deal": deal}))
```

- Redis как брокер (`redis://redis:6379/0`) и как результат-хранилище (`redis://redis:6379/1`).

## HTMX + Django Templates

- Подключение: `<script src="https://unpkg.com/htmx.org@2.0.0"></script>`.
- Базовые атрибуты:
  - `hx-get="/clients/partial/" hx-target="#clients-list" hx-trigger="load, keyup delay:500ms"`.
  - `hx-post="/clients/create/" hx-swap="outerHTML" hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'`.
- Сервер может возвращать:
  - `HX-Redirect` — редирект.
  - `HX-Trigger` — запуск JS-события (`showToast`).

## Tailwind CSS

- Установка: `npm install -D tailwindcss postcss autoprefixer`.
- Конфиг: `npx tailwindcss init --full`.
- Команда сборки: `npx tailwindcss -i ./static/src/tailwind.css -o ./static/css/tailwind.css --watch`.
- Основные utility:
  - Грид: `grid grid-cols-1 gap-4 md:grid-cols-2`.
  - Карточки: `bg-white shadow rounded-lg p-4`.

## Docker / Nginx

- Dev: `docker compose up --build`.
- Prod overlay: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`.
- Лейблы:
  - `backend`: Gunicorn `gunicorn config.wsgi:application -w 4 -b 0.0.0.0:8000`.
  - `frontend`: `gunicorn crm_frontend.wsgi:application -w 3 -b 0.0.0.0:8001`.
- Nginx конфиг (фрагмент):

```
location /api/ {
    proxy_pass http://backend:8000/;
    proxy_set_header Authorization $http_authorization;
    proxy_set_header Host $host;
}
location / {
    proxy_pass http://frontend:8001/;
}
```

## Тестирование и качество

- Backend: `pytest --ds=config.settings.test --reuse-db`.
- Frontend/BFF: `pytest apps/bff/tests`.
- Линтеры: `ruff check .`, `black .`, `isort .`.
- Smoke: `docker compose run --rm backend pytest -m "smoke"`.
- Seed данных: `python manage.py loaddata fixtures/dev_seed.json`.

Используйте файл как быстрый reference при разработке и демонстрации проекта.
