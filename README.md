# Homepagerr - A Simple, Self-Hosted Dashboard

[![Docker Image CI](https://github.com/christiandavies79/homepagerr/actions/workflows/docker-build.yml/badge.svg)](https://github.com/christiandavies79/homepagerr/actions/workflows/docker-build.yml)
[![Docker Hub](https://img.shields.io/docker/pulls/dpooper79/homepagerr.svg?style=flat-square)](https://hub.docker.com/r/dpooper79/homepagerr)

A clean, lightweight, and easy-to-use personal homepage application, designed to be run as a Docker container. Perfect for a home server dashboard on platforms like Unraid.

## Features

- **Link Organization**: Arrange your favorite links into customizable sections.
- **In-Browser Editing**: No need to edit config files directly. Click "Edit Links" to add, remove, and re-order links and sections on the fly.
- **Drag & Drop**: Simply drag a URL from another browser tab and drop it onto the page to quickly add a new link.
- **Customization**: Use the Settings modal to change the page title and set whether links open in a new tab.
- **Persistent Storage**: All of your links and settings are stored in a Docker volume, so they persist through container updates and restarts.
- **Scratchpad for quick note taking when you have nowhere else to drop something quickly or you want to be able to easily move it between devices.

## Running with Docker

This application is designed to be run as a Docker container.

**1. Pull the image from Docker Hub:**
```bash
docker pull dpooper79/homepagerr:latest
```

**2. Run the container:**
You must map a local directory to the container's `/app/config` path. This is where your `links.json` and `settings.json` files will be stored.

```bash
docker run -d \
  --name=homepagerr \
  -p 8000:8000 \
  -v /path/on/your/host:/app/config \
  --restart unless-stopped \
  dpooper79/homepagerr:latest
```

Replace `/path/on/your/host` with the actual path where you want to store your configuration (e.g., `/mnt/user/appdata/homepagerr`).

**3. Access the application:**
Once running, you can access your new homepage at `http://<your-server-ip>:8000`.

## Configuration

### Volume Mapping
- `/app/config`: This is the only directory that needs to be persisted. It contains:
    - `/data/links.json`: Your list of sections and links.
    - `/data/settings.json`: Your application settings.
    - `/static/*`: The front-end files (`index.html`, `style.css`, `scripts.js`).

### Overwriting Static Files
On the first run, the container will create default static files (HTML, CSS, JS). If you want to force the container to overwrite these with the defaults from a newer image on a subsequent run, you can do so from the UI:
1. Go to **Settings**.
2. Check the box **"Force overwrite static files on next restart"**.
3. Save settings and restart the container.

This is useful for applying front-end updates without losing your link data.

## Development & CI

This repository uses GitHub Actions to automate the building and publishing of Docker images to [Docker Hub](https://hub.docker.com/r/dpooper79/homepagerr).

- **`main` branch**: A push to `main` triggers a build that is tagged as `:latest` and `:sha-<commit_hash>`.
- **Other branches**: A push to any other branch (e.g., `test`) triggers a build that is tagged as `:test` and `:sha-<commit_hash>`.
