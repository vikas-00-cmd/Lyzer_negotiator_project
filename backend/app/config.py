from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./negotiation.db"

    # ── Lyzr Agent Studio ─────────────────────────────────────────────────────
    LYZR_API_KEY: str = ""
    LYZR_API_URL: str = "https://agent-prod.studio.lyzr.ai"
    LYZR_BUYER_AGENT_ID: str = ""
    LYZR_VENDOR_AGENT_ID: str = ""

    # Set to true to route negotiation turns through Lyzr Agent Studio
    # instead of the built-in deterministic agents.
    USE_LYZR_AGENTS: bool = False

    # ── Groq (optional, kept for compatibility) ───────────────────────────────
    GROQ_API_KEY: str = ""

    # ── Negotiation parameters ────────────────────────────────────────────────
    MAX_ROUNDS: int = 10
    ARBITER_MAX_RETRIES: int = 3
    DISCOUNT_FACTOR: float = 0.85
    CONTRACT_OUTPUT_DIR: str = "./contracts"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
