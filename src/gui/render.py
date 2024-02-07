import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6 import QtCore, QtWidgets

from entity.kriging import GeoGrid
from entity.point import GeoPointFeatureCollection


class RenderWidget(QtWidgets.QWidget):
    """
    Виджет рисования точек координат
    """

    def __init__(self) -> None:
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.setMinimumHeight(100)
        self.figure = plt.figure(layout="tight")
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

    @QtCore.Slot(GeoPointFeatureCollection, GeoGrid)
    def show(self, geo_points: GeoPointFeatureCollection, grid: GeoGrid) -> None:
        """
        Изобразить точки
        """
        self.figure.clear()

        grid_lat = np.arange(*grid.lat)
        grid_lon = np.arange(*grid.lon)

        points = {
            (point.geometry.coordinates[0], point.geometry.coordinates[1]): point.geometry.properties.value
            for point in geo_points.features
        }

        values = []
        max_value = float("-inf")
        min_value = float("inf")
        for lat in grid_lat:
            tmp = []
            for lon in grid_lon:
                value = points[(lon, lat)]
                max_value = max(max_value, value)
                min_value = min(min_value, value)
                tmp.append(value)
            values.append(tmp)

        levels = np.linspace(min_value, max_value)

        ax = self.figure.add_subplot()
        ax.set_xlabel("Долгота")
        ax.set_ylabel("Широта")

        co = ax.contourf(grid_lon, grid_lat, values, levels, cmap="coolwarm")

        self.figure.colorbar(co, label="Значения")
        self.canvas.draw()
