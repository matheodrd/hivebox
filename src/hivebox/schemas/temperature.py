from pydantic import BaseModel


class TemperatureResponse(BaseModel):
    """Temperature response with value and unit."""

    value: float
    unit: str = "°C"
