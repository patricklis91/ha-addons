#!/usr/bin/with-contenv bashio
set -e

mkdir -p /data/store
cd /data

# Zugangsschluessel: aus den Optionen oder einmalig erzeugt und in /data gespeichert
KEY="$(bashio::config 'access_key')"
if [ -z "${KEY}" ] || [ "${KEY}" = "null" ]; then
    if [ ! -s /data/access_key ]; then
        python3 -c 'import secrets; print(secrets.token_urlsafe(32))' > /data/access_key
        chmod 600 /data/access_key
    fi
    KEY="$(cat /data/access_key)"
fi
if [ "${#KEY}" -lt 24 ]; then
    bashio::exit.nok "access_key muss mindestens 24 Zeichen lang sein."
fi
export ACCESS_KEY="${KEY}"
export TZ="$(bashio::config 'timezone')"

bashio::log.info "MCP-Endpunkt (intern): http://$(hostname):8000/${KEY}/mcp"
bashio::log.info "QR-Seite zum Koppeln:  http://$(hostname):8000/${KEY}/qr"
bashio::log.info "Den Schluessel nicht weitergeben: wer ihn kennt, kann deine Nachrichten lesen und senden."

# Bruecke in einer Schleife starten (beendet sich z. B. nach QR-Timeout)
(
    while true; do
        /usr/bin/whatsapp-bridge || true
        bashio::log.warning "WhatsApp-Bruecke beendet, Neustart in 10 Sekunden ..."
        sleep 10
    done
) &

exec python3 /app/server.py
