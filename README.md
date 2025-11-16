# CRM BFF Portfolio Project

Пет-проект CRM-системы с архитектурой Back-for-Front (BFF). Репозиторий предназначен для демонстрации подхода, поэтому делает упор на документацию, читаемый код и понятные сценарии запуска.

## Стек

- Backend: Django + DRF + PostgreSQL + Celery + Redis.
- Frontend/BFF: Django Templates + HTMX + Tailwind + Redis cache.
- Инфраструктура: Docker Compose, Gunicorn, Nginx.
- Инструменты качества: pytest, pre-commit, Sentry/structured logging (по желанию).

## Роли и зоны ответственности

| Роль / участник         | Зона ответственности                                                                                   | Артефакты/директории                                                    |
|-------------------------|--------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| Тимлид (Codex)          | Архитектурное видение, планирование, методички, ревью решений.                                         | `plan.md`, `README.md`, `docs/`                                         |
| Backend-разработчик     | Реализация `crm_backend`: модели, DRF API, Celery, миграции, интеграция с Postgres/Redis.              | будущая папка `crm_backend/`, docker-compose, тесты backend             |
| Frontend/BFF-разработчик| Django templates, HTMX, Tailwind, BFF-сервисы, интеграция с backend API через DTO/клиент.             | `crm_frontend/` (особенно `services/`), UI-компоненты, BFF-кэш          |
| DevOps/Infra            | Docker/Nginx, CI/CD, переменные окружения, мониторинг/алертинг.                                        | `docker-compose*.yml`, `.env.example`, CI workflows                     |

Таблица помогает быстро понять, к кому относится конкретный раздел и кому адресовать вопросы.

## Структура (в разработке)

```
drf_project/
├─ docs/                     # дополнительные инструкции
├─ crm_frontend/
│  └─ services/
│     ├─ dto.py              # DTO-схемы для BFF
│     └─ backend_api.py      # HTTP-клиент для доступа к backend
├─ plan.md                   # детальный план работ/архитектуры
├─ README.md                 # этот файл
└─ main.py                   # временные заглушки (если нужны)
```

## Быстрый старт (dev-режим)

1. Установите зависимости (Python 3.12+, Docker, Make/NPM при необходимости).
2. Скопируйте переменные окружения:
   ```powershell
   Copy-Item .env.example .env
   ```
   *(файл появится после инициализации backend/frontend приложений)*.
3. Запустите инфраструктуру:
   ```bash
   docker compose up --build
   ```
4. Создайте суперпользователя в backend и администратора в frontend:
   ```bash
   docker compose run --rm backend python manage.py createsuperuser
   docker compose run --rm frontend python manage.py createsuperuser
   ```
5. Откройте `http://localhost:8000` (frontend) и `http://localhost:8000/api/` (backend через nginx proxy).

## Частые команды

| Цель                      | Команда                                                                 |
|---------------------------|-------------------------------------------------------------------------|
| Применить миграции        | `docker compose run --rm backend python manage.py migrate`             |
| Выполнить тесты backend   | `docker compose run --rm backend pytest`                               |
| Выполнить тесты frontend  | `docker compose run --rm frontend pytest`                              |
| Собрать Tailwind          | `docker compose run --rm frontend npm run build:css`                   |
| Запустить celery worker   | `docker compose up celery celery-beat`                                 |
| Очистить BFF-кэш          | `docker compose run --rm frontend python manage.py bff_refresh_cache`  |

## Документация

- Архитектура и план: [`plan.md`](plan.md)
- Интеграция BFF ↔ backend: [`docs/bff-integration.md`](docs/bff-integration.md)
- Шпаргалка по стеку: [`docs/tech-cheatsheet.md`](docs/tech-cheatsheet.md)

## Дальнейшие шаги

- Реализовать Django-проекты `crm_backend` и `crm_frontend`.
- Добавить CI (GitHub Actions) и линтеры (`ruff`, `black`, `isort`).
- Подключить централизованный мониторинг (Sentry, Prometheus).

README обновляйте по мере развития репозитория, добавляя команды, скрипты и подсказки.
