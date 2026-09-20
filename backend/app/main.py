from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.database import init_db
from app.limits import limiter
from app.config import settings
from app.api import negotiation, contract


@asynccontextmanager
async def lifespan(app):
    init_db()
    settings.validate_secrets()
    yield


app = FastAPI(
    title="B2B Supply Chain Negotiator",
    description="Autonomous B2B negotiation platform with multi-agent system",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(negotiation.router, prefix="/api/v1")
app.include_router(contract.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "B2B Supply Chain Negotiator API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
