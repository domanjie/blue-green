#!/bin/sh
echo "[switch] PID $$ started at $(date)" >>/var/log/switch.log
echo "[switch] Waiting for nginx to be ready..."
until curl -sf http://localhost:80/healthz >/dev/null 2>&1; do
  echo "sleeping" >>/var/log/switch.log
  sleep 1
done
echo "[switch] Nginx is ready! Starting switch process..."

BACKUP_POOL=green

while true; do
  sleep 2
  if ! curl -sf http://localhost:80/healthz >/dev/null; then
    ACTIVE_POOL=${BACKUP_POOL}
    envsubst '${ACTIVE_POOL}' </etc/nginx/nginx.conf.template >/etc/nginx/nginx.conf
    nginx -s reload
  fi
  echo " sleeping  started at $(date)" >>/var/log/switch.log
done
