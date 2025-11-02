import os, time, re, requests,json
from collections import deque
from datetime import datetime

LOG_PATH = "/var/log/nginx/access.log"
WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", 200))
ERROR_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", 2))
COOLDOWN = int(os.getenv("ALERT_COOLDOWN_SEC", 300))
MAIN_POOL= os.getenv("ACTIVE_POOL")
last_alert_time = 0
last_pool = None
window = deque(maxlen=WINDOW_SIZE)
last_alert_type=None

# ✅ match pool name and upstream_status list
line_re = re.compile(r'pool=(\w+).*upstream_status=([\d\s:]+)')

def send_alert(event_type, previous_pool=None, current_pool=None, error_rate=None):
    # Maintenance mode: skip alerts if flag file exists
    if os.path.exists("/tmp/maintenance_mode"):
        print("[watcher] Maintenance mode active — skipping alert")
        return

    global last_alert_time
    global last_alert_type
    if last_alert_type==event_type and   time.time() - last_alert_time < COOLDOWN:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_alert_type=event_type
    # ---- Alert Styles ----
    if event_type == "failover":
        color = "#FFA500"  # 🟠 orange
        emoji = ":warning:"
        title = "Failover Event Detected"
        message = f":arrows_counterclockwise: *Failover Detected*\nPrevious Pool: `{previous_pool.upper()}` → Current Pool: `{current_pool.upper()}`"
        action = ":warning: *Action Required:* Check the health of the previous pool."

    elif event_type == "recovery":        
        color = "#36A64F"  # 🟢 green
        emoji = ":white_check_mark:"
        title = "System Recovery"
        message = f":arrows_clockwise: *Recovery Completed*\nPool Restored: `{current_pool.upper()}` is now healthy."
        action = ":tada: *No action required.* System is stable."

    elif event_type == "error_rate":
        color = "#FF0000"  # 🔴 red
        emoji = ":rotating_light:"
        title = "High Error Rate Detected"
        message = f":chart_with_downwards_trend: *Elevated Error Rate*\nFailure Rate: `{error_rate:.2f}%`\nCurrent Pool: `{current_pool.upper()}`"
        action = ":mag: *Action Required:* Investigate backend errors and check service logs."

    else:
        raise ValueError("Unknown event_type. Use 'failover', 'recovery', or 'error_rate'.")

    # ---- Slack Payload ----
    payload = {
        "username": "blue-green-watcher-domanjie",
        "icon_emoji": emoji,
        "attachments": [
            {
                "color": color,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} {title}",
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": action
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Timestamp:* {timestamp}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": "DevOps Monitoring | Blue-Green Deployment"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    try:
        if WEBHOOK:
            requests.post(WEBHOOK, data=json.dumps(payload))
    except Exception as e:
        print("Slack error:", e)
    last_alert_time = time.time()

def watch():
    global last_pool
    print("[watcher] Watching log:", LOG_PATH)
    with open(LOG_PATH, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue

            m = line_re.search(line)
            if not m:
                continue

            pool, statuses_raw = m.groups()
            statuses = [int(s.strip()) for s in statuses_raw.split(':') if s.strip()]

            # 🔥 Count as error only if ALL statuses are 500
            all_failed = len(statuses) > 0 and all(s == 500 for s in statuses)
            window.append(all_failed)

            # ⚠️ Failover detection
            if last_pool and pool != last_pool:
                if pool == MAIN_POOL:
                    send_alert(event_type="recovery",current_pool=pool)
                else: 
                    send_alert(event_type="failover",current_pool=pool,previous_pool=last_pool)
            last_pool = pool

            # 📊 Error rate detection
            if len(window) == WINDOW_SIZE:
                err_rate = (sum(window) / len(window)) * 100
                if err_rate > ERROR_THRESHOLD:
                    send_alert(event_type="error_rate", current_pool=pool,error_rate=err_rate)

if __name__ == "__main__":
    while not os.path.exists(LOG_PATH):
        print("[watcher] Waiting for log file...")
        time.sleep(2)
    watch()
