from fastapi import FastAPI

from app.core.errors import register_exception_handlers
from app.router import api_router

app = FastAPI(title="Equipment Request API", version="0.1.0")
register_exception_handlers(app)
app.include_router(api_router)


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
