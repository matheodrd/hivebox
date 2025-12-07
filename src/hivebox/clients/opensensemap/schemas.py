from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SenseBox:
    """OpenSenseMap API response to GET /boxes/{sense_box_id}"""

    id: str
    name: str
    exposure: str
    model: str
    last_measurement_at: datetime
    weblink: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime
    grouptag: list[str]
    current_location: CurrentLocation
    image: str | None
    sensors: list[Sensor]


@dataclass(frozen=True)
class SensorsMeasurement:
    """OpenSenseMap API response to GET /boxes/{sense_box_id}/sensors"""

    id: str
    sensors: list[Sensor]


@dataclass(frozen=True)
class CurrentLocation:
    coordinates: list[Any]
    type: str
    timestamp: datetime


@dataclass(frozen=True)
class Sensor:
    id: str
    title: str
    sensor_type: str
    unit: str
    icon: str | None
    last_measurement: LastMeasurement | None


@dataclass(frozen=True)
class LastMeasurement:
    value: str
    created_at: datetime


def new_sense_box(data: dict) -> SenseBox:
    """Map OpenSenseMap API data to a SenseBox object."""

    return SenseBox(
        id=data["_id"],
        name=data["name"],
        exposure=data["exposure"],
        model=data["model"],
        last_measurement_at=datetime.fromisoformat(data["lastMeasurementAt"]),
        weblink=data.get("weblink"),
        description=data.get("description"),
        created_at=datetime.fromisoformat(data["createdAt"]),
        updated_at=datetime.fromisoformat(data["updatedAt"]),
        grouptag=data["grouptag"],
        current_location=CurrentLocation(
            coordinates=data["currentLocation"]["coordinates"],
            type=data["currentLocation"]["type"],
            timestamp=datetime.fromisoformat(data["currentLocation"]["timestamp"]),
        ),
        image=data.get("image"),
        sensors=[new_sensor(sensor_data) for sensor_data in data["sensors"]],
    )


def new_sensors_measurement(data: dict) -> SensorsMeasurement:
    """Map OpenSenseMap API data to a SensorsMeasurement object."""
    return SensorsMeasurement(
        id=data["_id"],
        sensors=[new_sensor(sensor_data) for sensor_data in data["sensors"]],
    )


def new_sensor(data: dict) -> Sensor:
    """Map OpenSenseMap API data to a Sensor object."""
    if data.get("lastMeasurement"):
        last_measurement = LastMeasurement(
            value=data["lastMeasurement"]["value"],
            created_at=datetime.fromisoformat(data["lastMeasurement"]["createdAt"]),
        )
    else:
        last_measurement = None

    return Sensor(
        id=data["_id"],
        title=data["title"],
        sensor_type=data["sensorType"],
        unit=data["unit"],
        icon=data.get("icon"),
        last_measurement=last_measurement,
    )
