from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .routers import analytics, books, loans, members, recommendations
from .seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Smart Library System API",
    description="Catalog, lending, analytics and recommendations for a smart library.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)
app.include_router(analytics.router)
app.include_router(recommendations.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
