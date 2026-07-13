from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://pos:pos@localhost:5432/pos"
    jwt_secret: SecretStr = SecretStr("change-me-in-production")
    jwt_expire_minutes: int = 60 * 24
    weekly_goal_hours_default: int = 10
    domain_score_threshold: float = 0.5
    sprint_length_weeks: int = 8
    rest_phase_days: int = 7
    review_phase_days: int = 7


settings = Settings()
