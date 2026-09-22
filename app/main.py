from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Email Routing API",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json"
)
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status":"healthy"}