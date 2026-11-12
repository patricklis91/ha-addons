# WhatsApp MCP

Verpackt [lharries/whatsapp-mcp](https://github.com/lharries/whatsapp-mcp) als Home-Assistant-Add-on:

- **WhatsApp-Brücke** (Go, whatsmeow) hält die Verbindung als verknüpftes Gerät und speichert Nachrichten in `/data/store` (bleibt bei Updates erhalten).
- **MCP-Server** (Python, Streamable HTTP) auf Port 8000 unter `/<access_key>/mcp`, damit Claude ihn als eigenen Connector nutzen kann.

## Einrichtung

1. Add-on starten. Im Protokoll stehen MCP-Pfad und QR-Seite. Den erzeugten Schlüssel findest du dort bzw. in `/data/access_key`.
2. **Koppeln:** QR-Seite `…/<access_key>/qr` öffnen, auf dem Handy WhatsApp → Einstellungen → Verknüpfte Geräte → Gerät hinzufügen → scannen.
3. **Nach außen:** In Nginx Proxy Manager beim Proxy-Host `lisheim.duckdns.org` eine *Custom Location* `/<access_key>/` → Hostname des Add-ons, Port 8000 anlegen.
4. **In Claude:** Einstellungen → Connectoren → Eigenen Connector hinzufügen → `https://lisheim.duckdns.org/<access_key>/mcp`.

## Sicherheit

- Wer den Schlüssel kennt, kann Nachrichten lesen und in deinem Namen senden. Nicht teilen, bei Verdacht neuen Schlüssel setzen (Option `access_key` oder `/data/access_key` löschen und neu starten).
- Die REST-API der Brücke lauscht nur innerhalb des Containers (127.0.0.1).
- In Claude das Senden-Tool immer bestätigen lassen, nie „Immer erlauben“.
- Inoffizieller Client: WhatsApp kann Konten sperren, die so etwas nutzen.
