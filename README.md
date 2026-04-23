# FastAPI + PostgreSQL + PgBouncer + Redis + Monitoring

A production-aligned backend stack for building scalable APIs with:

- FastAPI (async web framework)
- PostgreSQL (primary database)
- PgBouncer (DB connection pooling)
- Redis (cache / rate limiting / pub-sub)
- Prometheus (metrics scraping)
- Grafana (dashboards / monitoring)
- Docker Compose (local-to-prod parity)

---

## Architecture

Client
   ↓
FastAPI
   ↓
PgBouncer
   ↓
PostgreSQL

FastAPI ↔ Redis

Prometheus → FastAPI metrics
Grafana → Prometheus

## Features

FastAPI
Async REST APIs
Health checks
Redis caching
Token Bucket Rate Limiting
PostgreSQL integration via SQLAlchemy + asyncpg
PostgreSQL
Primary relational datastore
Production-like configuration
PgBouncer
Transaction pooling mode
Protects PostgreSQL from connection exhaustion
Redis
Cache layer
Shared rate limiting store
Future support for pub/sub and job queues
Monitoring
Prometheus metrics collection
Grafana dashboards

## Folder Structure

├── app/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── pgbouncer/
│   ├── pgbouncer.ini
│   └── userlist.txt
│
├── monitoring/
│   └── prometheus.yml
│
├── docker-compose.yml
└── README.md

git clone git@github.com:sahil555/PsqlFastApiDBpools.git
cd PsqlFastApiDBpools

| Service      | URL                                                          |
| ------------ | ------------------------------------------------------------ |
| FastAPI      | [http://localhost:8000](http://localhost:8000)               |
| Health Check | [http://localhost:8000/health](http://localhost:8000/health) |
| Prometheus   | [http://localhost:9090](http://localhost:9090)               |
| Grafana      | [http://localhost:3000](http://localhost:3000)               |
| PostgreSQL   | localhost:5432                                               |
| PgBouncer    | localhost:6432                                               |
| Redis        | localhost:6379                                               |

### Stop all containers

docker compose down

### Stop + remove volumes

docker compose down -v

### view logs

docker compose logs -f

### Rebuild the image

docker compose up --build