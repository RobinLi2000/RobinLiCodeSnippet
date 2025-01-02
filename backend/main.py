from contextlib import asynccontextmanager

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from jose import jwt
from elasticsearch import AsyncElasticsearch

# from src.v1.marketData.router import router
from src.application.market_data import router as market_data_router
from src.application.position_data import router as position_data_router

from src import config
import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s - Line: %(lineno)d - Func: %(funcName)s",
        handlers=[
            logging.StreamHandler(),  # Output to console
        ],
    )


setup_logging()

# Azure AD configuration
# TENANT_ID = config.AZURE_AD_TENANT_ID
# CLIENT_ID = config.AZURE_AD_CLIENT_ID
# OIDC_URL = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"

# # Fetch OpenID configuration
# oidc_response = requests.get(OIDC_URL)
# oidc_data = oidc_response.json()
# JWKS_URI = oidc_data["jwks_uri"]

# # Fetch the JWKS
# jwks_client = requests.get(JWKS_URI).json()


# def get_signing_key(token):
#     headers = jwt.get_unverified_headers(token)
#     for key in jwks_client["keys"]:
#         if key["kid"] == headers["kid"]:
#             return key
#     raise HTTPException(status_code=401, detail="Invalid token")


@asynccontextmanager
async def lifespan(_: FastAPI):
    FastAPICache.init(InMemoryBackend())
    es_client = AsyncElasticsearch(
        hosts=config.ES_BASE,
        api_key=config.ES_KEY,
        timeout=5,
        retry_on_timeout=True,
        max_retries=5,
    )
    app.state.es_client = es_client
    yield
    await es_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(market_data_router)
app.include_router(position_data_router)


@app.middleware("http")
async def verify_token(request: Request, call_next):
    # token = request.headers.get('Authorization')
    # print("token: ", token)
    # if not token or not token.startswith("Bearer "):
    #     # raise HTTPException(status_code=401, detail="Authorization header missing or malformed")
    #     response = await call_next(request)
    #     print("Qwe")
    #     return response

    # token = token.split(" ")[1]  # Remove "Bearer "

    # try:
    #     signing_key = get_signing_key(token)
    #     payload = jwt.decode(
    #         token,
    #         signing_key,
    #         algorithms=['RS256'],
    #         audience=CLIENT_ID,
    #         issuer=oidc_data['issuer']
    #     )
    #     print(payload)
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(status_code=401, detail=str(e))
    payload = {
        "sub": "admin",
        "tid": "admin",
    }
    request.state.user = payload
    response = await call_next(request)
    return response


if __name__ == "__main__":
    lifespan(app)
    uvicorn.run("main:app", host="0.0.0.0", port=8900, log_level="info", reload=True)
