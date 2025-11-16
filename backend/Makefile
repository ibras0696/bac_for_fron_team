PYTHON ?= python
MANAGE ?= $(PYTHON) manage.py

.PHONY: install migrate runserver shell test lint createsuperuser

# Install python requirements locally / Установить зависимости локально
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

# Apply database migrations / Применить миграции
migrate:
	$(MANAGE) migrate

# Run Django dev server (used outside Docker) / Запустить dev-сервер
runserver:
	$(MANAGE) runserver 0.0.0.0:8000

# Open Django shell (prefers shell_plus if available) / Открыть shell (shell_plus при наличии)
shell:
	$(MANAGE) shell_plus || $(MANAGE) shell

# Run backend pytest suite / Запустить pytest
test:
	pytest

# Run linters (ruff + black) / Проверить линтами
lint:
	ruff check .
	black --check .

# Create admin user interactively / Создать суперпользователя
createsuperuser:
	$(MANAGE) createsuperuser
