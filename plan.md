# План CRM Back-for-Front

Документ описывает CRM-проект для портфолио с паттерном Back-for-Front (BFF). Цель: показать зрелую архитектуру, пригодную для демонстрации на собеседованиях, без фанатичного масштабирования.

---

## 1. Контекст и цели

- Роли: фронтенд-разработчик (HTMX + Django Templates), бекенд-разработчик (DRF), тимлид (контроль архитектуры).
- Стек: Django, DRF, PostgreSQL, Redis, Celery, HTMX, Tailwind, Docker, Nginx.
- Ценности: предсказуемость, понятные контракты, простая эксплуатация.

---

## 2. BFF-архитектура

### 2.1 Backend (`crm_backend`)

| Компонент            | Детали                                                                                  |
|----------------------|-----------------------------------------------------------------------------------------|
| Django + DRF         | ViewSet + Router, django-filter, drf-spectacular (OpenAPI/Swagger).                     |
| Auth                 | SimpleJWT (5 мин access, 1 день refresh) с ротацией и blacklist в Redis/Postgres.       |
| База данных          | PostgreSQL (extensions: `citext`, `pg_trgm`).                                           |
| Асинхронка           | Celery + Redis: еmail-уведомления, напоминания, nightly digest метрик.                  |
| Логирование/метрики  | structured logging, Sentry (или аналог), health-check `/healthz`.                       |
| CI                   | pytest + coverage, pre-commit (black, isort, flake8, mypy optional).                    |

### 2.2 Frontend/BFF (`crm_frontend`)

- Django + SQLite (хранит только локальные таблицы BFF: пользователи, привязки токенов, кэшированные ответы).
- Templates + HTMX + Tailwind (JIT). Нет полного SPA.
- Основные обязанности:
  1. Авторизация пользователей и маппинг на backend JWT (refresh хранится в Redis, access — в signed cookie).
  2. Агрегация данных: BFF формирует удобные JSON/HTML для UI, обращаясь к backend по HTTP (через слой сервисов, а не напрямую из view).
  3. Кэширование быстрых данных (Redis или локальный SQLite cache) и graceful degradation при недоступности backend.
  4. Политики ошибок: user-friendly сообщения, логирование причин и alert тимлиду.

### 2.3 Инфраструктура

- Docker Compose (dev): `backend`, `frontend`, `postgres`, `redis`, `celery`, `celery-beat`, `nginx`.
- Nginx:
  - `/api/` → backend (Gunicorn + DRF).
  - `/` → frontend (Gunicorn + Django templates).
- Prod compose overlay (`docker-compose.prod.yml`): разведение секретов, build-стадий, autoheal.

---

## 3. Доменная модель

| Модель       | Поля / заметки                                                                                               |
|--------------|--------------------------------------------------------------------------------------------------------------|
| User         | email (unique, citext), full_name, role (`ADMIN`, `USER`), is_active, timestamps.                            |
| Client       | name, phone, email, company, notes, owner (FK User), timestamps.                                             |
| Deal         | client, title, amount (Decimal), status (`NEW`, `IN_PROGRESS`, `WON`, `LOST`), owner, description, expected_close_date. |
| Task         | client, deal (nullable), title, description, due_date, status (`TODO`, `IN_PROGRESS`, `DONE`), assigned_to, created/completed. |
| ActivityLog  | user, entity_type (`client`, `deal`, `task`), entity_uuid, action, payload JSON, created_at.                  |
| DashboardCache | snapshot JSON, `valid_until`, `type` (например `pipeline`, `stats`).                                        |

Расширения для портфолио: импорты CSV, вложения к задачам (S3/minio), webhooks.

---

## 4. API-уровень backend

1. `/api/v1/auth/login|refresh|logout`.
2. `/api/v1/clients/` — поиск, фильтры по owner, пагинация `limit/offset`.
3. `/api/v1/deals/` — фильтры status, client, owner, amount range.
4. `/api/v1/tasks/` — фильтры status, assignee, overdue flag.
5. `/api/v1/stats/overview/` — метрики (ответ кэшируется Celery-таском).
6. `/api/v1/activity/` — лента с пагинацией, фильтрами `entity_type`, `user_id`.
7. `/api/v1/files/` (по желанию) — загрузка вложений с presigned URL.

### BFF endpoints

