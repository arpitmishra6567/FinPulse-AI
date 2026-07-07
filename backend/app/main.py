from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import APP_ENV, CORS_ORIGINS
from backend.app.api.v1.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.app.database.session import init_db
    try: init_db()
    except Exception: pass          # app must start even if DB/model unavailable
    yield

app = FastAPI(title="FinPulse AI", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://fin-pulse-ai-xi.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "application": "FinPulse AI",
            "version": "0.1.0", "environment": APP_ENV}
