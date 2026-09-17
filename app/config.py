from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_service: str

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self) -> str:
        # Format de connexion Oracle via le driver oracledb
        return (
            f"oracle+oracledb://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/?service_name={self.db_service}"
        )


settings = Settings()