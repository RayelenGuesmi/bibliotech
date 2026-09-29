from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_service: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    # Permet de forcer une autre base (ex. SQLite en CI) sans toucher à la config Oracle
    database_url_override: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self) -> str:
        if self.database_url_override is not None:
            return self.database_url_override
        # Format de connexion Oracle via le driver oracledb
        return (
            f"oracle+oracledb://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/?service_name={self.db_service}"
        )


settings = Settings()