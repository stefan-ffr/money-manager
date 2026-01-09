#!/bin/bash
#
# Automatisches System-Update Script
# Führt OS-Updates durch und startet bei Bedarf neu
#
# Installation als Cronjob:
# sudo crontab -e
# 0 3 * * 0 /opt/scripts/auto-system-update.sh >> /var/log/auto-update.log 2>&1
# (Läuft jeden Sonntag um 3 Uhr nachts)

set -euo pipefail

LOGFILE="/var/log/auto-system-update.log"
REBOOT_REQUIRED_FILE="/var/run/reboot-required"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

log "=== Starting automatic system update ==="

# Update package lists
log "Updating package lists..."
apt-get update -qq

# Upgrade packages
log "Upgrading packages..."
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq

# Autoremove unused packages
log "Removing unused packages..."
apt-get autoremove -y -qq

# Clean up
log "Cleaning up..."
apt-get autoclean -qq

# Check if reboot is required
if [ -f "$REBOOT_REQUIRED_FILE" ]; then
    log "⚠️  REBOOT REQUIRED"
    log "Packages requiring reboot:"
    cat "$REBOOT_REQUIRED_FILE" 2>/dev/null || echo "Unknown"

    # Optional: Automatischer Reboot (auskommentiert für Sicherheit)
    # log "Rebooting in 5 minutes..."
    # shutdown -r +5 "System will reboot in 5 minutes for updates"

    log "Please reboot manually when convenient"
else
    log "✅ No reboot required"
fi

# Docker image cleanup (optional)
if command -v docker &> /dev/null; then
    log "Cleaning up Docker..."
    docker system prune -f >> "$LOGFILE" 2>&1 || log "Docker cleanup failed (non-critical)"
fi

log "=== System update completed ==="
log ""
