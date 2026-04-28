#!make

-include .env # this will make the .env file variables available to the Makefile when present

DC=docker compose -f docker-compose.yaml
DCP=docker compose -f docker-compose.production.yaml
DC_APP=app
DCP_APP=prod-app
DCP_WAIT_DB=$(DCP) exec prod-db sh -c 'until pg_isready -U postgres; do sleep 1; done'
MANAGE=python manage.py

.PHONY: help
help:
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Docker Compose targets"
	@echo "======================="
	@echo "build          Build the Docker containers"
	@echo "down           Stop and remove the Docker containers"
	@echo "destroy        Stop and remove the Docker containers, networks, and volumes"
	@echo "run            Run the Django development server"
	@echo "up             Start the Docker containers"
	@echo ""
	@echo "Container targets"
	@echo "================="
	@echo "collectstatic  Collect static files"
	@echo "migrate        Run Django migrations"
	@echo "restart        Restart the containers"
	@echo "sh             Execute a command in a running container"
	@echo "superuser      Create a superuser"
	@echo "test           Run tests"
	@echo ""
	@echo "Miscellaneous targets"
	@echo "====================="
	@echo "clean          Clean up generated files and folders (node_modules, static, media, prod_media, etc.)"
	@echo "frontend       Build the frontend (npm)"
	@echo "frontend-check Check frontend formatting and linting (npm)"
	@echo "quickstart     Build and start all (npm & docker)"
	@echo "start          Build the front end and start local development server (npm)"
	@echo ""
	@echo "Production-mode local checks"
	@echo "============================"
	@echo "prod-build         Build production-mode Docker images, including frontend assets"
	@echo "prod-up            Start production-mode Postgres, Gunicorn, and nginx"
	@echo "prod-down          Stop production-mode containers"
	@echo "prod-restart       Restart production-mode containers"
	@echo "prod-migrate       Run migrations with DEBUG=False settings"
	@echo "prod-collectstatic Collect static files with DEBUG=False settings"
	@echo "prod-import-data   Import db_backups/backup.dump into production-mode Postgres"
	@echo "prod-pull-data     Pull Heroku data directly into production-mode Postgres"
	@echo "prod-pull-media    Pull S3 media directly into isolated production-mode media"
	@echo "prod-push-data     Export local dev data and import it into production-mode Postgres"
	@echo "prod-push-media    Copy local media into isolated production-mode media"
	@echo "prod-run           Build and run production mode from source"
	@echo ""
	@echo "Pulling data from Heroku and S3"
	@echo "============================================================================"
	@echo "The commands below require the Heroku CLI and s3cmd to be installed"
	@echo "you can run the 'extract-vars' target to copy the Heroku config vars to .env"
	@echo "----------------------------------------------------------------------------"
	@echo "extract-vars   Copy Heroku config vars to .env"
	@echo "               update the HEROKU_APP_NAME in the .env file before running"
	@echo "pull-data      Pull the data from the Heroku database and import it into the local database"
	@echo "pull-media     Pull the media from the S3 bucket"
	@echo ""
	@echo "Mirroring data to production-mode Docker"
	@echo "============================================================================"
	@echo "export-data      Export the local development Postgres database to a file"
	@echo "prod-pull-data   Pull Heroku data directly into production-mode Postgres"
	@echo "prod-pull-media  Pull S3 media directly into isolated production-mode media"
	@echo "prod-push-data   Export local dev data and import it into production-mode Postgres"
	@echo "prod-push-media  Copy local media into isolated production-mode media"
	@echo ""
	

# Build the containers
.PHONY: build
build:
	@$(DC) build

# Start the containers
.PHONY: up
up:
	@$(DC) up -d

# Stop and remove containers, networks, and volumes
.PHONY: down
down:
	@$(DC) down

# Restart the containers
.PHONY: restart
restart:
	@$(DC) restart

# Execute a command in a running container
.PHONY: sh
sh:
	@$(DC) exec app bash

# Run the Django development server
.PHONY: run
run:
	@$(DC) exec $(DC_APP) $(MANAGE) runserver 0.0.0.0:8000

# Stop and remove the Docker containers, networks, and volumes
.PHONY: destroy
destroy:
	@$(DC) down -v

# Run migrations
.PHONY: migrate
migrate:
	@$(DC) exec $(DC_APP) $(MANAGE) migrate

# Create a superuser
.PHONY: superuser
superuser:
	@$(DC) exec $(DC_APP) $(MANAGE) createsuperuser

# Collect static files
.PHONY: collectstatic
collectstatic:
	@$(DC) exec $(DC_APP) $(MANAGE) collectstatic --noinput

# Run tests, you will need to have run `make collectstatic` first
.PHONY: test
test:
	@$(DC) exec $(DC_APP) $(MANAGE) test

# Quickstart blank project
.PHONY: quickstart
quickstart: frontend build up migrate collectstatic superuser

# Build the frontend
.PHONY: frontend
frontend:
	@npm install
	@npm run build

