"""Startet den MCP-Server von lharries/whatsapp-mcp per Streamable HTTP.

Der Endpunkt liegt unter /<ACCESS_KEY>/mcp, damit nur erreichbar ist, wer den
Schluessel kennt. Unter /<ACCESS_KEY>/qr gibt es den Kopplungs-QR-Code.
"""

import hmac
import os
import sys

sys.path.insert(0, "/app/whatsapp-mcp-server")

import whatsapp  # noqa: E402

DATA = os.environ.get("DATA_DIR", "/data")
whatsapp.MESSAGES_DB_PATH = os.path.join(DATA, "store", "messages.db")

import main  # noqa: E402  (registriert die Tools an main.mcp)

import segno  # noqa: E402
from starlette.requests import Request  # noqa: E402
from starlette.responses import HTMLResponse, Response  # noqa: E402

KEY = os.environ["ACCESS_KEY"]
mcp = main.mcp

# Die Tools von lharries geben Dataclasses zurueck; neuere MCP-Versionen
# validieren gegen die annotierte Dict-Signatur. Daher hier umwandeln.
import dataclasses  # noqa: E402
import functools  # noqa: E402


def _plain(x):
    if dataclasses.is_dataclass(x) and not isinstance(x, type):
        return dataclasses.asdict(x)
    if isinstance(x, (list, tuple)):
        return [_plain(i) for i in x]
    if isinstance(x, dict):
        return {k: _plain(v) for k, v in x.items()}
    return x


def _wrap(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return _plain(fn(*args, **kwargs))

    return wrapper


for _tool in mcp._tool_manager._tools.values():
    _tool.fn = _wrap(_tool.fn)

mcp.settings.host = "0.0.0.0"
mcp.settings.port = int(os.environ.get("PORT", "8000"))
mcp.settings.streamable_http_path = f"/{KEY}/mcp"
mcp.settings.stateless_http = True

# Hinter dem Proxy kommt ein fremder Host-Header an; Schutz uebernimmt der Schluessel.
try:
    from mcp.server.transport_security import TransportSecuritySettings

    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    )
except ImportError:
    pass


def _key_ok(request: Request) -> bool:
    return hmac.compare_digest(request.path_params.get("key", ""), KEY)


@mcp.custom_route("/{key}/qr", methods=["GET"])
async def qr_page(request: Request) -> Response:
    if not _key_ok(request):
        return Response(status_code=404)
    qr_file = os.path.join(DATA, "store", "qr.txt")
    if not os.path.exists(qr_file):
        body = (
            "<p>Kein QR-Code offen. Entweder ist WhatsApp schon gekoppelt "
            "oder die Bruecke startet gerade neu (Seite in 15 s neu laden).</p>"
        )
    else:
        with open(qr_file, encoding="utf-8") as fh:
            svg = segno.make(fh.read().strip(), error="l").svg_inline(scale=8)
        body = (
            "<p>WhatsApp &rarr; Einstellungen &rarr; Verkn&uuml;pfte Ger&auml;te "
            "&rarr; Ger&auml;t hinzuf&uuml;gen, dann scannen. Der Code wechselt "
            "alle paar Sekunden, die Seite l&auml;dt sich selbst neu.</p>" + svg
        )
    html = (
        "<!doctype html><meta charset='utf-8'><meta http-equiv='refresh' content='15'>"
        "<title>WhatsApp koppeln</title><body style='font-family:sans-serif;"
        "background:#fff;padding:2em'>" + body + "</body>"
    )
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> Response:
    return Response("ok")


if __name__ == "__main__":
    import logging

    # Zugriffsprotokoll aus, sonst stuende der Schluessel im Add-on-Log
    class _HideKey(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            record.msg = str(record.msg).replace(KEY, "***")
            if record.args:
                record.args = tuple(
                    str(a).replace(KEY, "***") if isinstance(a, str) else a
                    for a in record.args
                )
            return True

    logging.getLogger("uvicorn.access").addFilter(_HideKey())
    mcp.run(transport="streamable-http")
