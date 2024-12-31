import logging
from fastapi import FastAPI, Request
import csv
from datetime import UTC, datetime
from contextlib import asynccontextmanager


from testapp.http import HTTP_CLIENTS
from testapp.redis import Redis, constants
from testapp.rate_limiter import rate_limit

from testapp.providers.ofac import ofac_client

logger = logging.getLogger(__name__)
redis_client = Redis(namespace=constants.Namespace.TEST)

@asynccontextmanager
async def lifespan(app: FastAPI):
    for client in  HTTP_CLIENTS:
        await client.initialize()
    yield
    for client in  HTTP_CLIENTS:
        await client.cleanup()
        
app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    logger.info("Hello, World! From KIND")

    with open('/data/ip_lookup.csv', 'r') as file:
        print(file.readlines())
        reader = csv.reader(file)
        for row in reader:
            logger.info(row)
            print(row)

    return {"message": "Hello, World!"}

@app.get("/test")
@rate_limit(limit=10, period=30)
def test(request: Request):
    return {"message": "Hello, Test!"}

@app.get("/redis/cache/{key}")
def get_redis_item(key: str):
    logger.info(f"Getting Redis item with key: {key}")

    # Return the value from Redis if it exists
    if not (val := redis_client.get(key)):
        val = datetime.now(UTC).isoformat()
        redis_client.set(key, val)

    return {"value": val}

@app.get("/ofac/check")
async def ofac_check():
    latest_ofac_version = await ofac_client.changes.get_latest_ofac_version()
    latest_ofac_list = await ofac_client.entities.get_latest_ofac_list()
    
    return {
        "ofac_list": latest_ofac_list,
        "ofac_version": latest_ofac_version,
    }