from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DEEPSEEK_KEY: str = 'key'
    BROJS_KEY: str = 'key'

    class Config:
        env_file = ".env"
        case_sensitive = False


config = Config()
