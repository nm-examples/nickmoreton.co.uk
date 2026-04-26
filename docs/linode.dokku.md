# Production Deployment with Dokku on Linode

Set up a production environment using Linode (Akamai Cloud) and Dokku. Need a local testing environment instead? Check our [local setup guide](./local.dokku.md).

## Server Requirements
- Ubuntu 22.04 LTS
- 1 CPU / 1 GB RAM minimum
- 25 GB SSD storage
➡️ [Get started with Linode](https://www.linode.com/lp/refer/?r=2973f4e51059904e42c0dc36b66be18e54f25282)

## Features
- Automatic SSL with Let's Encrypt
- Managed PostgreSQL
- Persistent storage
- Git-push deployments

## Install Dokku

https://dokku.com/docs/getting-started/installation/

- Update and upgrade the server
- Install `wget` and `htop`

```bash
wget -NP . https://dokku.com/install/[DOKKU_VERSION]/bootstrap.sh
DOKKU_TAG=[DOKKU_VERSION] bash bootstrap.sh
```

### Setup SSH Keys

```bash
# Add the public key to the server
ssh-copy-id -i ~/.ssh/[key-file].pub root@[server-ip]
# Add the public key to dokku
# usually your key is already available under the current user's `~/.ssh/authorized_keys` file
cat ~/.ssh/authorized_keys | dokku ssh-keys:add admin
```

### Setup Domain

```bash
# you can use any domain you already have access to
# this domain should have an A record or CNAME pointing at your server's IP
dokku domains:set-global [domain-name]
```

### Install PostgreSQL

https://github.com/dokku/dokku-postgres

```bash
# on the Dokku host
# install the postgres plugin
# plugin installation requires root, hence the user change
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git
```

### Install Let's Encrypt

https://github.com/dokku/dokku-letsencrypt

```bash
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
sudo dokku letsencrypt:cron-job --add # <- To enable auto-renew
```

## Create a New App and Link it to a PostgreSQL Database

```bash
dokku apps:create nickmoreton-staging
dokku postgres:create nickmoreton-staging
dokku postgres:link nickmoreton-staging nickmoreton-staging
```

## Set Up the App's Environment Variables

```bash
dokku config:set nickmoreton-staging DJANGO_SECRET_KEY=supersecretkey --no-restart
dokku config:set nickmoreton-staging DJANGO_ALLOWED_HOSTS=the-domain-in-use --no-restart
dokku config:set nickmoreton-staging DJANGO_CSRF_TRUSTED_ORIGINS=https://the-domain-in-use --no-restart
```

## Ensure the App Storage Directory Exists

```bash
# The permissions are set to 32767:32767
dokku storage:ensure-directory nickmoreton-staging --chown herokuish
# Sometimes the above command fails, so run this to ensure the directory exists
# and is owned by the correct user

# Mount the app's storage directory
dokku storage:mount nickmoreton-staging /var/lib/dokku/data/storage/nickmoreton-staging/media:/app/media
```

## Set Up the Herokuish Buildpacks

No docker file in production... the order matters, node first, then python

```bash
dokku buildpacks:clear nickmoreton-staging
dokku buildpacks:add nickmoreton-staging https://github.com/heroku/heroku-buildpack-nodejs.git
dokku buildpacks:add nickmoreton-staging https://github.com/heroku/heroku-buildpack-python.git
```

## Set the Ports for the App

By default it gets set to http:8000:8000 

```bash
dokku ports:add or set nickmoreton-staging https:80:8000
# example output
# dokku ports:report nickmoreton-staging
# =====> nickmoreton-staging ports information
#        Ports map:                     http:80:8000 https:443:8000
#        Ports map detected:            http:80:5000 https:443:5000
```

## Add an Nginx Config File for the App's Media Files

```bash
mkdir -p /home/dokku/nickmoreton-staging/nginx.conf.d
```

Add a file with the following content to the directory:

```bash
cat <<EOL > /home/dokku/nickmoreton-staging/nginx.conf.d/media.conf
location /media {
    alias /var/lib/dokku/data/storage/nickmoreton-staging/media;
}
```

Run the following command to set the nginx config:

```bash
dokku ps:restart nickmoreton-staging
service nginx reload
```

Adjust the nginx config for uploads:

```bash
dokku nginx:set nickmoreton-staging client-max-body-size 10m
dokku proxy:build-config nickmoreton-staging # for settings to take effect
```

## Set Up the Let's Encrypt Certificate

```bash
dokku letsencrypt:enable nickmoreton-staging
dokku letsencrypt:cron-job --add
dokku letsencrypt:list # to check the status
```

## Deployment Checklist

1. [ ] Server created and accessible
2. [ ] Domain DNS configured
3. [ ] SSL certificates installed
4. [ ] Database created and linked
5. [ ] Environment variables set
6. [ ] Storage mounted
7. [ ] First deployment completed

## Make a Deployment

Git is used to deploy the app to the server. 

### Add a Git Remote

```bash
git remote add dokku dokku@[server-ip-or-domain]:nickmoreton-staging
```

### Deploy to Staging

```bash
git push dokku [local-branch]:main
```

The deploy process will run the following:

- Build the frontend and backend
- Run the migrations
- Collect the static files
- Restart the app
- Restart the nginx server

It should be working after this and a domain link should be shown.

## Data and Media

Use the focused [data and media workflow](./data-and-media.md) for Heroku-backed local imports, local database exports, and media copy helpers. Treat production data and media commands as intentional local operations and do not commit generated dumps or copied secrets.
