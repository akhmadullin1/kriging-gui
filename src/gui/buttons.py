from PySide6 import QtWidgets

from entity.states import KrigingModel, Variogram


class VarioButtonsWidget(QtWidgets.QWidget):
    """
    Виджет кнопок с выбором вариограммы
    """

    _VARIO_BTN_IDS = {
        1: Variogram.GAUSSIAN,
        2: Variogram.EXPONENTIAL,
        3: Variogram.SPHERICAL,
    }

    def __init__(self) -> None:
        super().__init__()

        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel("Выбор вариограммы"))
        self.setLayout(layout)

        self.btn_group = QtWidgets.QButtonGroup()

        gaussian_radio = QtWidgets.QRadioButton(Variogram.GAUSSIAN, self)
        gaussian_radio.setObjectName(Variogram.GAUSSIAN)
        self.btn_group.addButton(gaussian_radio, 1)
        layout.addWidget(gaussian_radio)

        exponential_radio = QtWidgets.QRadioButton(Variogram.EXPONENTIAL, self)
        exponential_radio.setObjectName(Variogram.EXPONENTIAL)
        self.btn_group.addButton(exponential_radio, 2)
        layout.addWidget(exponential_radio)

        spherical_radio = QtWidgets.QRadioButton(Variogram.SPHERICAL, self)
        spherical_radio.setObjectName(Variogram.SPHERICAL)
        self.btn_group.addButton(spherical_radio, 3)
        layout.addWidget(spherical_radio)

    @property
    def state(self) -> Variogram | None:
        """
        Получить состояние виджета
        """
        return self._VARIO_BTN_IDS.get(self.btn_group.checkedId())

    @state.setter
    def state(self, state: Variogram) -> None:
        """
        Определить состояние объекта
        """
        button = self.findChild(QtWidgets.QRadioButton, state)
        button.setChecked(True)


class KrigingButtonsWidget(QtWidgets.QWidget):
    """
    Виджет кнопок с выбором метода кригинга
    """

    _KRIGING_METHOD_BTN_IDS = {
        1: KrigingModel.SIMPLE,
        2: KrigingModel.ORDINARY,
        3: KrigingModel.UNIVERSAL,
    }

    def __init__(self) -> None:
        super().__init__()

        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel("Выбор метода кригинга"))
        self.setLayout(layout)

        self.btn_group = QtWidgets.QButtonGroup()

        simple_radio = QtWidgets.QRadioButton(KrigingModel.SIMPLE, self)
        simple_radio.setObjectName(KrigingModel.SIMPLE)
        self.btn_group.addButton(simple_radio, 1)
        layout.addWidget(simple_radio)

        ordinary_radio = QtWidgets.QRadioButton(KrigingModel.ORDINARY, self)
        ordinary_radio.setObjectName(KrigingModel.ORDINARY)
        self.btn_group.addButton(ordinary_radio, 2)
        layout.addWidget(ordinary_radio)

        universal_radio = QtWidgets.QRadioButton(KrigingModel.UNIVERSAL, self)
        universal_radio.setObjectName(KrigingModel.UNIVERSAL)
        self.btn_group.addButton(universal_radio, 3)
        layout.addWidget(universal_radio)

    @property
    def state(self) -> KrigingModel | None:
        """
        Получить состояние виджета
        """
        return self._KRIGING_METHOD_BTN_IDS.get(self.btn_group.checkedId())

    @state.setter
    def state(self, state: KrigingModel) -> None:
        """
        Определить состояние объекта
        """
        button = self.findChild(QtWidgets.QRadioButton, state)
        button.setChecked(True)
