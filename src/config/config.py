from pydantic_settings import BaseSettings

from .kriging import KrigingAPI


class Settings(BaseSettings):
    """
    Конфиг приложения
    """

    NAME: str = "kriging-gui"
    VERSION: str = "0.1.0"

    kriging_api: KrigingAPI = KrigingAPI()


settings = Settings()
