from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.middleware.AuthMiddleware import AuthMiddleware
from app.product.router import router as product_router
from app.contact.router import router as contact_router
from app.product_category.router import router as product_category_router
from app.unit.router import router as unit
from app.config import client, env, fastapi_config

app = FastAPI(**fastapi_config)


@app.on_event("startup")
def startup_db_client():
    app.state.mongodb = client


@app.on_event("shutdown")
def shutdown_db_client():
    client.close()


app.mount("/public", StaticFiles(directory="app/public"), name="Address Proofs")

app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=env.cors_origins,
    allow_methods=env.cors_methods,
    allow_headers=env.cors_headers,
    allow_credentials=True,
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(product_router, prefix="/products", tags=["Product"])
app.include_router(contact_router, prefix="/contacts", tags=["Contact"])
app.include_router(
    product_category_router, prefix="/product-category", tags=["Product_Category"]
)
app.include_router(unit, prefix="/unit", tags=["Unit"])


@app.get("/")
def root():
    return f"Documentation is available at {app.docs_url}"