| Endpoint (frontend)            | Что делает                                                                                           |
|--------------------------------|-------------------------------------------------------------------------------------------------------|
| `GET /login/` / `POST /login/` | Форма логина, hit backend `/auth/login/`, сохраняет refresh → Redis, access → cookie.                |
| `GET /dashboard/`              | Параллельно собирает `/stats/overview/`, `/deals/?status=IN_PROGRESS`, `/activity/?limit=5`.         |
| `GET /clients/`                | Берёт `search` query → backend, отдаёт partial list (HTMX).                                          |
| `POST /clients/`               | Отправляет форму → backend, обрабатывает ошибки валидации.                                           |
| `GET /deals/board/`            | Сервис BFF агрегирует сделки по статусу, отдаёт структуру для Kanban.                               |
| `GET /tasks/calendar/`         | Преобразует список задач в dataset для календаря.                                                    |
| `GET /activity/stream/`        | Server-Sent Events из Redis pub/sub (опционально).                                                  |

---

## 5. Узкие места и меры

| Риск                                     | Митигирующая мера                                                                                         |
|------------------------------------------|------------------------------------------------------------------------------------------------------------|
| Дублирование бизнес-логики в BFF         | Создать слой сервисов `backend_api.py` + pydantic-схемы; unit-тесты контрактов.                           |
| Потеря синхронизации auth                | BFF не хранит пароли, использует backend как IdP; refresh-токены лежат в Redis, logout инвалидирует их.  |
| Тайм-ауты/нестабильный backend           | Retry с backoff (3 попытки), graceful fallback (readonly стейты, заглушки данных).                        |
| ActivityLog без связей                   | Используем UUID и дублируем важные поля в payload, плюс task, deal names; cron чистит orphans.            |
| Отсутствие тестов                        | Pytest + factory_boy + coverage в CI, smoke `docker compose run backend pytest`.                         |
| Нет наблюдаемости                        | Структурные логи, Sentry, health-checkи, `/metrics` (Prometheus) при желании.                            |

---

## 6. План работ (3 итерации по ~2 недели)

### Итерация 1 — Сквозной CRUD минимум

- backend: проект Django, Postgres, SimpleJWT, Users, Clients, Deals CRUD, фильтры, docker-compose dev.
- frontend/BFF: базовое приложение, layout, логин/logout, список клиентов (HTMX), общий API-клиент.
- DevOps: README с запуском, pre-commit, CI skeleton (GitHub Actions).

### Итерация 2 — Продвинутая функциональность

- backend: Tasks, ActivityLog, Stats endpoint, Celery + Redis, email-уведомления, swagger.
- frontend: доска сделок, задачи, Activity feed partials, shared components (search, pagination).
- Observability: Sentry, health-check, structured logging.

### Итерация 3 — Полировка и портфолио-фичи

- backend: role-based permissions, attachments/webhooks, отчетности (CSV export), dashboard cache job.
- frontend: dashboard агрегатор, SSE notifications, UX polishing (loading states, toasts).
- Deploy: docker-compose prod, nginx конфиг, база переменных `.env.example`, make-команды.

---

## 7. Требования к качеству

1. **Документация:** README, диаграммы, cheat sheets (см. `docs/`), описанные контракты.
2. **Тестирование:** 80%+ покрытие ключевых сервисов, smoke-тесты HTMX view, контрактные тесты BFF ↔ backend.
3. **Безопасность:** HTTPS (self-signed для dev), CSP-заголовки, rate limiting DRF (ScopedRateThrottle), CSRF для форм HTMX.
4. **Данные:** миграции управляются `manage.py migrate`, фикстуры `initial_data.json`, фабрики для dev-наполнения.

---

## 8. Backlog идей

- Импорт/экспорт клиентов (CSV/Excel).
- Система напоминаний в Telegram/Slack (webhook).
- Kanban drag-n-drop (HTMX + SortableJS).
- А/B демо скрипты (recorded demo).
- Модуль отчетов (PDF через WeasyPrint).

---

## 9. Контакты и ссылочные материалы

- Архитектурные диаграммы: `docs/bff-integration.md`.
- Cheatsheet по стеку: `docs/tech-cheatsheet.md`.
- Основные команды: `README.md` (создать после реализации).

Документ поддерживается тимлидом. Обновлять после каждого крупного изменения API/архитектуры.
