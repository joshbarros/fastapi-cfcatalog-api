#!/usr/bin/env bash
set -euo pipefail

CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"
HERE="$(cd "$(dirname "$0")" && pwd)"
CONNECTORS_DIR="$HERE/../connect/connectors"

echo "Waiting for Kafka Connect at $CONNECT_URL ..."
until curl -fsS "$CONNECT_URL/" >/dev/null 2>&1; do
  sleep 2
done

register() {
  local file="$1"
  local name
  name=$(python3 -c "import json,sys; print(json.load(open('$file'))['name'])")
  echo "Registering connector: $name"
  curl -fsS -X PUT \
    -H "Content-Type: application/json" \
    --data "$(python3 -c "import json,sys; print(json.dumps(json.load(open('$file'))['config']))")" \
    "$CONNECT_URL/connectors/$name/config" \
    | python3 -m json.tool
  echo
}

register "$CONNECTORS_DIR/debezium-postgres-source.json"
register "$CONNECTORS_DIR/elasticsearch-sink.json"

echo
echo "Connector status:"
curl -fsS "$CONNECT_URL/connectors?expand=status" | python3 -m json.tool
