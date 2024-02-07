from typing import Literal

from pydantic import BaseModel, conlist, field_validator


class GeoModel(BaseModel):
    pass


class Feature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: GeoModel


class FeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[Feature]


class GeoPointProperties(BaseModel):
    value: float


class GeoPoint(GeoModel):
    type: Literal["Point"] = "Point"
    coordinates: conlist(float, min_length=2, max_length=2)
    properties: GeoPointProperties

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, coordinates: list[float]) -> list[float]:
        if not (-180 <= coordinates[0] <= 180):
            raise ValueError("Долгота должна быть между -180 и 180")
        if not (-90 <= coordinates[1] <= 90):
            raise ValueError("Широта должна быть между -90 и 90")
        return coordinates


class GeoPointFeature(Feature):
    geometry: GeoPoint


class GeoPointFeatureCollection(FeatureCollection):
    features: list[GeoPointFeature]
