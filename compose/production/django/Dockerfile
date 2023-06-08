FROM node:18-bullseye-slim as client-builder

ARG APP_HOME=/app
WORKDIR ${APP_HOME}
COPY ./package.json ${APP_HOME}
RUN npm install && npm cache clean --force
COPY . ${APP_HOME}
RUN npm run build


FROM python:3.11.3-slim-bullseye

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

ARG BUILD_ENVIRONMENT=production
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

ENV PATH="/root/.local/bin:${PATH}" \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install --no-install-recommends -y \
  curl libpq-dev build-essential gettext \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

ARG POETRY_VERSION
ENV POETRY_VERSION="${POETRY_VERSION:-1.4.2}"
RUN curl -sSL https://install.python-poetry.org \
  | python - --version "${POETRY_VERSION}" \
  && poetry --version

COPY poetry.lock pyproject.toml .
RUN poetry install --no-root

COPY . ${APP_HOME}

RUN poetry install


COPY --from=client-builder  ${APP_HOME} ${APP_HOME}
