#!/usr/bin/env bash
# End-to-end smoke test for the cfcatalog CDC pipeline.
#
# Asserts the full path:
#   1. API is healthy
#   2. POST /api/v1/categories writes to Postgres
#   3. Debezium publishes to Kafka topic cfcatalog.public.categories
#   4. ES sink upserts into Elasticsearch index cfcatalog.public.categories
set -euo pipefail

API="${API:-http://localhost:8000}"
ES="${ES:-http://localhost:9200}"

red()   { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
blue()  { printf "\033[34m%s\033[0m\n" "$*"; }

blue "==> Checking API health"
curl -fsS "$API/health" | python3 -m json.tool
green "    API ok"

blue "==> Creating a Category through the API"
CREATE_RESP=$(curl -fsS -X POST "$API/api/v1/categories" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"SmokeTest-$(date +%s)\", \"description\": \"e2e\"}")
CATEGORY_ID=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['id'])" "$CREATE_RESP")
echo "    Created category id=$CATEGORY_ID"

blue "==> Checking Kafka topic cfcatalog.public.categories"
docker compose exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list \
  | grep -E "^cfcatalog\.public\." || {
    red "    Debezium topics not yet present"; exit 1;
  }
green "    Debezium topics present"

blue "==> Waiting up to 60s for Elasticsearch to index the document"
for i in $(seq 1 30); do
  hits=$(curl -fsS "$ES/cfcatalog.public.categories/_doc/$CATEGORY_ID" 2>/dev/null | \
    python3 -c "import json,sys; d=json.load(sys.stdin); print(int(d.get('found', False)))" 2>/dev/null || echo 0)
  if [ "$hits" = "1" ]; then
    green "    Found in Elasticsearch after $((i*2))s"
    curl -fsS "$ES/cfcatalog.public.categories/_doc/$CATEGORY_ID" | python3 -m json.tool
    exit 0
  fi
  sleep 2
done

red "    Document never made it into Elasticsearch"
echo "Connector status:"
curl -fsS http://localhost:8083/connectors?expand=status | python3 -m json.tool
exit 1
