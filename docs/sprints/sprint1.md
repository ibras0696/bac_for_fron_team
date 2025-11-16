# Спринт 1 — Сквозной CRUD минимум

Продолжительность: 2 недели. Цель — получить работающий «скелет» системы с базовыми сущностями и первым UX.

## Цели

- Настроить окружение и инфраструктуру (Docker Compose, Postgres, Redis).
- Реализовать базовый backend API для клиентов и сделок.
- Поднять каркас фронтенда/BFF, реализовать авторизацию и список клиентов.

## Задачи по ролям

### Backend

1. Инициализация Django-проекта `crm_backend`.
2. Настройка Postgres, `settings/base|dev`.
3. Модели `User`, `Client`, `Deal` + миграции.
4. Серилизаторы и ViewSet'ы в DRF, фильтры и пагинация.
5. Аутентификация через SimpleJWT.
6. Dockerfile + docker-compose сервис `backend`.

### Frontend/BFF

1. Инициализация Django-проекта `crm_frontend`.
2. Базовый layout (Navbar, контейнер, flash-сообщения).
3. Авторизация (форма логина, вызов `/auth/login/`, сохранение токенов).
4. Список клиентов с поиском (HTMX partial).
5. Dockerfile + docker-compose сервис `frontend`.

### DevOps / Общее

1. Общий `docker-compose.yml` (backend, frontend, postgres, redis, nginx).
2. Настройка nginx маршрутов `/` и `/api/`.
3. README с инструкциями запуска.
4. Базовые фикстуры/seed-скрипт для тестовых пользователей.

## Definition of Done

- `docker compose up` поднимает всю инфраструктуру.
- Можно залогиниться в BFF и увидеть список клиентов (данные из backend).
- Тесты/линтеры backend проходят (`pytest`, `ruff`), фронтенд smoke-тесты выполняются.
- Документация обновлена (plan.md, README, sprint notes).
