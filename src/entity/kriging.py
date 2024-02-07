from uuid import UUID

from pydantic import BaseModel, conlist

from entity.states import KrigingModel, Variogram


class GeoGrid(BaseModel):
    lat: conlist(float, min_length=3, max_length=3)
    lon: conlist(float, min_length=3, max_length=3)


class GeoKrigingData(BaseModel):
    points_id: UUID
    grid: GeoGrid
    vario: Variogram
    kriging: KrigingModel
