import pydantic


class BaseSettings(pydantic.BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
