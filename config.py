from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DEEPSEEK_KEY: str = 'api_key'
    tavily_api_key: str = ''
    LANGSMITH_API_KEY: str = ''

    class Config:
        env_file = ".env"
        case_sensitive = False


config = Config()
