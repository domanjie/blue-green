🚀 Blue-Green Deployment with Nginx & Docker

This project implements a Blue-Green Deployment architecture using Nginx and Docker Compose to achieve seamless, zero-downtime application updates.

🧩 Overview

Blue-Green Deployment is a release strategy that maintains two identical environments:

Blue – the currently active (production) version

Green – the standby version ready to replace Blue

Traffic is routed through Nginx, which proxies requests to the active pool defined by the environment variable ACTIVE_POOL.
A lightweight health-check script monitors the active pool and automatically switches to the backup if the current one becomes unhealthy — ensuring continuous availability.

⚙️ How It Works

Nginx starts with ACTIVE_POOL (either blue or green).

The script switch.sh periodically checks a health endpoint (e.g., /healthz).

On failure, it regenerates Nginx’s config using envsubst, validates it, and reloads Nginx to switch traffic to the healthy pool.

The switch happens automatically, with no downtime and no 500 errors visible to users.

🧠 Key Components
File	Description
docker-compose.yml	Defines Nginx, Blue, and Green services
nginx.conf.template	Nginx config template with ${ACTIVE_POOL} placeholder
switch.sh	Automatic failover script handling health checks and Nginx reloads
▶️ Run the Project
docker-compose up --build


By default, Nginx routes traffic to the Blue environment.
If Blue becomes unhealthy, it automatically switches to Green.

✅ Features

Zero-downtime deployment

Automatic health checks and failover

Config reload without restarting containers

Simple, production-ready implementation
