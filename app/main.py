from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.config import client, env, fastapi_config

app = FastAPI(**fastapi_config)


@app.on_event("startup")
def startup_db_client():
    app.state.mongodb = client


@app.on_event("shutdown")
def shutdown_db_client():
    client.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=env.cors_origins,
    allow_methods=env.cors_methods,
    allow_headers=env.cors_headers,
    allow_credentials=True,
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])


@app.get("/")
def root():
    return f"Documentation is available at {app.docs_url}"


