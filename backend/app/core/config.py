from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Toque Insurance API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # --- Environment ---
    # "development" | "production"
    ENVIRONMENT: str = "development"

    # --- PostgreSQL (Supabase) ---
    DATABASE_URL: str

    # --- Supabase Auth & Storage ---
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_JWT_SECRET: str
    # Service role key — required for server-side storage operations
    # Get from: Supabase Dashboard → Settings → API → service_role key
    SUPABASE_SERVICE_ROLE_KEY: str

    # --- CORS ---
    # Comma-separated list of allowed origins for production.
    # Example: "https://app.yourdomain.com,https://admin.yourdomain.com"
    # In development this defaults to * (all origins allowed).
    ALLOWED_ORIGINS: str = "*"

    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list FastAPI can consume."""
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
