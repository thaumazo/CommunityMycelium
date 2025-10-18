# Makefile for managing Django project on cPanel (no containers)

DB_USER=$(shell grep DATABASE_URL mycelium/.env | sed -E 's|.*//([^:]+):.*|\1|')
DB_PASS=$(shell grep DATABASE_URL mycelium/.env | sed -E 's|.*//[^:]+:([^@]+)@.*|\1|')
DB_HOST=$(shell grep DATABASE_URL mycelium/.env | sed -E 's|.*@([^:/]+):.*|\1|')
DB_NAME=$(shell grep DATABASE_URL mycelium/.env | sed -E 's|.*/([^?]+).*|\1|')

clean:
	rm -rf ../public_html/static/*
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc"  -delete
	find . -name "*.pyc" -delete
	echo "SET FOREIGN_KEY_CHECKS = 0;" > drop_tables.sql
	echo "SET FOREIGN_KEY_CHECKS = 1;" >> drop_tables.sql
	mysql -u $(DB_USER) -p$(DB_PASS) -h $(DB_HOST) $(DB_NAME) < drop_tables.sql
	rm drop_tables.sql

migrate:
	python mycelium/manage.py makemigrations users
	python mycelium/manage.py makemigrations
	python mycelium/manage.py migrate

createsuperuser:
	python mycelium/manage.py createsuperuser

shell:
	python mycelium/manage.py shell

collectstatic:
	python mycelium/manage.py collectstatic --noinput

setup-groups:
	python mycelium/manage.py setup_admin_roles
	python mycelium/manage.py setup_user_roles
	python mycelium/manage.py setup_meeting_roles
	python mycelium/manage.py setup_task_roles

seed-users:
	python mycelium/manage.py seed_users

seed-meetings:
	python mycelium/manage.py seed_meetings

seed-tasks:
	python mycelium/manage.py seed_tasks

seed-all:
	python mycelium/manage.py print_seed_order | while read cmd; do \
		echo "Running $$cmd..."; \
	done

scratch: clean migrate setup-groups seed-all

local:
	python mycelium/manage.py runserver

.PHONY: clean migrate createsuperuser shell collectstatic setup-groups seed-users seed-meetings seed-tasks seed-all scratch local
