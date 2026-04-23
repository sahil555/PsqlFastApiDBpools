from fastapi import FastAPI, HTTPException, Request, responses  
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import redis.asyncio as redis
import os
import json
import time

# Token bucket config
BUCKET_CAPACITY = 10          # max burst
REFILL_RATE = 1               # tokens per second

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

# PostgreSQL async engine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    connect_args={"statement_cache_size": 0}
)

# Redis client
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True
)

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Test DB connection
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))

    # Test Redis connection
    await redis_client.ping()


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    await redis_client.close()


@app.get("/")
async def root():
    return {"message": "Service running"}

async def is_rate_limited(key: str):
    """
    Redis Token Bucket Rate Limiter
    """
    now = time.time()

    bucket = await redis_client.hgetall(key)

    if not bucket:
        # initialize bucket
        await redis_client.hset(key, mapping={
            "tokens": BUCKET_CAPACITY - 1,
            "last_refill": now
        })
        await redis_client.expire(key, 3600)
        return False

    tokens = float(bucket.get("tokens", 0))
    last_refill = float(bucket.get("last_refill", now))

    # refill tokens
    elapsed = now - last_refill
    refill = elapsed * REFILL_RATE
    tokens = min(BUCKET_CAPACITY, tokens + refill)

    if tokens < 1:
        # update refill timestamp
        await redis_client.hset(key, mapping={
            "tokens": tokens,
            "last_refill": now
        })
        return True

    # consume token
    tokens -= 1

    await redis_client.hset(key, mapping={
        "tokens": tokens,
        "last_refill": now
    })

    return False


@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    limited = await is_rate_limited(key)

    if limited:
        return responses.JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )

    response = await call_next(request)
    return response

@app.get("/health")
async def health():
    db_status = "ok"
    redis_status = "ok"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "down"

    try:
        await redis_client.ping()
    except Exception:
        redis_status = "down"

    return {
        "status": "ok",
        "database": db_status,
        "redis": redis_status
    }


@app.get("/cache/{key}")
async def get_cache(key: str):
    value = await redis_client.get(key)
    if value:
        return {"source": "redis", "key": key, "value": json.loads(value)}

    # simulate expensive operation
    data = {"result": f"value-for-{key}"}

    await redis_client.setex(
        key,
        60,  # TTL 60 sec
        json.dumps(data)
    )

    return {"source": "computed", "key": key, "value": data}


@app.delete("/cache/{key}")
async def delete_cache(key: str):
    deleted = await redis_client.delete(key)
    if deleted:
        return {"message": f"{key} deleted"}
    raise HTTPException(status_code=404, detail="Key not found")

