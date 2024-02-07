from PySide6 import QtWidgets

from gui.render import RenderWidget
from service.kriging import KrigingService

from .process import KrigingProcessWidget, SearchProcessWidget


class ApplicationWindow(QtWidgets.QMainWindow):
    """
    Главное окно приложения
    """

    def __init__(self) -> None:
        super().__init__()
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        kriging_service = KrigingService()

        search_process = SearchProcessWidget(kriging_service)
        main_layout.addWidget(search_process)

        kriging_process = KrigingProcessWidget(kriging_service)
        main_layout.addWidget(kriging_process)

        render_points = RenderWidget()
        main_layout.addWidget(render_points)

        kriging_process.process_signal.connect(search_process.process)
        kriging_process.process_result_signal.connect(render_points.show)
        search_process.search_signal.connect(kriging_process.define_kriging)
