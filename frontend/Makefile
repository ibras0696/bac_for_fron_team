PYTHON ?= python
MANAGE ?= $(PYTHON) manage.py
NPM ?= npm

.PHONY: install dev lint test runserver tailwind

# Install python (and optional npm) dependencies / Установить python (и npm) зависимости
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	if [ -f package.json ]; then $(NPM) install; fi

# Run Django dev server (aliases: runserver/dev) / Запустить dev-сервер
runserver dev:
	$(MANAGE) runserver 0.0.0.0:8001

# Build Tailwind assets in watch mode / Собрать Tailwind (watch)
tailwind:
	$(NPM) run dev:css

# Run linters for BFF code / Прогнать линтеры
lint:
	ruff check .
	black --check .

# Run pytest suite for BFF / Запустить pytest
test:
	pytest
