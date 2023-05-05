include .envs/local/.django
include .envs/local/.postgres
export

.PHONY: django webpack celery migrate load-envs unload-envs services

django:
	poetry run python manage.py runserver 0.0.0.0:8000

tests:
	poetry run pytest

webpack:
	npm run dev

celery:
	poetry run celery -A config.celery_app worker --loglevel=info

migrate:
	poetry run python manage.py migrate

services:
	docker-compose up -d mailhog mq opensearch celerybeat redis db
