# Infrastructure Overview

Этот документ фиксирует базовую инфраструктуру для CRM BFF проекта.

## Контейнеры

- `backend` — Django + DRF (порт 8000).
- `frontend` — Django Templates + HTMX (порт 8001).
- `postgres` — БД (volume `pg_data`).
- `redis` — брокер/кэш.
- `celery`, `celery-beat` — фоновые задачи.
- `nginx` — reverse proxy, проксирует `/api/` на backend, остальное на frontend.

## Docker Compose

- `docker-compose.yml` — dev-режим (runserver, hot reload, volume-монтаж).
- `docker-compose.prod.yml` — prod-режим (Gunicorn, disable volumes, требует `.env.prod`).
- Основные переменные хранятся в `.env`, backend/frontend используют собственные `.env`.

## Nginx

Конфиг в `infra/nginx/default.conf`; для прод-режима добавьте TLS (certbot или mkcert).

## Makefile

- Корневой `Makefile` даёт команды `up`, `down`, `logs`, `backend-test` и т.д.
- Внутри `backend/Makefile` и `frontend/Makefile` размещены команды разработки.

## TODO

- Добавить CI/CD pipeline (GitHub Actions).
- Описать TLS и секреты для продакшена.
- При необходимости вынести инфраструктуру в отдельный `infra` проект или Helm chart.

Используйте этот файл как шпаргалку при работе с инфраструктурой.
