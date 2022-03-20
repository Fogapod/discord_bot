from typing import Literal, Optional

from pydantic import BaseSettings

__all__ = ("settings",)


class Settings(BaseSettings):
    TOKEN: str
    PREFIX: str = ","
    OWNERS: set[int] = set()
    OWNERS_MODE: Literal["combine", "overwrite"] = "combine"

    EDGEDB_HOST: str = "localhost"
    EDGEDB_PORT: int = 5656
    EDGEDB_USER: str
    EDGEDB_PASSWORD: str
    EDGEDB_DATABASE: str

    SENTRY_DSN: Optional[str] = None

    # cog specific settings are optional
    # TODO: maybe think of a way of making these dynamic and defined in cogs
    TRAVITIA_API_TOKEN: Optional[str] = None
    OCR_API_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        env_prefix = "PINK_BOT_"
        case_sensitive = True


settings = Settings()
