# Local Dokku Staging with OrbStack

This guide helps you create a local staging environment using OrbStack and Dokku for production-like verification before deployment.

**Note:** This is for staging/testing deployment behavior, not day-to-day local development or permanent deployment.

The default local machine name is `dokku-machine`. The default local app name is `myapp`. These names match the Makefile defaults and `scripts/dokku-setup.sh`; update both places if you change them.

## Happy Path

1. Install OrbStack.
2. Create the `dokku-machine` OrbStack machine.
3. Install Dokku, Postgres, and your SSH key.
4. Create the `myapp` app and `myapp-db` database.
5. Configure buildpacks, environment variables, persistent media storage, and nginx media serving.
6. Add the `dokku` git remote.
7. Deploy `main` with `git push dokku main`, or deploy a feature branch with `git push dokku <current-branch>:main`.
8. Create a Wagtail superuser and optionally copy local data/media using the [data and media workflow](./data-and-media.md).

Most of the machine and app setup is wrapped by:

```bash
make make-dokku
```

Run it from the project root after copying `.env.example` to `.env`.

## Key Features
- Heroku-compatible buildpacks
- Local storage system
- PostgreSQL database
- HTTPS with local domain
- Git-push deployments

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
orbctl run -m dokku-machine -u root bash -c "dokku config:set myapp WAGTAIL_UNVEIL_API_KEY=local-dokku-key --no-restart"
orbctl run -m dokku-machine -u root bash -c "dokku config:set myapp WAGTAIL_UNVEIL_ENABLE_PRODUCTION_REPORTS=true --no-restart"
orbctl run -m dokku-machine -u root bash -c "dokku config:set myapp WAGTAIL_UNVEIL_SKIP_URL_PREFIXES=django-admin,__reload__ --no-restart"
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
The local setup serves the app over HTTP unless you add HTTPS separately:

- Site: `http://myapp.dokku-machine.orb.local`
- Admin: `http://myapp.dokku-machine.orb.local/admin`

Verify the deployment with:

```bash
curl -I -L http://myapp.dokku-machine.orb.local
orbctl run -m dokku-machine -u root bash -c "dokku ps:report myapp"
```

If running commands from a sandboxed tool such as Codex, OrbStack and Docker socket commands may need elevated host access. A plain terminal session should not need anything extra.

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

## Quick Setup Script

Save time with our automated setup script:

[dokku-setup.sh](../scripts/dokku-setup.sh) Don't forget to modify the SSH key in the script before running it.

```bash
# Ensure to modify ssh-key in the script first
bash ./scripts/dokku-setup.sh
```

## Getting data and media files into the Dokku app

Use the provided Makefile commands to export local Docker data, import it into local Dokku, and copy local media files. See [Data and media workflows](./data-and-media.md) for the full guide and cleanup notes.

## Troubleshooting Checklist

- If a deploy fails during build, confirm the buildpack order is Node.js first, then Python.
- If static files are missing, rebuild frontend assets and confirm the deploy ran `collectstatic`.
- If media uploads fail, check that the mounted media directory is owned by `32767:32767`.
- If the site returns host or CSRF errors, check `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS`.
