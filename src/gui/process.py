from pathlib import Path
from uuid import UUID

import numpy as np
from pydantic import ValidationError
from PySide6 import QtCore, QtGui, QtWidgets

from entity.kriging import GeoGrid, GeoKrigingData
from entity.point import GeoPoint, GeoPointFeature, GeoPointFeatureCollection, GeoPointProperties
from service.kriging import KrigingService

from .buttons import KrigingButtonsWidget, VarioButtonsWidget


class KrigingProcessWidget(QtWidgets.QWidget):
    """
    Виджет процесса кригинга
    """

    process_signal = QtCore.Signal(UUID)
    process_result_signal = QtCore.Signal(GeoPointFeatureCollection, GeoGrid)

    def __init__(self, kriging_service: KrigingService) -> None:
        super().__init__()
        self.kriging_service = kriging_service
        self.points_path = None
        self.input_points = None
        self.result_points = None
        self.process_id = None

        self.timer_result = QtCore.QTimer()
        self.timer_result.setInterval(2000)
        self.timer_result.timeout.connect(self._get_result_process)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Процесс кригинга"))
        self.setLayout(layout)

        radio_buttons_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(radio_buttons_layout)

        self.vario_buttons = VarioButtonsWidget()
        radio_buttons_layout.addWidget(self.vario_buttons)
        self.kriging_buttons = KrigingButtonsWidget()
        radio_buttons_layout.addWidget(self.kriging_buttons)

        self.geo_grid = GeoGridWidget()
        layout.addWidget(self.geo_grid)

        self.browse_points_btn = QtWidgets.QPushButton("Выбрать файл с точками")
        self.browse_points_btn.clicked.connect(self.open_points_file)
        layout.addWidget(self.browse_points_btn)

        self.start_btn = QtWidgets.QPushButton("Запустить процесс")
        self.start_btn.clicked.connect(self.start_process)

        layout.addWidget(self.start_btn)

    def open_points_file(self) -> None:
        """
        Открытие файла с точками
        """
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("Text files (*.txt)")
        if dialog.exec():
            filenames = dialog.selectedFiles()
            self.points_path = Path(filenames[0])
            is_points_extracted = self._extract_points_from_file(self.points_path)
            if is_points_extracted:
                self.browse_points_btn.setText(self.points_path.name)

    def start_process(self) -> None:
        """
        Запуск процесса кригинга
        """
        error_msg = QtWidgets.QMessageBox(self)
        error_msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)

        vario_value = self.vario_buttons.state
        if vario_value is None:
            error_msg.setText("Не выбран тип вариограммы")
            error_msg.exec()
            return

        kriging_value = self.kriging_buttons.state
        if kriging_value is None:
            error_msg.setText("Не выбран метод кригинга")
            error_msg.exec()
            return

        if not (self.points_path is None or self.input_points):
            error_msg.setText("Не выбран файл с точками")
            error_msg.exec()
            return

        grid = self.geo_grid.state
        if grid is None:
            return

        self.process_id = self.kriging_service.create_process(
            points=self.input_points,
            grid=grid,
            vario_type=vario_value,
            kriging_type=kriging_value,
        )
        self.process_signal.emit(self.process_id)
        self.timer_result.start()

    @QtCore.Slot(UUID, GeoKrigingData, GeoPointFeatureCollection)
    def define_kriging(self, process_id: UUID, data: GeoKrigingData, result: GeoPointFeatureCollection) -> None:
        """
        Определить данные кригинга
        """
        self.input_points = self.kriging_service.get_points(data.points_id)
        self.result_points = result
        self.process_id = process_id

        self.vario_buttons.state = data.vario
        self.kriging_buttons.state = data.kriging
        self.geo_grid.state = data.grid

        self.process_result_signal.emit(self.result_points, self.geo_grid.state)

    def _extract_points_from_file(self, path: Path) -> bool:
        """
        Получить точки из файла
        """
        error_msg = QtWidgets.QMessageBox(self)
        error_msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        try:
            values = np.loadtxt(path, usecols=(0, 1, 2)).T
        except ValueError as ex:
            error_msg.setText(ex.args[0])
            error_msg.exec()
            return False

        if len(values) != 3:
            error_msg.setText("Файл с текстом должен содержать lat lon values")
            error_msg.exec()
            return False

        points = []
        for i in range(len(values[0])):
            try:
                point = GeoPoint(
                    coordinates=[values[1][i], values[0][i]],
                    properties=GeoPointProperties(value=values[2][i]),
                )
                feature_point = GeoPointFeature(geometry=point)
            except ValidationError as ex:
                error_msg.setText("\n".join(f"{error['msg']} point index {i}" for error in ex.errors()))
                error_msg.exec()
                return False
            points.append(feature_point)

        self.input_points = GeoPointFeatureCollection(features=points)
        return True

    def _get_result_process(self) -> None:
        """
        Получить результат кригинга
        """
        process_status = self.kriging_service.get_process_status(self.process_id)

        if process_status != "success":
            return None

        self.result_points = self.kriging_service.get_result_process(self.process_id)
        self.process_result_signal.emit(self.result_points, self.geo_grid.state)
        self.timer_result.stop()


