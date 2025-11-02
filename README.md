# 🚀 Blue-Green Deployment with Nginx, Docker & Slack Monitoring

This project implements a **Blue-Green Deployment architecture** using **Nginx**, **Docker Compose**, and a **Python-based monitoring service** that integrates with Slack for **real-time alerts** and **failover detection** — enabling **zero-downtime deployments** with minimal complexity.
---

## 🧩 Overview

Blue-Green Deployment maintains two identical environments:

* 🟦 **Blue** – the currently active (production) version
* 🟩 **Green** – the standby version ready to replace Blue

Traffic routing and health fallback are handled **entirely within Nginx**, using upstream definitions with backup servers and automatic failover.

A **Python watcher** monitors Nginx access logs, detects pool changes and high error rates, and pushes detailed, styled alerts to **Slack**.

---

## ⚙️ How It Works

1. **Nginx** starts using the pool defined by the environment variable `ACTIVE_POOL` (`blue` or `green`).
2. Requests are routed through an **upstream block** that defines:

   * The active pool server(s)
   * A backup pool for automatic fallback on failure
3. **Failover happens natively** inside Nginx, with no external switch script.
4. **`watcher.py`** continuously tails Nginx access logs:

   * Detects failovers by comparing `pool=` values
   * Monitors error rates using `upstream_status`
   * Sends **color-coded Slack alerts** for failover, recovery, or high error rate events

---

## 🧠 Key Components

| File                  | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `docker-compose.yml`  | Defines Nginx, Blue, Green, and Watcher containers       |
| `nginx.conf.template` | Nginx config template with `${ACTIVE_POOL}` placeholders |
| `watcher.py`          | Log-watching and Slack alerting script                   |
| `runbook.md`          | Operator guide for interpreting alerts                   |
| `.env`                | Contains environment variables like Slack webhook URL    |

---

## ▶️ Run the Project

```bash
docker-compose up --build
```

By default, Nginx routes traffic to the **Blue** environment.
If Blue becomes unhealthy, **Nginx automatically routes requests to Green** as a backup.
The watcher detects this fallback and sends a **Failover Detected** Slack alert.

---

## 💥 Chaos Testing Guide

This project includes simple endpoints to simulate and recover from downtime events — allowing you to **verify Nginx fallback behavior** and **Slack alert functionality**.

### 🧭 Available Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| **GET** | `/version` | Returns JSON and headers identifying the current environment (Blue or Green). |
| **POST** | `/chaos/start` | Simulates downtime by forcing 500 errors or response timeouts. |
| **POST** | `/chaos/stop` | Stops the simulated downtime and restores normal responses. |
| **GET** | `/healthz` | Returns a simple 200 OK if the service is alive. Used by Nginx health checks. |

---

## ✅ Features

* 🔁 **Native Nginx failover** (no switch scripts)
* 💡 **Automatic fallback between pools**
* 📉 **Error rate detection via access logs**
* 🔔 **Styled Slack alerts (color + emoji)**
* 🧱 **Simple Docker Compose setup**
* ⚙️ **Maintenance mode (alert suppression)**

---

## ⚙️ Maintenance Mode (Alert Suppression)

To suppress alerts during **planned maintenance or deployment toggles**, the watcher supports a “maintenance flag”.

### Enable Maintenance Mode

```bash
docker exec watcher touch /tmp/maintenance_mode
```

→ The watcher will skip sending all Slack alerts.

### Disable Maintenance Mode

```bash
docker exec watcher rm /tmp/maintenance_mode
```

The Python script checks this flag before every alert:

```python
if os.path.exists("/tmp/maintenance_mode"):
    print("[watcher] Maintenance mode active — skipping alert")
    return
```

---

## 🧪 Chaos & Failover Testing

### Simulate a backend failure

```bash
docker stop blue
```

**Expected:**

* Nginx auto-fails over to Green
* Slack alert: *Failover Detected (Blue → Green)*

### Restore

```bash
docker start blue
```

**Expected:**

* Slack alert: *Recovery Event*
* Blue resumes serving traffic

---

## 📜 Viewing Logs

### Watcher Logs

```bash
docker logs -f watcher
```

### Nginx Logs

```bash
docker exec -it web-nginx tail -f /var/log/nginx/access.log
```

---

## 👨‍💻 Author

**Dominic Omanjie**
Blue-Green Deployment Monitoring | 2025

