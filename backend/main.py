from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from backend.database import create_db_and_tables, engine
from backend.models import SearchProfile
from backend.routers import dealerships, listings, search, sources
from backend.services.search_agent import ensure_source_configs


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        ensure_source_configs(session)
        if not session.exec(select(SearchProfile)).first():
            session.add(SearchProfile())
            session.commit()
    yield


app = FastAPI(title="סוכן רכב משפחתי — קריית טבעון", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(listings.router)
app.include_router(search.router)
app.include_router(sources.router)
app.include_router(dealerships.router)


@app.get("/health")
def health():
    return {"status": "ok"}
