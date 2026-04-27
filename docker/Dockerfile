FROM node:24-bookworm AS frontend

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY scripts/images.js ./scripts/images.js
COPY webapp/static_src ./webapp/static_src
RUN npm run build

FROM python:3.13-bookworm AS base

RUN useradd --create-home --shell /bin/bash wagtail

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/.venv \
    PORT=8000

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

RUN chown wagtail:wagtail /app

# Install dependencies.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

ENV PATH="/opt/.venv/bin:$PATH"

COPY --chown=wagtail:wagtail . .
COPY --from=frontend --chown=wagtail:wagtail /app/webapp/static_compiled ./webapp/static_compiled

USER wagtail

# RUN python manage.py collectstatic --noinput --clear

# FROM base AS development

# CMD tail -f /dev/null
