include .envs/local/.django
include .envs/local/.postgres
export

.PHONY: django webpack celery migrate load-envs unload-envs services

django:
	poetry run python manage.py runserver 0.0.0.0:8000

run-tests:
	poetry run pytest

webpack:
	npm run dev

celery:
	poetry run celery -A config.celery_app worker --loglevel=info

migrate:
	poetry run python manage.py migrate

services:
	docker-compose up -d mailhog mq opensearch celerybeat redis db

load-demo-data:
	poetry run python manage.py loaddata local

shell:
	poetry run python manage.py shell

flush:
	poetry run python manage.py flush

make-migrations:
	poetry run python manage.py makemigrations

migrate:
	poetry run python manage.py migrate
