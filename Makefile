# Makefile for initializing and managing Django project with Podman (no podman-compose)

PROJECT_NAME = mycelium
POD_NAME = $(PROJECT_NAME)-pod

# --- Project Bootstrap Commands ---
init:
	mkdir -p apps/users apps/orgs apps/tasks
	echo "DEBUG=True\nSECRET_KEY=supersecretkey\nALLOWED_HOSTS=*\nDATABASE_URL=postgres://postgres:postgres@$(PROJECT_NAME)-db:5432/$(PROJECT_NAME)" > .env

	@if ! podman pod exists $(POD_NAME); then \
		echo "Creating pod $(POD_NAME)..."; \
		podman pod create --name $(POD_NAME) -p 8000:8000 -p 5432:5432; \
	else \
		echo "Pod $(POD_NAME) already exists."; \
	fi
	@if ! podman container exists $(PROJECT_NAME)-db; then \
		echo "Starting DB container..."; \
		podman run -d --name $(PROJECT_NAME)-db --pod $(POD_NAME) -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=$(PROJECT_NAME) -v pgdata:/var/lib/postgresql/data postgres:15; \
	else \
		echo "Database container already exists."; \
	fi

# Build and run Django container in the pod
up:
	@if ! podman container exists $(PROJECT_NAME)-db; then \
		echo "Starting DB container..."; \
		podman run -d --name $(PROJECT_NAME)-db --pod $(POD_NAME) -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=$(PROJECT_NAME) -v pgdata:/var/lib/postgresql/data postgres:15; \
	else \
		echo "Database container already running."; \
	fi

	@if podman container exists $(PROJECT_NAME)-web; then \
		echo "Removing old web container..."; \
		podman rm -f $(PROJECT_NAME)-web; \
	fi

	podman build -t $(PROJECT_NAME)-web .
	podman run -dt --name $(PROJECT_NAME)-web --pod $(POD_NAME) -v .:/app --env-file .env $(PROJECT_NAME)-web


stop:
	podman stop $(PROJECT_NAME)-web $(PROJECT_NAME)-db

rm:
	podman rm $(PROJECT_NAME)-web $(PROJECT_NAME)-db

rmpod:
	podman pod rm $(POD_NAME)

clean: stop rm rmpod
	podman volume rm pgdata

# Django management
migrate:
	podman exec $(PROJECT_NAME)-web python manage.py makemigrations users
	podman exec $(PROJECT_NAME)-web python manage.py makemigrations
	podman exec $(PROJECT_NAME)-web python manage.py migrate

createsuperuser:
	podman exec -it $(PROJECT_NAME)-web python manage.py createsuperuser

shell:
	podman exec -it $(PROJECT_NAME)-web python manage.py shell

pytest:
	podman exec $(PROJECT_NAME)-web pytest

test: pytest

.PHONY: init up stop rm rmpod clean migrate createsuperuser shell pytest test
