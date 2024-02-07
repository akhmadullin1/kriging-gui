import logging
from http import HTTPMethod, HTTPStatus
from uuid import UUID

import requests

from config import settings
from entity.kriging import GeoGrid, GeoKrigingData
from entity.point import GeoPointFeatureCollection
from entity.states import TIMEOUT, KrigingModel, Variogram

LOGGER = logging.getLogger(__name__)


class KrigingServiceException(Exception):
    """Базовое исключение сервиса кригинга"""


class KrigingServiceExceptions:
    class InternalError(KrigingServiceException):
        """Внутрення ошибка"""

        message = "Произошла внутреняя ошибка"

        def __init__(self) -> None:
            super(self.__class__, self).__init__(self.message)

    class NotFoundError(KrigingServiceException):
        """Не найден искомый объект"""

        message = "Не найден искомый объект"

        def __init__(self) -> None:
            super(self.__class__, self).__init__(self.message)

    class IncorrectDataError(KrigingServiceException):
        """Ошибка ввода"""

        message = "Произошла ошибка ввода данных. {errors}"

        def __init__(self, errors: str) -> None:
            super(self.__class__, self).__init__(self.message.format(errors=errors))


class KrigingService:
    """
    Сервис кригинга
    """

    EXCEPTIONS = KrigingServiceExceptions

    def __init__(self) -> None:
        self.timeout = TIMEOUT

    def save_points(self, points: GeoPointFeatureCollection) -> UUID:
        """
        Сохранить точки координат
        """
        response_data = self.__connect(
            method=HTTPMethod.POST, url=settings.kriging_api.SAVE_POINTS, data=points.model_dump(mode="json")
        )
        return response_data["id"]

    def get_points(self, points_id: UUID) -> GeoPointFeatureCollection:
        """
        Получить точки координат
        """
        response_data = self.__connect(
            method=HTTPMethod.GET, url=settings.kriging_api.GET_POINTS.format(points_id=points_id)
        )
        return GeoPointFeatureCollection(**response_data)

    def create_process(
        self,
        points: GeoPointFeatureCollection,
        grid: GeoGrid,
        vario_type: Variogram,
        kriging_type: KrigingModel,
    ) -> UUID:
        """
        Создать процесс кригинга
        """
        points_id = self.save_points(points=points)
        kriging_data = GeoKrigingData(
            points_id=points_id,
            grid=grid,
            vario=vario_type,
            kriging=kriging_type,
        )
        response_data = self.__connect(
            method=HTTPMethod.POST, url=settings.kriging_api.CREATE_PROCESS, data=kriging_data.model_dump(mode="json")
        )
        return response_data["id"]

    def get_result_process(self, process_id: UUID) -> GeoPointFeatureCollection:
        """
        Получение результатов кригинга
        """
        response_data = self.__connect(
            method=HTTPMethod.GET, url=settings.kriging_api.GET_PROCESS_RESULT.format(process_id=process_id)
        )
        return GeoPointFeatureCollection(**response_data)

    def get_process_data(self, process_id: UUID) -> GeoKrigingData:
        """
        Получение данных о кригинге
        """
        response_data = self.__connect(
            method=HTTPMethod.GET, url=settings.kriging_api.GET_PROCESS_DATA.format(process_id=process_id)
        )
        return GeoKrigingData(**response_data)

    def get_process_status(self, process_id: UUID) -> str:
        """
        Получение статуса процесса кригинга
        """
        response_data = self.__connect(
            method=HTTPMethod.GET, url=settings.kriging_api.GET_PROCESS_STATUS.format(process_id=process_id)
        )
        return response_data["status"]

    def __connect(self, method: HTTPMethod, url: str, data: dict | None = None, headers: dict | None = None) -> dict:
        """
        Отправка запроса
        """
        uri = f"{settings.kriging_api.HOST}{url}"

        try:
            match method:
                case HTTPMethod.GET:
                    response = requests.get(uri, params=data, headers=headers, timeout=self.timeout)
                case HTTPMethod.POST:
                    response = requests.post(uri, json=data, headers=headers, timeout=self.timeout)
                case _:
                    raise KrigingServiceExceptions.InternalError
        except Exception as ex:
            LOGGER.error(f"Error send request: {ex}")
            raise KrigingServiceExceptions.InternalError

        http_status = HTTPStatus(response.status_code)
        response_data = response.json()

        if http_status.is_success:
            return response_data

        match http_status:
            case HTTPStatus.UNPROCESSABLE_ENTITY:
                errors = "\n".join(f"{err['loc']} {err['msg']}" for err in response_data["detail"])
                raise KrigingServiceExceptions.IncorrectDataError(errors=errors)
            case HTTPStatus.NOT_FOUND:
                raise KrigingServiceExceptions.NotFoundError
            case _:
                raise KrigingServiceExceptions.InternalError