# Check the frontend
.PHONY: frontend-check
frontend-check:
	@npm install
	@npm run biome:check

# Start the frontend and run the local development server
.PHONY: start
start:
	@npm install
	@npm run build
	@npm run start

.PHONY: prod-prepare
prod-prepare:
	@mkdir -p static prod_media db_backups

.PHONY: prod-build
prod-build: prod-prepare
	@$(DCP) build

.PHONY: prod-up
prod-up: prod-prepare
	@$(DCP) up -d

.PHONY: prod-down
prod-down:
	@$(DCP) down

.PHONY: prod-restart
prod-restart:
	@$(DCP) restart

.PHONY: prod-migrate
prod-migrate: prod-prepare
	@$(DCP) run --rm $(DCP_APP) $(MANAGE) migrate

.PHONY: prod-collectstatic
prod-collectstatic: prod-prepare
	@$(DCP) run --rm $(DCP_APP) $(MANAGE) collectstatic --noinput

.PHONY: prod-import-data
prod-import-data: prod-prepare
	@if [ ! -f db_backups/backup.dump ]; then echo "db_backups/backup.dump is missing. Run make export-data first."; exit 1; fi
	@echo "Importing db_backups/backup.dump into production-mode Postgres"
	@$(DCP) up -d prod-db
	@$(DCP_WAIT_DB)
	-@$(DCP) stop prod-app prod-nginx
	@$(DCP) exec prod-db sh -c 'psql -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '\''webapp'\'' AND pid <> pg_backend_pid();"'
	@$(DCP) exec prod-db sh -c 'psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS webapp;"'
	@$(DCP) exec prod-db sh -c 'psql -U postgres -d postgres -c "CREATE DATABASE webapp;"'
	@$(DCP) exec prod-db sh -c 'pg_restore --no-owner --no-acl -U postgres -d webapp /db_backups/backup.dump'
	@$(DCP) up -d prod-app prod-nginx
	@echo "Production-mode data imported"

.PHONY: prod-pull-data
prod-pull-data: prod-prepare
	@if [ -z "$(HEROKU_APP_NAME)" ]; then echo "HEROKU_APP_NAME is not set"; exit 1; fi
	@echo "Pulling Heroku data directly into production-mode Postgres"
	@rm -f latest.dump db_backups/prod-latest.dump
	@heroku pg:backups:download -a $(HEROKU_APP_NAME)
	@mv latest.dump db_backups/prod-latest.dump
	@$(DCP) up -d prod-db
	@$(DCP_WAIT_DB)
	-@$(DCP) stop prod-app prod-nginx
	@$(DCP) exec prod-db sh -c 'psql -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '\''webapp'\'' AND pid <> pg_backend_pid();"'
	@$(DCP) exec prod-db sh -c 'psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS webapp;"'
	@$(DCP) exec prod-db sh -c 'psql -U postgres -d postgres -c "CREATE DATABASE webapp;"'
	@$(DCP) exec prod-db sh -c 'pg_restore --no-owner --no-acl -U postgres -d webapp /db_backups/prod-latest.dump'
	@rm -f db_backups/prod-latest.dump
	@$(DCP) up -d
	@echo "Heroku data imported into production-mode Postgres"

.PHONY: prod-push-data
prod-push-data: export-data prod-import-data prod-up

.PHONY: prod-push-media
prod-push-media: prod-prepare
	@if [ ! -d media ]; then echo "media directory is missing. Run make pull-media first or add local media."; exit 1; fi
	@echo "Copying local media into isolated production-mode media"
	@mkdir -p prod_media
	@find prod_media -mindepth 1 -exec rm -rf {} +
	@cp -R media/. prod_media/
	@$(DCP) up -d prod-db
	@$(DCP) run --rm $(DCP_APP) $(MANAGE) shell -c "from wagtail.images.models import Rendition; Rendition.objects.all().delete()"
	@echo "Production-mode media copied and renditions cleared"

.PHONY: prod-pull-media
prod-pull-media: prod-prepare
	@if [ -z "$(HEROKU_APP_NAME)" ]; then echo "HEROKU_APP_NAME is not set"; exit 1; fi
	@$(eval S3CFG=$(PWD)/.s3cfg)
	$(call heroku_to_env,$(HEROKU_APP_NAME))
	@echo "Pulling S3 media directly into isolated production-mode media"
	@rm -rf prod_media
	@mkdir -p prod_media/original_images
	@touch .s3cfg
	@echo "[default]" >> .s3cfg
	@AWS_ACCESS_KEY_ID=$$(grep '^AWS_ACCESS_KEY_ID=' .env | cut -d= -f2-); \
	AWS_SECRET_ACCESS_KEY=$$(grep '^AWS_SECRET_ACCESS_KEY=' .env | cut -d= -f2-); \
	AWS_STORAGE_BUCKET_NAME=$$(grep '^AWS_STORAGE_BUCKET_NAME=' .env | cut -d= -f2-); \
	s3cmd --config=$(PWD)/.s3cfg --access_key=$$AWS_ACCESS_KEY_ID --secret_key=$$AWS_SECRET_ACCESS_KEY sync s3://$$AWS_STORAGE_BUCKET_NAME/original_images prod_media
	@$(DCP) up -d prod-db
	@$(DCP) run --rm $(DCP_APP) $(MANAGE) shell -c "from wagtail.images.models import Rendition; Rendition.objects.all().delete()"
	@echo "S3 media pulled into production-mode media and renditions cleared"

