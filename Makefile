#!make

include .env # this will make the .env file variables available to the Makefile

DC=docker compose -f docker-compose.yaml
DC_APP=app
MANAGE=python manage.py
# update this if you change the MACHINE_NAME in scripts/dokku-setup.sh
DOKKU_MACHINE_NAME=dokku-machine
# update this if you change the APP_NAME in scripts/dokku-setup.sh
DOKKU_APP_NAME=myapp
DOKKU_DB_NAME=$(DOKKU_APP_NAME)-db

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
	@echo "clean          Clean up generated files and folders (node_modules, static, media, etc.)"
	@echo "frontend       Build the frontend (npm)"
	@echo "frontend-check Check frontend formatting and linting (npm)"
	@echo "quickstart     Build and start all (npm & docker)"
	@echo "start          Build the front end and start local development server (npm)"
	@echo "make-dokku     Make the dokku machine"
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
	@echo "Pushing data to Dokku"
	@echo "============================================================================"
	@echo "push-dokku-data Push the media to the dokku machine"
	@echo "                run the copy-media.sh script on the dokku machine to copy the media to the dokku app"
	@echo "                and run the following command in the dokku app shell:"
	@echo "                from wagtail.images.models import Rendition; Rendition.objects.all().delete()"
	@echo "                to clear the cached images"
	@echo "export-data     Export the data from the postgres database to a file"
	@echo "import-data     Import the data from the file into the dokku postgres database"
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


# Clean up
# rm -rf ./webapp/static_compiled; \ add when needed
.PHONY: clean
clean:
	@echo "WARNING:"
	@echo "This will destroy all data in the database and remove all generated files and folders (node_modules, static, media)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		make destroy; \
		rm -rf ./node_modules ./static ./media ./db_backups db.sqlite3 webapp/static_compiled .s3cfg bootstrap.sh copy-media.sh; \
		echo "Cleaned up"; \
	else \
		echo "Aborted"; \
	fi

# Make the dokku machine
.PHONY: make-dokku
make-dokku:
	@bash ./scripts/dokku-setup.sh

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
	-@$(DC) exec db sh -c 'pg_restore -U postgres -d webapp /db_backups/latest.dump || true'
	@rm -rf db_backups/latest.dump
	@echo "Data pulled from Heroku database"

# Export the data from the postgres database to a file
.PHONY: export-data
export-data:
	echo "Exporting data from the postgres database"
	@mkdir -p db_backups
	@$(DC) exec db sh -c 'pg_dump -Fc -U postgres -d webapp > /db_backups/backup.dump'

# Import the data from the file into the postgres database
.PHONY: import-data
import-data:
	echo "Importing data into the dokku postgres database"
	orbctl push -m $(DOKKU_MACHINE_NAME) db_backups/backup.dump /root/backup.dump
	orbctl exec -m $(DOKKU_MACHINE_NAME) bash -c 'dokku postgres:import $(DOKKU_DB_NAME) < /root/backup.dump'

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
	@s3cmd --config=$(PWD)/.s3cfg --access_key=$(AWS_ACCESS_KEY_ID) --secret_key=$(AWS_SECRET_ACCESS_KEY) sync s3://$(AWS_STORAGE_BUCKET_NAME)/original_images media
	@$(DC) exec $(DC_APP) $(MANAGE) shell -c "from wagtail.images.models import Rendition; Rendition.objects.all().delete()"
	@echo "Media pulled from S3 bucket"

.PHONY: push-dokku-data
push-dokku-data:
	@echo "Pushing setup to dokku"
	@PWD=$(PWD)
	@touch copy-media.sh
	@echo "#!/bin/bash" > copy-media.sh
	@echo "WORKDIR=$(WORKDIR)" >> copy-media.sh
	@echo "DOKKU_APP_NAME=$(DOKKU_APP_NAME)" >> copy-media.sh
	@echo "cp -r $(WORKDIR)/media/original_images/ /var/lib/dokku/data/storage/$(DOKKU_APP_NAME)/media/" >> copy-media.sh
	@echo "dokku storage:ensure-directory $(DOKKU_APP_NAME) --chown herokuish" >> copy-media.sh
	@orbctl push -m $(DOKKU_MACHINE_NAME) copy-media.sh /root/copy-media.sh
	@orbctl exec -m $(DOKKU_MACHINE_NAME) bash -c 'chmod +x /root/copy-media.sh'
	@echo "========================================================="
	@echo "Now run the following command on the dokku machine:"
	@echo "orbctl run -m $(DOKKU_MACHINE_NAME) -u root bash -c '/root/copy-media.sh'"
	@echo "Enter the dokku machine with: 'dokku enter $(DOKKU_APP_NAME)' and run the following command:"
	@echo "and run: ./manage.py shell"
	@echo "and run: from wagtail.images.models import Rendition; Rendition.objects.all().delete()"
	@echo "========================================================="

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
	@echo "DOKKU_MACHINE_NAME=$(DOKKU_MACHINE_NAME)" >> .env
    @echo "Heroku config vars copied to .env for app: $(APP_NAME)"
endef
