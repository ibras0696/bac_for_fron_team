# Инфраструктура: Prod-окружение

Рекомендации по подготовке продакшен-среды для CRM BFF.

---

## 1. Архитектура

- Разделённые сервера/контейнеры для `crm_backend`, `crm_frontend`, `postgres`, `redis`, `celery`, `nginx`.
- Используем `docker-compose.prod.yml` или Helm chart (при необходимости Kubernetes).
- Nginx/Traefik выступает обратным прокси с TLS (Let's Encrypt / self-managed).
- Secrets хранятся в `.env.prod` или secret manager (Vault, AWS SSM).

---

## 2. Переменные окружения (пример `.env.prod`)

```
DJANGO_SETTINGS_MODULE=config.settings.prod
POSTGRES_DB=crm_prod
POSTGRES_USER=crm_prod
POSTGRES_PASSWORD=super-secret
POSTGRES_HOST=postgres
REDIS_URL=redis://redis:6379/0
BACKEND_API_URL=https://crm.example.com/api/v1
FRONTEND_URL=https://crm.example.com
DJANGO_SECRET_KEY=<generate>
ALLOWED_HOSTS=crm.example.com
SENTRY_DSN=<dsn>
```

Frontend/BFF может использовать отдельный `.env.prod` (например, ключи Tailwind, настройки кэшей).

---

## 3. Docker Compose prod

`docker-compose.prod.yml` расширяет dev-конфиг:

- Gunicorn вместо runserver (`gunicorn config.wsgi:application -w 4 -b 0.0.0.0:8000`).
- Static/Media volume для backend и frontend (общий или S3).
- Nginx с TLS (используйте `certbot` или `mkcert`).
- Healthcheck'и для каждого сервиса.
- Autoheal/Restart policy `always`.

Команда деплоя:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## 4. База данных и резервное копирование

- Postgres размещается на отдельном volume или управляемом сервисе (RDS).
- Настроить регулярные бэкапы (`pg_dump` + cron или облачный snapshot).
- Репликация/standby — опционально для портфолио, но можно описать в документации.

---

## 5. Логи и мониторинг

- Логи всех сервисов отправляются в централизованный агрегатор (ELK, Loki, CloudWatch).
- Sentry подключён к backend и frontend.
- Prometheus + Grafana (или аналог) для системных метрик.
- Алерты по ключевым показателям (ошибки 5xx, задержки Celery).

---

## 6. CI/CD

- GitHub Actions:
  - линтеры/тесты для backend и frontend,
  - сборка Docker-образов и push в Registry,
  - деплой на сервер (ssh/rsync или GitHub Deployments).
- Pre-commit на всех разработчиков.
- Секреты CI хранятся в GitHub Secrets.

---

## 7. Обновление и откат

- Версионируйте образ (`crm-frontend:1.0.0`, `crm-backend:1.0.0`).
- Катите обновления через Blue/Green или Rolling (по необходимости).
- Храните миграции и seed-команды (например, `python manage.py migrate && python manage.py seed_prod`).
- Для отката держите предыдущий compose файл и бэкапы базы.

---

## 8. Безопасность

- Только HTTPS, HSTS.
- Ограниченный доступ к админке (IP whitelist, Basic Auth).
- Регулярные обновления зависимостей (Dependabot/ Renovate).
- Настроить rate limiting (Nginx + DRF throttle).

---

Документ служит шпаргалкой при описании прод-настройки и может быть расширен после появления реальной инфраструктуры.
