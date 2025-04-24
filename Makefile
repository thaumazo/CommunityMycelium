# Makefile for initializing and managing Django project with Podman (no podman-compose)

POD_NAME = mycelium

# --- Project Bootstrap Commands ---
init:
	@if ! podman pod exists $(POD_NAME); then \
		echo "Creating pod $(POD_NAME)..."; \
		podman pod create --name $(POD_NAME) -p 8000:8000 -p 5432:5432; \
	else \
		echo "Pod $(POD_NAME) already exists."; \
	fi

	@if ! podman container exists $(POD_NAME)-db; then \
		echo "Starting DB container..."; \
		podman run -d --name $(POD_NAME)-db --pod $(POD_NAME) \
			-e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=$(POD_NAME) \
			-v pgdata:/var/lib/postgresql/data postgres:15; \
	else \
		echo "Database container already exists."; \
	fi

# Build and run Django container in the pod
up:
	@if ! podman container exists $(POD_NAME)-db; then \
		echo "Starting DB container..."; \
		podman run -d --name $(POD_NAME)-db --pod $(POD_NAME) \
			-e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=$(POD_NAME) \
			-v pgdata:/var/lib/postgresql/data postgres:15; \
	else \
		echo "Database container already running."; \
	fi

	@if podman container exists $(POD_NAME)-web; then \
		echo "Removing old web container..."; \
		podman rm -f $(POD_NAME)-web; \
	fi

	podman build -t $(POD_NAME)-web .
	podman run -dt --name $(POD_NAME)-web --pod $(POD_NAME) -v ./app:/app --env-file app/.env $(POD_NAME)-web

stop:
	podman stop $(POD_NAME)-web $(POD_NAME)-db || true

rm:
	podman rm $(POD_NAME)-web $(POD_NAME)-db || true

rmpod:
	podman pod rm $(POD_NAME) || true

clean: stop rm rmpod
	podman volume rm pgdata || true

scratch: clean init up migrate

# Django management
migrate:
	podman exec $(POD_NAME)-web python manage.py makemigrations users
	podman exec $(POD_NAME)-web python manage.py makemigrations
	podman exec $(POD_NAME)-web python manage.py migrate

createsuperuser:
	podman exec -it $(POD_NAME)-web python manage.py createsuperuser

shell:
	podman exec -it $(POD_NAME)-web python manage.py shell

ssh:
	podman exec -ti $(POD_NAME)-web /bin/bash

pytest:
	podman exec $(POD_NAME)-web pytest

test: pytest

.PHONY: init up stop rm rmpod clean migrate createsuperuser shell pytest test setup-groups
