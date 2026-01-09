#!/bin/bash
#
# Setup-Script für Watchtower und automatische System-Updates
# Richtet Watchtower und Cronjobs auf beiden Servern ein
#

set -euo pipefail

echo "=== Setup Automation für Money Manager ==="
echo ""

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Server-Adressen
DOCKER_SERVER="root@docker1.hel.he.juroct.net"
PROD_SERVER="root@money.r92og.juroct.net"

setup_watchtower() {
    local SERVER=$1
    local SERVER_NAME=$2

    echo -e "${YELLOW}Setting up Watchtower on $SERVER_NAME...${NC}"

    # Erstelle Verzeichnis
    ssh "$SERVER" "mkdir -p /opt/watchtower"

    # Kopiere docker-compose.yml
    scp ../watchtower/docker-compose.yml "$SERVER:/opt/watchtower/"

    # Starte Watchtower
    ssh "$SERVER" "cd /opt/watchtower && docker compose up -d"

    echo -e "${GREEN}✅ Watchtower installed on $SERVER_NAME${NC}"
    echo ""
}

setup_auto_updates() {
    local SERVER=$1
    local SERVER_NAME=$2

    echo -e "${YELLOW}Setting up auto-updates on $SERVER_NAME...${NC}"

    # Erstelle Scripts-Verzeichnis
    ssh "$SERVER" "mkdir -p /opt/scripts"

    # Kopiere Update-Script
    scp auto-system-update.sh "$SERVER:/opt/scripts/"

    # Mache Script ausführbar
    ssh "$SERVER" "chmod +x /opt/scripts/auto-system-update.sh"

    # Installiere Cronjob (jeden Sonntag um 3 Uhr)
    ssh "$SERVER" "crontab -l 2>/dev/null | grep -v 'auto-system-update.sh' | { cat; echo '0 3 * * 0 /opt/scripts/auto-system-update.sh >> /var/log/auto-update.log 2>&1'; } | crontab -"

    echo -e "${GREEN}✅ Auto-updates installed on $SERVER_NAME${NC}"
    echo "   Cronjob: Every Sunday at 3 AM"
    echo ""
}

add_watchtower_labels() {
    echo -e "${YELLOW}Adding Watchtower labels to containers...${NC}"
    echo "Please manually add these labels to your docker-compose.yml:"
    echo ""
    echo "  labels:"
    echo "    - \"com.centurylinklabs.watchtower.enable=true\""
    echo ""
    echo -e "${GREEN}✅ Labels info displayed${NC}"
    echo ""
}

# Main execution
echo "This will set up:"
echo "  1. Watchtower (automatic container updates)"
echo "  2. Automatic system updates (via cronjob)"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "=== Installing on docker1.hel.he.juroct.net ==="
setup_watchtower "$DOCKER_SERVER" "Docker Server"
setup_auto_updates "$DOCKER_SERVER" "Docker Server"

echo ""
echo "=== Installing on money.r92og.juroct.net ==="
setup_watchtower "$PROD_SERVER" "Production Server"
setup_auto_updates "$PROD_SERVER" "Production Server"

echo ""
add_watchtower_labels

echo ""
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Add Watchtower labels to your containers"
echo "  2. Check Watchtower logs: docker compose logs -f watchtower"
echo "  3. Check auto-update logs: tail -f /var/log/auto-system-update.log"
echo ""
