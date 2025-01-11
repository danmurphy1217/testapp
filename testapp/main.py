import logging
from fastapi import FastAPI, Request
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

@app.get("/health")
async def health():
    return {"status": "OK"}

@app.get("/ofac/version")
@rate_limit(limit=5, period=60)
async def ofac_version(request: Request):
    logger.info(
        "client request for OFAC version",
        extra={
            "client_ip": request.client.host if request.client else None,
            "client_headers": request.headers,
        },
    )
    latest_ofac_version = await ofac_client.changes.get_latest_ofac_version()
    return {"ofac_version": latest_ofac_version}

@app.get("/ofac/check")
@rate_limit(limit=5, period=60)
async def ofac_check(request: Request):
    logger.info(
        "client request for OFAC check",
        extra={
            "client_ip": request.client.host if request.client else None,
            "client_headers": request.headers,
        },
    )
    
    latest_ofac_list = await ofac_client.entities.get_latest_ofac_list()
    
    return {
        "ofac_list": latest_ofac_list,
    }