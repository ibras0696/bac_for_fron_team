COMPOSE ?= docker compose

.PHONY: up down logs build backend-shell frontend-shell migrate backend-test frontend-test

# Start entire stack in dev mode (rebuild images)
up:
	$(COMPOSE) up --build

# Stop stack and remove containers
down:
	$(COMPOSE) down

# Tail all service logs
logs:
	$(COMPOSE) logs -f

# Build/rebuild images without starting them
build:
	$(COMPOSE) build

# Open Django shell inside backend container
backend-shell:
	$(COMPOSE) run --rm backend python manage.py shell

# Open Django shell inside frontend container
frontend-shell:
	$(COMPOSE) run --rm frontend python manage.py shell

# Run migrations for backend and frontend
migrate:
	$(COMPOSE) run --rm backend python manage.py migrate
	$(COMPOSE) run --rm frontend python manage.py migrate

# Execute backend test suite
backend-test:
	$(COMPOSE) run --rm backend pytest

# Execute frontend/BFF test suite
frontend-test:
	$(COMPOSE) run --rm frontend pytest
