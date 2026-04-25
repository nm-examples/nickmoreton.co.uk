# Local Development with Dokku on OrbStack 🛠️

This guide helps you create a production-like environment locally using OrbStack and Dokku.

⚠️ **Note**: This is for development/testing purposes, not permanent deployment. For production, see our [Linode deployment guide](./linode.dokku.md).

## Key Features
- 🔄 Heroku-compatible buildpacks
- 💾 Local storage system
- 🗄️ PostgreSQL database
- 🔒 HTTPS with local domain
- 🚀 Git-push deployments

## Prerequisites
- [OrbStack](https://orbstack.dev/) installed

## Create A Machine

```bash
orbctl create --arch amd64 --user root debian:bookworm dokku-machine
# wget is required for the dokku install
orbctl run -m dokku-machine -u root bash -c "apt install wget htop -y"
```

### Install Dokku

You could run the commands inside the machine console, logged in as root. That should translate to running the same commands below but omitting `orbctl run -m dokku-machine -u root bash -c`.

```bash
# Make sure the latest version is used
orbctl run -m dokku-machine -u root bash -c "wget -NP . https://dokku.com/install/v0.35.16/bootstrap.sh && sudo DOKKU_TAG=v0.35.16 bash bootstrap.sh"
```

### Configure Global Domain

This should match the machine Domain name in OrbStack.

```bash
orbctl run -m dokku-machine -u root bash -c "dokku domains:set-global dokku-machine.orb.local"
# -----> Set dokku-machine.orb.local
```

### SSH Key

```bash
orbctl run -m dokku-machine -u root bash -c "echo 'your-ssh-key' | dokku ssh-keys:add admin"
# SHA256:j3xU+dszYsIv...
```

### Install Postgres

```bash
orbctl run -m dokku-machine -u root bash -c "dokku plugin:install https://github.com/dokku/dokku-postgres.git"
# Takes a little while to install
# -----> Priming bash-completion cache
```

## Create A New App

```bash
orbctl run -m dokku-machine -u root bash -c "dokku apps:create myapp"
# -----> Creating myapp...
# -----> Creating new app virtual host file...

orbctl run -m dokku-machine -u root bash -c "dokku postgres:create myapp-db"
# =====> Postgres container created: myapp-db

orbctl run -m dokku-machine -u root bash -c "dokku postgres:link myapp-db myapp"
# -----> Restarting app myapp
# !     App image (dokku/myapp:latest) not found

# Domains might need checking here and corrected at the end
orbctl run -m dokku-machine -u root bash -c "dokku domains:report myapp"
# =====> myapp domains information
# ...

orbctl run -m dokku-machine -u root bash -c "dokku buildpacks:add myapp https://github.com/heroku/heroku-buildpack-nodejs.git"
orbctl run -m dokku-machine -u root bash -c "dokku buildpacks:add myapp https://github.com/heroku/heroku-buildpack-python.git"
# No feedback seen here

orbctl run -m dokku-machine -u root bash -c "dokku config:set myapp DJANGO_SECRET_KEY=supersecretkey --no-restart"
orbctl run -m dokku-machine -u root bash -c "dokku config:set myapp DJANGO_ALLOWED_HOSTS=myapp.dokku-machine.orb.local --no-restart"
orbctl run -m dokku-machine -u root bash -c "dokku config:set myapp DJANGO_CSRF_TRUSTED_ORIGINS=https://myapp.dokku-machine.orb.local --no-restart"
# -----> Setting config vars
# ...

orbctl run -m dokku-machine -u root bash -c "dokku storage:ensure-directory myapp --chown herokuish"
# -----> Ensuring /var/lib/dokku/data/storage/myapp exists

orbctl run -m dokku-machine -u root bash -c "dokku storage:mount myapp /var/lib/dokku/data/storage/myapp/media:/app/media"
# No feedback seen here optionally check with
orbctl run -m dokku-machine -u root bash -c "dokku storage:report myapp"

orbctl run -m dokku-machine -u root bash -c "mkdir -p /home/dokku/myapp/nginx.conf.d"
orbctl run -m dokku-machine -u root bash -c "cat <<EOF > /home/dokku/myapp/nginx.conf.d/media.conf
location /media {
    alias /var/lib/dokku/data/storage/myapp/media;
}
EOF"
# No feedback seen here optionally check with
orbctl run -m dokku-machine -u root bash -c "ls /home/dokku/myapp/nginx.conf.d"
# media.conf
orbctl run -m dokku-machine -u root bash -c "cat /home/dokku/myapp/nginx.conf.d/media.conf"
# location /media {
#    alias /var/lib/dokku/data/storage/myapp/media;
#}

# Set the upload size limit
orbctl run -m dokku-machine -u root bash -c "dokku nginx:set myapp client-max-body-size 10m"
# =====> Setting client-max-body-size to 10m

# Make any other corrections here

# Restart the app for all settings to take effect
# But this may not have any effect until the app is deployed
orbctl run -m dokku-machine -u root bash -c "dokku ps:restart myapp"
# After the app is deployed the restart will happen automatically
```

## Deploying to Dokku

From the root of the project:

```bash
# only required once
git remote add dokku dokku@dokku-machine@orb:myapp
git remote -v # to check (optional)

# On the first deployment the app should be restarted so will capture any of the above changes
git push dokku main
# =====> Application deployed:
#        http://myapp.dokku-machine.orb.local
# and optional command to deploy could be
git push dokku current_branch_name:main

# now you will need to set an admin user login
orbctl run -m dokku-machine -u root bash -c "dokku enter myapp"
# Inside the container
./manage.py createsuperuser
# If need be other commands could be run here
# Exit the container
```

## Accessing the App
You should be able to access the app at `https://myapp.dokku-machine.orb.local` and the admin at `https://myapp.dokku-machine.orb.local/admin`.

## Troubleshooting

### Images and documents cannot be uploaded

This is likely due to the permissions of the storage directory. You can check the permissions with:

```bash
orbctl run -m dokku-machine -u root bash -c "ls -l /var/lib/dokku/data/storage/myapp"
# drwxr-xr-x 1 root  root   0 Apr  2 17:08 media
# The media directory should be owned by the user `32767` and group `32767`

# If required you can change the permissions with:
orbctl run -m dokku-machine -u root bash -c "dokku storage:ensure-directory myapp --chown herokuish"
# -----> Ensuring /var/lib/dokku/data/storage/myapp exists
#        Setting directory ownership to 32767:32767
#        Directory ready for mounting

orbctl run -m dokku-machine -u root bash -c "ls -l /var/lib/dokku/data/storage/myapp"
# drwxr-xr-x 1 32767 32767  0 Apr  2 17:08 media
```

And try uploading again.

## Quick Setup Script 🚀

Save time with our automated setup script:

[dokku-setup.sh](./files/dokku-setup.sh) Don't forget to modify the SSH key in the script before running it.

```bash
# Ensure to modify ssh-key in the script first
bash ./docs/files/dokku-setup.sh
```

## Getting data and media files into the Dokku app

There's a few ways to do this, but the easiest is to use the provided Makefile commands.

### Copy development data

```bash
# Copy the development data into the dokku app
make export-data
make import-data
```
This will copy the data from the local development environment into the dokku app.

The `export-data` command will create a dump of the database to `db_backups`. The `import-data` command will copy the dump into the dokku machine and import it into the database.

### Copy media files

```bash
# Copy the media files into the dokku app
make push-dokku-data
```
This will create a script `copy-media.sh` which is pushed over to the dokku machine.

You then need to run the script on the dokku machine to copy the files over.

```bash
# Run the script on the dokku machine
./copy-media.sh
```
This will copy the media files from the local development environment into the dokku app.

If your images are not showing up, you may need to delete renditions using the Django shell

In a console on the dokku machine, run:

```bash
./manage.py shell
```

Then run the following commands:

```python
from wagtail.images.models import Rendition; Rendition.objects.all().delete()
```
This will delete all renditions and force Wagtail to regenerate them when the images are accessed again.
