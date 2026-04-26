#!/bin/bash

SSH_KEY=$(cat ~/.ssh/id_ed25519.pub) # add path to a *.pub key file here
MACHINE_NAME="dokku-machine"
APP_NAME="myapp"
DOKKU_VERSION="v0.35.16"

orbctl create --arch amd64 --user root debian:bookworm $MACHINE_NAME
orbctl run -m $MACHINE_NAME -u root bash -c "apt install wget htop -y"
orbctl run -m $MACHINE_NAME -u root bash -c "wget -NP . https://dokku.com/install/$DOKKU_VERSION/bootstrap.sh && sudo DOKKU_TAG=$DOKKU_VERSION bash bootstrap.sh"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku domains:set-global $MACHINE_NAME.orb.local"
orbctl run -m $MACHINE_NAME -u root bash -c "echo $SSH_KEY | dokku ssh-keys:add admin"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku plugin:install https://github.com/dokku/dokku-postgres.git"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku apps:create $APP_NAME"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku postgres:create $APP_NAME-db"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku postgres:link $APP_NAME-db $APP_NAME"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku domains:report $APP_NAME"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku buildpacks:add $APP_NAME https://github.com/heroku/heroku-buildpack-nodejs.git"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku buildpacks:add $APP_NAME https://github.com/heroku/heroku-buildpack-python.git"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku config:set $APP_NAME DJANGO_SECRET_KEY=supersecretkey --no-restart"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku config:set $APP_NAME DJANGO_ALLOWED_HOSTS=$APP_NAME.$MACHINE_NAME.orb.local --no-restart"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku config:set $APP_NAME DJANGO_CSRF_TRUSTED_ORIGINS=https://$APP_NAME.$MACHINE_NAME.orb.local --no-restart"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku config:set $APP_NAME WAGTAIL_UNVEIL_API_KEY=local-dokku-key --no-restart"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku config:set $APP_NAME WAGTAIL_UNVEIL_ENABLE_PRODUCTION_REPORTS=true --no-restart"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku config:set $APP_NAME WAGTAIL_UNVEIL_SKIP_URL_PREFIXES=django-admin,__reload__ --no-restart"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku storage:ensure-directory $APP_NAME --chown herokuish"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku storage:mount $APP_NAME /var/lib/dokku/data/storage/$APP_NAME/media:/app/media"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku storage:report $APP_NAME"
orbctl run -m $MACHINE_NAME -u root bash -c "mkdir -p /home/dokku/$APP_NAME/nginx.conf.d"
orbctl run -m $MACHINE_NAME -u root bash -c "cat <<EOF > /home/dokku/$APP_NAME/nginx.conf.d/media.conf
location /media {
    alias /var/lib/dokku/data/storage/$APP_NAME/media;
}
EOF"
orbctl run -m $MACHINE_NAME -u root bash -c "ls /home/dokku/$APP_NAME/nginx.conf.d"
orbctl run -m $MACHINE_NAME -u root bash -c "cat /home/dokku/$APP_NAME/nginx.conf.d/media.conf"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku nginx:set $APP_NAME client-max-body-size 10m"
orbctl run -m $MACHINE_NAME -u root bash -c "dokku ps:restart $APP_NAME"
