PYTHON ?= python
MANAGE ?= $(PYTHON) manage.py

.PHONY: install migrate runserver shell test lint createsuperuser

# Install python requirements locally
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

# Apply database migrations
migrate:
	$(MANAGE) migrate

# Run Django dev server (used outside Docker)
runserver:
	$(MANAGE) runserver 0.0.0.0:8000

# Open Django shell (prefers shell_plus if available)
shell:
	$(MANAGE) shell_plus || $(MANAGE) shell

# Run backend pytest suite
test:
	pytest

# Run linters (ruff + black)
lint:
	ruff check .
	black --check .

# Create admin user interactively
createsuperuser:
	$(MANAGE) createsuperuser