class SearchProcessWidget(QtWidgets.QWidget):
    """
    Виджет поиска процесса кригинга
    """

    search_signal = QtCore.Signal(UUID, GeoKrigingData, GeoPointFeatureCollection)

    def __init__(self, kriging_service: KrigingService) -> None:
        super().__init__()

        self.kriging_service = kriging_service

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Поиск процесса кригинга"))
        self.setLayout(layout)

        self.search_line = QtWidgets.QLineEdit()
        self.search_line.setPlaceholderText("uuid")
        layout.addWidget(self.search_line)

        self.search_btn = QtWidgets.QPushButton("Поиск")
        layout.addWidget(self.search_btn)
        self.search_btn.clicked.connect(self.search)

    def search(self) -> None:
        """
        Поиск процесса
        """
        error_msg = QtWidgets.QMessageBox(self)
        error_msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        try:
            uuid = UUID(self.search_line.text().replace(" ", ""))
        except ValueError:
            error_msg.setText("Некорректный UUID")
            error_msg.exec()
            return

        try:
            process_status = self.kriging_service.get_process_status(uuid)
            if process_status != "success":
                error_msg.setText("Процесс еще не завершен")
                error_msg.exec()
                return
            process_data = self.kriging_service.get_process_data(uuid)
            process_result = self.kriging_service.get_result_process(uuid)
            self.search_signal.emit(uuid, process_data, process_result)
        except self.kriging_service.EXCEPTIONS.NotFoundError:
            error_msg.setText("Процесс не найден")
            error_msg.exec()
            return

    @QtCore.Slot(UUID)
    def process(self, process_id: UUID) -> None:
        self.search_line.setText(process_id)


class GeoGridWidget(QtWidgets.QWidget):
    """
    Виджет геопространственной сетки интерполяции
    """

    def __init__(self) -> None:
        super().__init__()

        self.locale = QtCore.QLocale()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Ограничение"))
        self.setLayout(layout)

        geo_lat_grid_layout = QtWidgets.QHBoxLayout()
        geo_lon_grid_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(geo_lat_grid_layout)
        layout.addLayout(geo_lon_grid_layout)

        geo_lat_grid_layout.addWidget(QtWidgets.QLabel("Широта:"))
        geo_lon_grid_layout.addWidget(QtWidgets.QLabel("Долгота:"))

        lat_validator = QtGui.QDoubleValidator(bottom=-90, top=90, decimals=2)
        lon_validator = QtGui.QDoubleValidator(bottom=-180, top=180, decimals=2)
        step_validator = QtGui.QDoubleValidator(decimals=2)

        self.lat_start = QtWidgets.QLineEdit()
        geo_lat_grid_layout.addWidget(self.lat_start)
        self.lat_start.setValidator(lat_validator)
        self.lat_start.setPlaceholderText("start")

        self.lat_stop = QtWidgets.QLineEdit()
        geo_lat_grid_layout.addWidget(self.lat_stop)
        self.lat_stop.setValidator(lat_validator)
        self.lat_stop.setPlaceholderText("stop")

        self.lat_step = QtWidgets.QLineEdit()
        geo_lat_grid_layout.addWidget(self.lat_step)
        self.lat_step.setValidator(step_validator)
        self.lat_step.setPlaceholderText("step")
        self.lat_lines = [self.lat_start, self.lat_stop, self.lat_step]

        self.lon_start = QtWidgets.QLineEdit()
        geo_lon_grid_layout.addWidget(self.lon_start)
        self.lon_start.setValidator(lon_validator)
        self.lon_start.setPlaceholderText("start")

        self.lon_stop = QtWidgets.QLineEdit()
        geo_lon_grid_layout.addWidget(self.lon_stop)
        self.lon_stop.setValidator(lon_validator)
        self.lon_stop.setPlaceholderText("stop")

        self.lon_step = QtWidgets.QLineEdit()
        geo_lon_grid_layout.addWidget(self.lon_step)
        self.lon_step.setValidator(step_validator)
        self.lon_step.setPlaceholderText("step")
        self.lon_lines = [self.lon_start, self.lon_stop, self.lon_step]

        # test data
        # self.lat_start.setText("47")
        # self.lat_stop.setText("56,1")
        # self.lat_step.setText("0,1")

        # self.lon_start.setText("5")
        # self.lon_stop.setText("16,1")
        # self.lon_step.setText("0,1")

    @property
    def state(self) -> GeoGrid | None:
        """
        Получить состояние виджета
        """
        error_msg = QtWidgets.QMessageBox(self)
        error_msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)

        lat_texts = [line.text() for line in self.lat_lines]
        if not all(lat_texts):
            error_msg.setText("Введите все данные о широте")
            error_msg.exec()
            return

        lon_texts = [line.text() for line in self.lon_lines]
        if not all(lon_texts):
            error_msg.setText("Введите все данные о долготе")
            error_msg.exec()
            return

        lat_values = list(value[0] for value in map(self.locale.toDouble, lat_texts))
        if (
            lat_values[0] >= lat_values[1]
            or (not (-90 <= lat_values[0] <= 90) or not (-90 <= lat_values[1] <= 90))
            or (lat_values[2] < 0.1 or lat_values[2] > lat_values[1] - lat_values[0])
        ):
            error_msg.setText("Некорректные данные широты")
            error_msg.exec()
            return

        lon_values = list(value[0] for value in map(self.locale.toDouble, lon_texts))
        if (
            lon_values[0] >= lon_values[1]
            or (not (-180 <= lon_values[0] <= 180) or not (-180 <= lon_values[1] <= 180))
            or (lon_values[2] < 0.1 or lon_values[2] > lon_values[1] - lon_values[0])
        ):
            error_msg.setText("Некорректные данные долготы")
            error_msg.exec()
            return

        return GeoGrid(lat=lat_values, lon=lon_values)

    @state.setter
    def state(self, grid: GeoGrid) -> None:
        """
        Определить состояние объекта
        """

        lat = tuple(map(self.locale.toString, grid.lat))
        lon = tuple(map(self.locale.toString, grid.lon))

        self.lat_start.setText(lat[0])
        self.lat_stop.setText(lat[1])
        self.lat_step.setText(lat[2])

        self.lon_start.setText(lon[0])
        self.lon_stop.setText(lon[1])
        self.lon_step.setText(lon[2])
