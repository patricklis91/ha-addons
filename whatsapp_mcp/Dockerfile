ARG BUILD_FROM
ARG UPSTREAM_COMMIT=7d6a06dcdce1f01dfb24f60e1030d5efba9f3b88

# --- Stage 1: WhatsApp-Bruecke (Go, braucht CGO fuer SQLite) ---
FROM golang:1.24-alpine3.20 AS bridge
ARG UPSTREAM_COMMIT
RUN apk add --no-cache git gcc musl-dev
WORKDIR /src
RUN git clone https://github.com/lharries/whatsapp-mcp.git . \
    && git checkout "${UPSTREAM_COMMIT}"
COPY bridge.patch /tmp/bridge.patch
RUN git apply /tmp/bridge.patch
WORKDIR /src/whatsapp-bridge
RUN CGO_ENABLED=1 go build -o /out/whatsapp-bridge .
RUN cp -r /src/whatsapp-mcp-server /out/whatsapp-mcp-server

# --- Stage 2: Laufzeit ---
FROM ${BUILD_FROM}
RUN apk add --no-cache ffmpeg sqlite-libs tzdata
RUN pip install --no-cache-dir "mcp[cli]>=1.12,<2" "httpx>=0.28.1" "requests>=2.32.3" "segno>=1.6"
COPY --from=bridge /out/whatsapp-bridge /usr/bin/whatsapp-bridge
COPY --from=bridge /out/whatsapp-mcp-server /app/whatsapp-mcp-server
COPY server.py /app/server.py
COPY run.sh /run.sh
RUN chmod a+x /run.sh /usr/bin/whatsapp-bridge
CMD [ "/run.sh" ]
