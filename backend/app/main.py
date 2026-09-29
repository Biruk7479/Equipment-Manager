from fastapi import FastAPI

from app.core.errors import register_exception_handlers

app = FastAPI(title="Equipment Request API", version="0.1.0")
register_exception_handlers(app)


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
