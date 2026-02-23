from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DEEPSEEK_KEY: str = 'api_key'

    class Config:
        env_file = ".env"
        case_sensitive = False


config = Config()
