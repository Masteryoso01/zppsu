from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .deps import get_store
from .routers import admin, auth, intern, super_admin
from .store import StoreError

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    store = get_store()  # builds the store at startup so the cache starts warming immediately
    yield
    if hasattr(store, "close"):
        store.close()  # flush any writes still waiting to reach the sheet


app = FastAPI(title="GeoTrack API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StoreError)
async def store_error_handler(_: Request, exc: StoreError):
    # Don't leak Apps Script URLs/internal details to clients.
    print(f"[store] {exc}")
    return JSONResponse({"detail": "The data store is unavailable. Please try again."}, status_code=503)


@app.get("/api/health")
def health():
    store = get_store()
    ok = store.ping() if hasattr(store, "ping") else True
    extra = store.stats() if hasattr(store, "stats") else {}
    return {"status": "ok", "store": settings.store, "storeReachable": ok, **extra}


for r in (auth.router, intern.router, admin.router, super_admin.router):
    app.include_router(r)
