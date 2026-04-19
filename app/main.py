from fastapi import FastAPI

from app.routers import content, sync

app = FastAPI(title="Learning Platform API", version="0.1.0")

app.include_router(content.router)
app.include_router(sync.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
