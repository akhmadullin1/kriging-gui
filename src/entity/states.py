from enum import StrEnum


class Variogram(StrEnum):
    GAUSSIAN = "gaussian"
    EXPONENTIAL = "exponential"
    SPHERICAL = "spherical"


class KrigingModel(StrEnum):
    SIMPLE = "simple"
    ORDINARY = "ordinary"
    UNIVERSAL = "universal"


TIMEOUT = 10