.PHONY: prod-run
prod-run: prod-build prod-migrate prod-collectstatic prod-up
	@echo "Production-mode site running at https://prod-nginx.nickmoreton-production.orb.local"
	@echo "Localhost fallback available at http://localhost:$${PROD_PORT:-8001}"


# Clean up
# rm -rf ./webapp/static_compiled; \ add when needed
.PHONY: clean
clean:
	@echo "WARNING:"
	@echo "This will destroy all data in the database and remove all generated files and folders (node_modules, static, media, prod_media)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		make destroy; \
		rm -rf ./node_modules ./static ./media ./prod_media ./db_backups db.sqlite3 webapp/static_compiled .s3cfg bootstrap.sh copy-media.sh; \
		echo "Cleaned up"; \
	else \
		echo "Aborted"; \
	fi

# Pull the data using the Heroku CLI and import it into the local database
.PHONY: pull-data
pull-data:
	@if [ -z "$(HEROKU_APP_NAME)" ]; then echo "HEROKU_APP_NAME is not set"; exit 1; fi
	@echo "Pulling data from Heroku database"
	@mkdir -p db_backups
	@heroku pg:backups:download -a $(HEROKU_APP_NAME)
	@mv latest.dump db_backups/latest.dump
	@$(DC) exec db sh -c 'psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS webapp;"'
	@$(DC) exec db sh -c 'psql -U postgres -d postgres -c "CREATE DATABASE webapp;"'
	@$(DC) exec db sh -c 'pg_restore --no-owner --no-acl -U postgres -d webapp /db_backups/latest.dump'
	@rm -rf db_backups/latest.dump
	@echo "Data pulled from Heroku database"

# Export the data from the postgres database to a file
.PHONY: export-data
export-data:
	echo "Exporting data from the postgres database"
	@mkdir -p db_backups
	@$(DC) exec db sh -c 'pg_dump -Fc -U postgres -d webapp > /db_backups/backup.dump'

# Pull the media from the S3 bucket
# Not sure why but if you have .s3cfg in your home directory it will use that for the s3cmd command keys etc.
# So you need to remove it at the moment
.PHONY: pull-media
pull-media:
	@if [ -z "$(HEROKU_APP_NAME)" ]; then echo "HEROKU_APP_NAME is not set"; exit 1; fi
	@$(eval S3CFG=$(PWD)/.s3cfg)
	$(call heroku_to_env,$(HEROKU_APP_NAME))
	@echo "Pulling media from S3 bucket"
	@rm -rf media
	@mkdir -p media/original_images
	@touch .s3cfg
	@echo "[default]" >> .s3cfg
	@AWS_ACCESS_KEY_ID=$$(grep '^AWS_ACCESS_KEY_ID=' .env | cut -d= -f2-); \
	AWS_SECRET_ACCESS_KEY=$$(grep '^AWS_SECRET_ACCESS_KEY=' .env | cut -d= -f2-); \
	AWS_STORAGE_BUCKET_NAME=$$(grep '^AWS_STORAGE_BUCKET_NAME=' .env | cut -d= -f2-); \
	s3cmd --config=$(PWD)/.s3cfg --access_key=$$AWS_ACCESS_KEY_ID --secret_key=$$AWS_SECRET_ACCESS_KEY sync s3://$$AWS_STORAGE_BUCKET_NAME/original_images media
	@$(DC) exec $(DC_APP) $(MANAGE) shell -c "from wagtail.images.models import Rendition; Rendition.objects.all().delete()"
	@echo "Media pulled from S3 bucket"

# Copy heroku config vars to .env
# required to run the pull-data and pull-media targets
# update the HEROKU_APP_NAME in the .env file before running
.PHONY: extract-vars
extract-vars:
	@if [ -z "$(HEROKU_APP_NAME)" ]; then echo "HEROKU_APP_NAME is not set"; exit 1; fi
	$(call heroku_to_env,$(HEROKU_APP_NAME))

# Function to copy Heroku config vars to .env
define heroku_to_env
    $(eval HEROKU_VARS=$(shell heroku config -a $(1) -s))
    $(eval APP_NAME=$(1))
    @> .env
    @echo "HEROKU_APP_NAME=$(APP_NAME)" >> .env
    @for var in $(HEROKU_VARS); do \
        echo "$$var" >> .env; \
	    done
	@echo "WORKDIR=$(PWD)" >> .env
    @echo "Heroku config vars copied to .env for app: $(APP_NAME)"
endef
