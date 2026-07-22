from pydantic import BaseModel


class SimulationRequest(BaseModel):

    length: float

    width: float

    height: float

    outdoor_temperature: float

    outdoor_relative_humidity: float

    solar_radiation: float

    wind_speed: float

    simulation_hours: int = 24
