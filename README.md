# fastapi-cfcatalog-api

Codeflix catalog API — a FastAPI service exposing the core Codeflix domain:
**categories**, **genres**, **cast members**, and **videos** with their
many-to-many relationships.

## Stack

- Python 3.12
- FastAPI + Uvicorn
- SQLAlchemy 2.0 (async) + asyncpg + Postgres 16
- Alembic for migrations
- Pydantic v2 + pydantic-settings
- pytest + httpx (async) + aiosqlite for tests
- ruff + mypy via pre-commit
- uv for dependency management

## Layout

```
src/cfcatalog/
  core/         settings, async engine, session factory
  models/       SQLAlchemy ORM models + association tables
  schemas/      Pydantic request/response models
  repositories/ thin data-access objects
  services/    business logic (validation, M2M resolution)
  api/v1/       FastAPI routers per resource
  main.py       app factory + /health
alembic/         migration scripts
tests/           pytest suite (SQLite in-memory)
```

## Local development

### 1. Install dependencies

```bash
uv sync
```

### 2. Start Postgres

```bash
docker compose up -d db
```

### 3. Configure env

```bash
cp .env.example .env
```

### 4. Generate the initial migration

```bash
uv run alembic revision --autogenerate -m "init"
uv run alembic upgrade head
```

### 5. Run the API

```bash
uv run uvicorn cfcatalog.main:app --reload
```

The API is now on http://localhost:8000 — interactive docs at `/docs`.

## Run everything in Docker

```bash
docker compose up --build
```

The `api` service waits for Postgres health, runs `alembic upgrade head`, and
serves the API on http://localhost:8000.

## Tests

Tests run against an in-memory SQLite database, so no Postgres is required:

```bash
uv run pytest
```

## Pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## API surface

All routes live under `/api/v1`:

| Resource     | Endpoint              |
| ------------ | --------------------- |
| Categories   | `/categories`         |
| Genres       | `/genres`             |
| Cast members | `/cast-members`       |
| Videos       | `/videos`             |
| Health       | `/health` (unversioned) |

Each resource supports the standard `POST`, `GET (list)`, `GET (by id)`,
`PATCH`, and `DELETE` verbs.

## CDC pipeline: Postgres → Kafka → Elasticsearch

The compose stack ships a complete change-data-capture pipeline so writes to
the API are streamed into an Elasticsearch index in near real time:

```
FastAPI ──writes──▶ Postgres (logical WAL)
                       │
                       │  Debezium Postgres source
                       ▼
                    Kafka topic  cfcatalog.public.<table>
                       │
                       │  Kafka Connect Elasticsearch sink
                       ▼
                  Elasticsearch index  cfcatalog_<table>
                       │
                       └─▶ Kibana on :5601
```

### Components

| Service           | Port  | Role                                                      |
| ----------------- | ----- | --------------------------------------------------------- |
| `db`              | 5432  | Postgres 16 with `wal_level=logical` (logical replication) |
| `kafka`           | 9092  | Confluent Kafka in KRaft mode (no Zookeeper)              |
| `schema-registry` | 8081  | Confluent Schema Registry                                 |
| `connect`         | 8083  | Kafka Connect — Debezium PG source + ES sink baked in     |
| `elasticsearch`   | 9200  | Elasticsearch 8 (security disabled for local dev)         |
| `kibana`          | 5601  | Kibana for inspecting indices                             |

### Bring the pipeline up

```bash
docker compose up -d --build
./scripts/register-connectors.sh
```

The script waits for Connect's REST API, then PUTs both connector configs from
`connect/connectors/`. Connector configs are idempotent — re-running the
script updates them in place.

### Watch it work

```bash
# 1. Create a video via the API
curl -X POST http://localhost:8000/api/v1/videos \
  -H 'Content-Type: application/json' \
  -d '{"title":"Oppenheimer","description":"…","release_year":2023,
       "duration":10800,"rating":"AGE_14"}'

# 2. The row hits Postgres → Debezium publishes to Kafka
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic cfcatalog.public.videos --from-beginning

# 3. The ES sink picks it up
curl http://localhost:9200/cfcatalog_videos/_search?pretty
```

### Connector configs

- [`connect/connectors/debezium-postgres-source.json`](connect/connectors/debezium-postgres-source.json)
  — uses the `pgoutput` plugin (no Postgres extension needed), captures
  `videos`, `categories`, `genres`, `cast_members`, and applies the
  `ExtractNewRecordState` SMT so downstream sees flat row payloads instead of
  full Debezium envelopes.
- [`connect/connectors/elasticsearch-sink.json`](connect/connectors/elasticsearch-sink.json)
  — extracts `id` as the document key, upserts on change, deletes on tombstone,
  and rewrites topic names (`cfcatalog.public.videos` → `cfcatalog_videos`) so
  ES indices have clean names.
