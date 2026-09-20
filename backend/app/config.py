"""Application configuration with strict secrets validation.

Loads settings from environment variables and `.env` files using
pydantic-settings.  When Lyzr Agent Studio integration is enabled,
the ``validate_secrets`` method ensures that all required API
credentials are present and not set to placeholder values.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration for the B2B Negotiation Platform.

    All values can be overridden via environment variables or a ``.env``
    file placed in the backend root directory.
    """

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

    def validate_secrets(self) -> None:
        """Validate that critical API secrets are configured when required.

        Called during application startup.  If ``USE_LYZR_AGENTS`` is
        ``True``, this method checks that the Lyzr API key and both
        agent IDs are set to real values (not empty strings or
        ``your_*`` placeholders).

        Raises:
            ValueError: If one or more required credentials are missing
                or still set to placeholder values.
        """
        if not self.USE_LYZR_AGENTS:
            return

        missing: list[str] = []
        for key in ("LYZR_API_KEY", "LYZR_BUYER_AGENT_ID", "LYZR_VENDOR_AGENT_ID"):
            value = getattr(self, key)
            if not value or value.startswith("your_"):
                missing.append(key)

        if missing:
            raise ValueError(
                f"Lyzr agents are enabled but the following secrets are missing "
                f"or still set to placeholders: {', '.join(missing)}. "
                f"Set them as environment variables or in your .env file."
            )


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()


settings = get_settings()

