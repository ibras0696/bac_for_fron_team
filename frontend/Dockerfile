# syntax=docker/dockerfile:1.6

# Base image for frontend BFF
FROM python:3.12-slim AS base

# Speed up Python startup, disable bytecode
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

# Install system deps (add node if Tailwind build required later)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Project files
COPY . .

# Serve via Gunicorn in prod (compose dev overrides command)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8001"]
