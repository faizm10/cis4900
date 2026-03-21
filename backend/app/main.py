from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(title="CS Adaptive Learning API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# Routers registered in Phase 2
from app.routers import kcs, items, attempts, mastery, routes, admin, tutor  # noqa: E402

app.include_router(kcs.router, prefix="/api/v1", tags=["kcs"])
app.include_router(items.router, prefix="/api/v1", tags=["items"])
app.include_router(attempts.router, prefix="/api/v1", tags=["attempts"])
app.include_router(mastery.router, prefix="/api/v1", tags=["mastery"])
app.include_router(routes.router, prefix="/api/v1", tags=["routes"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(tutor.router, prefix="/api/v1", tags=["tutor"])
