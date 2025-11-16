COMPOSE ?= docker compose

.PHONY: up down logs build backend-shell frontend-shell migrate backend-test frontend-test

# Start entire stack in dev mode (rebuild images) / Запустить dev-стек (с пересборкой)
up:
	$(COMPOSE) up --build

# Stop stack and remove containers / Остановить и удалить контейнеры
down:
	$(COMPOSE) down

# Tail all service logs / Смотреть логи всех сервисов
logs:
	$(COMPOSE) logs -f

# Build/rebuild images without starting them / Пересобрать образы без запуска
build:
	$(COMPOSE) build

# Open Django shell inside backend container / Открыть Django shell backend
backend-shell:
	$(COMPOSE) run --rm backend python manage.py shell

# Open Django shell inside frontend container / Открыть Django shell frontend
frontend-shell:
	$(COMPOSE) run --rm frontend python manage.py shell

# Run migrations for backend and frontend / Применить миграции обоих сервисов
migrate:
	$(COMPOSE) run --rm backend python manage.py migrate
	$(COMPOSE) run --rm frontend python manage.py migrate

# Execute backend test suite / Запустить тесты backend
backend-test:
	$(COMPOSE) run --rm backend pytest

# Execute frontend/BFF test suite / Запустить тесты frontend/BFF
frontend-test:
	$(COMPOSE) run --rm frontend pytest
