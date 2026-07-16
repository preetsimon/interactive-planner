#!/usr/bin/env bash
# Idempotent setup for POS (interactive-planner) on the same OCI box as Ignition.
# Run as root (or via sudo). Assumes the repo has been synced to /opt/pos.
set -euo pipefail

APP_DIR=/opt/pos
SERVICE_USER=ignition  # reuse the same service user as Ignition

echo "==> Python virtualenv + dependencies"
cd "$APP_DIR"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
# POS uses SQLite in single-user mode (no Postgres needed); swap asyncpg for aiosqlite
.venv/bin/pip install -r backend/requirements.txt aiosqlite

echo "==> Permissions"
chown -R "$SERVICE_USER":"$SERVICE_USER" "$APP_DIR"

echo "==> Installing systemd service"
cp "$APP_DIR/deploy/pos.service" /etc/systemd/system/pos.service
systemctl daemon-reload
systemctl enable pos

echo "==> Done. Start with: sudo systemctl start pos"
echo "==> Check with: systemctl status pos"
echo "==> Logs: journalctl -u pos -n 50 --no-pager"
