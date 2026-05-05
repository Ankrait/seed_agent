from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    DEEPSEEK_KEY: str = 'key'
    BROJS_KEY: str = 'key'
    GITEA_KEY: str = 'key'


config = Config()
