from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import content, sync

app = FastAPI(title="Learning Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(content.router)
app.include_router(sync.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
