# syntax=docker/dockerfile:1.6

# Base python image for backend / Базовый Python-образ для backend
FROM python:3.12-slim AS base

# Avoid pyc files, enable unbuffered output, and keep pip lean / Без pyc, вывод без буфера и быстрый pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

# Install system deps (build-essential, libpq for psycopg2) / Ставим системные зависимости (build-essential, libpq)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies / Устанавливаем python-зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files / Копируем код проекта
COPY . .

# Default command (overridden in dev compose) / Команда по умолчанию (в dev переопределяется)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
