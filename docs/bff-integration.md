# BFF ↔ Backend Integration Guide

Документ объясняет, как frontend-приложение (`crm_frontend`) взаимодействует с backend API (`crm_backend`) в паттерне Back-for-Front.

---

## 1. Auth flow

1. Пользователь открывает `GET /login/` (frontend).
2. Форма `POST /login/` отправляется во фронтовый view `LoginView`.
3. `LoginView` вызывает сервис `auth_service.login(email, password)`:
   - делает `POST {BACKEND_URL}/api/v1/auth/login/` (SimpleJWT),
   - при успехе получает `access`, `refresh`, `user` payload.
4. Сервис сохраняет:
   - refresh-токен в Redis (`refresh:{user_uuid}`) с TTL, помечает device fingerprint;
   - access-токен в Django signed-cookie (`bff_access`), httpOnly, secure.
5. Django session хранит только ссылку на backend user id + настройки UI.
6. Logout:
   - фронт удаляет cookie,
   - вызывает backend `/auth/logout/` (blacklist refresh),
   - чистит запись из Redis.

Access обновляется с помощью фоновой задачи:

```python
def refresh_access(user):
    refresh = redis.get(f"refresh:{user.backend_id}")
    response = requests.post(f"{BACKEND_URL}/api/v1/auth/refresh/", data={"refresh": refresh})
    set_access_cookie(response["access"])
```

---

## 2. Слой API-клиента

`crm_frontend/services/backend_api.py` — единая точка работы с REST.

- Используем `httpx` (async) или `requests` (sync) с таймаутом 5 секунд.
- Настройки:
  - `BASE_URL`
  - дефолтные заголовки (`Authorization`, `X-Request-ID`).
- Повторные попытки: до 3, экспоненциальный backoff (0.2, 0.5, 1.0с).
- Методы возвращают pydantic-модели, а не raw JSON.

Пример:

```python
class ClientListResponse(BaseModel):
    results: list[ClientSchema]
    count: int


def fetch_clients(token: str, params: dict[str, Any]) -> ClientListResponse:
    response = http.get("/clients/", headers={"Authorization": f"Bearer {token}"}, params=params)
    return ClientListResponse.model_validate_json(response.text)
```

---

## 3. BFF сервисы и HTMX views

1. HTMX view (`clients_list`) вызывает сервис `clients_service.list(search, request.user)`.
2. Сервис:
   - получает access-токен через `token_provider.get_access(request.user)`;
   - вызывает backend `fetch_clients`;
   - пишет результат в кэш (`cache.set(f"clients:{hash_params}", data, 30)`).
3. View рендерит partial `clients/_list.html`.
4. HTMX отвечает только фрагментом DOM, а глобальная верстка остаётся на Django template.

Ошибка backend → сервис выбрасывает `BackendUnavailable`, middleware конвертирует в дружелюбное сообщение и логирует инцидент.

---

## 4. Dashboard агрегатор

`GET /dashboard/` выполняет параллельные запросы.

```python
async def build_dashboard(user):
    token = token_provider.get_access(user)
    stats, deals, activity = await asyncio.gather(
        api.fetch_stats(token),
        api.fetch_deals(token, {"status": "IN_PROGRESS", "limit": 10}),
        api.fetch_activity(token, {"limit": 5}),
    )
    return DashboardDTO.from_sources(stats, deals, activity)
```

- Используем `asyncio` + `httpx.AsyncClient`.
- Ответ хранится в `DashboardCache` на 60 секунд для каждого пользователя.

---

## 5. Error handling

| Сценарий                                      | Поведение                                                                                              |
|-----------------------------------------------|---------------------------------------------------------------------------------------------------------|
| 401/403 от backend                            | Авто-logout и редирект на `/login/` с сообщением.                                                      |
| 5xx/timeout                                    | Показываем алерт «API временно недоступно», логируем, возвращаем кэш/placeholder.                      |
| Валидация 400                                 | Отображаем ошибки в форме HTMX (partial с inline errors).                                              |
| Rate limit 429                                | Дожидаемся retry-after, показываем подсказку.                                                          |

События записываются в `ActivityLog` BFF (`bff_activity` таблица) + Sentry.

---

## 6. Observability

- Каждый запрос к backend получает `X-Request-ID` (UUID), прокидываем в Nginx и DRF.
- Логи:
  - Frontend: `logger.info("Fetch clients", extra={"request_id": req_id, "user": request.user.id})`.
  - Backend: DRF loggers + `logging.Filter` с тем же `request_id`.
- Метрики (опционально):
  - Prometheus metrics endpoint `/metrics`.
  - Celery task durations.

---

## 7. Быстрые команды

| Цель                    | Команда                                                                                 |
|-------------------------|-----------------------------------------------------------------------------------------|
| Dev запуск              | `docker compose up --build`                                                             |
| Backend shell           | `docker compose run --rm backend python manage.py shell_plus`                           |
| Frontend tests          | `docker compose run --rm frontend pytest`                                               |
| Пересоздать кэш        | `docker compose run --rm frontend python manage.py clearsessions && python manage.py bff_refresh_cache` |

Используйте гайд при разработке и презентации архитектуры.
