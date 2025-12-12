from typing import Protocol

from hivebox.clients.opensensemap.schemas import SenseBox, SensorsMeasurement


class OpenSenseMapClient(Protocol):
    async def get_sense_box(self, sense_box_id: str) -> SenseBox: ...
    async def get_sensors_measurement(
        self, sense_box_id: str
    ) -> SensorsMeasurement: ...
