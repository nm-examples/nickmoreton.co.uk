# Nick Moreton's Wagtail-Powered Website 🚀

[![Wagtail](https://img.shields.io/badge/wagtail-7.3.1-olive.svg)](https://wagtail.org/)
[![Django](https://img.shields.io/badge/django-6.0.4-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

Welcome to the source code of [www.nickmoreton.co.uk](https://www.nickmoreton.co.uk) - a modern, Django-based website showcasing:
- ⚡ Lightning-fast performance with Wagtail CMS
- 🎨 Modern frontend architecture
- 🚀 Production-ready deployment options
- 📱 Responsive design throughout

> Special thanks to [Torchbox](https://torchbox.com) for providing my production hosting on the Heroku platform. 🙏

## Setup for development

Copy the `.env.example` file to `.env`.

```bash
cp .env.example .env
```

Update the `.env` file with the correct value for your Heroku app name.

```bash
 HEROKU_APP_NAME=add-the-app-name
 ```

### Running the development environment (quick start)

```bash
make quickstart
```

- The quickstart will perform an initial build of the frontend assets.
- You will be prompted for the admin username and password.

```bash
make run
```

View the site at <http://localhost:8000>

### Running the development environment (step by step)

Copy the `.env.example` file to `.env`.

```bash
cp .env.example .env
```

Update the `.env` file with the correct value for your Heroku app name.

```bash
 HEROKU_APP_NAME=add-the-app-name
 ```

First build and run should include the following commands:

```
make build
make up
make migrate
make run
```

Then you can run the following command to start the development environment:

```bash
make run
```

View the site at <http://localhost:8000> (frontend files may be missing, see below)

Create a superuser

```bash
make superuser
```

View the admin at <http://localhost:8000/admin>

Django-browser-reload will automatically reload the page in the browser when files are changed, see below for reloading the frontend and seeing the changes in the browser.

## Developer setup (frontend)

### Install the dependencies

```bash
nvm use
npm install
```

### Build the frontend

```bash
npm run build
```

### Build & watch the frontend

The wagtail app should be running in the background. 

```bash
npm start
```

Django-browser-reload will automatically reload the page in the browser when the frontend files are updated.

## Import data and media (from production)

The Heroku env vars are required to be set in the `.env` file for any make commands here.

```bash
make extract-vars
```

### Import the database

```bash
make pull-data
```

### Import the media

```bash
make pull-media
```

## Deployment Options 🌍

### Local Production-like Environment
Test your site in a production-like setup using:
- [OrbStack](https://orbstack.dev/) for containerization
- [Dokku](https://dokku.com) for PaaS functionality
➡️ [Local Dokku Setup Guide](./docs/local.dokku.md)

### Production Deployment
> Did I mention the company I work for, [Torchbox](https://torchbox.com), provide the production hosting for my website on the Heroku platform. 🙏

Deploy to actual production using:
- [Linode](https://www.linode.com/) (Akamai Cloud) for hosting
- [Dokku](https://dokku.com/) for deployment management
➡️ [Production Setup Guide](./docs/linode.dokku.md)
