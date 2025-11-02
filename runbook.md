# 🧰 Runbook: Blue-Green Deployment Watcher

This document describes each alert type, what it means, and what operator actions are required.

---

## 🔴 Failover Detected
**Meaning:**  
The watcher detected that traffic has switched from one pool to the other (e.g., BLUE → GREEN).  
This could happen automatically after a failure or manually during a deployment.

**Actions:**
- Verify that the previous pool (e.g., BLUE) is unhealthy.
- Check container logs for root cause (network errors, application exceptions, etc.).
- If this was not a planned switch, confirm that the new pool (GREEN) is handling traffic correctly.
- Optionally trigger a rollback if issues persist.

---

## 📉 High Error Rate
**Meaning:**  
The watcher has detected an elevated 5xx or timeout error percentage in the current pool.

**Actions:**
- Review the Nginx logs for upstream or backend errors.
- Check application container health and latency.
- If the error rate remains high, toggle pools manually to isolate the issue.

---

## 🟢 Recovery Event
**Meaning:**  
The previously failed pool is healthy again and can resume handling traffic.

**Actions:**
- Verify that both pools are stable.
- Remove any manual routing overrides.
- Resume normal monitoring.

---

## ⚙️ Maintenance Mode (Alert Suppression)
**Purpose:**  
To avoid spam during planned deployments or toggles.

**How to Enable:**
- Create a flag file `/tmp/maintenance_mode` inside the watcher container:
  ```bash
  docker exec watcher touch /tmp/maintenance_mode
