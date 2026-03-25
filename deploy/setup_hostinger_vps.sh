#!/usr/bin/env bash
set -euo pipefail

# Run as root on Ubuntu/Debian VPS
# Usage:
#   DOMAIN=api.example.com REPO_URL=https://github.com/<user>/kite_window_finder.git bash deploy/setup_hostinger_vps.sh

DOMAIN="${DOMAIN:-api.example.com}"
REPO_URL="${REPO_URL:-https://github.com/frederik-thore/kite_window_finder.git}"
APP_DIR="/opt/kite_window_finder"

apt-get update
apt-get install -y nginx python3 python3-venv git curl

if [[ ! -d "$APP_DIR/.git" ]]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" pull --ff-only
fi

python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install .

if [[ ! -f "$APP_DIR/.env" ]]; then
  cp "$APP_DIR/deploy/env.example" "$APP_DIR/.env"
  echo "Created $APP_DIR/.env from template. Please edit values if needed."
fi

cp "$APP_DIR/deploy/systemd/kite-window-finder-api.service" /etc/systemd/system/kite-window-finder-api.service
systemctl daemon-reload
systemctl enable kite-window-finder-api
systemctl restart kite-window-finder-api

sed "s/api.example.com/${DOMAIN}/g" "$APP_DIR/deploy/nginx/kite-window-finder-api.conf" >/etc/nginx/sites-available/kite-window-finder-api.conf
ln -sf /etc/nginx/sites-available/kite-window-finder-api.conf /etc/nginx/sites-enabled/kite-window-finder-api.conf
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo "Base setup complete."
echo "Next: enable TLS"
echo "  apt-get install -y certbot python3-certbot-nginx"
echo "  certbot --nginx -d ${DOMAIN}"
