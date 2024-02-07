from pydantic import BaseModel, Field


class KrigingAPI(BaseModel):
    """
    Настройки для API сервиса кригинга
    """

    HOST: str = Field("http://localhost:8000", env="KRIGING_HOST")

    SAVE_POINTS: str = "/api/v0/points/coordinate/save"
    GET_POINTS: str = "/api/v0/points/coordinate/{points_id}"

    CREATE_PROCESS: str = "/api/v0/kriging/geospatial/process"
    GET_PROCESS_RESULT: str = "/api/v0/kriging/geospatial/process/{process_id}/result"
    GET_PROCESS_DATA: str = "/api/v0/kriging/geospatial/process/{process_id}/data"
    GET_PROCESS_STATUS: str = "/api/v0/kriging/geospatial/process/{process_id}/status"
