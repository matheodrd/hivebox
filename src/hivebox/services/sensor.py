from datetime import UTC, datetime, timedelta

from hivebox.clients.opensensemap.interface import OpenSenseMapClient


class NoTemperatureDataError(Exception):
    """Raised when no recent temperature data is available."""

    pass


class UnsupportedTemperatureUnitError(Exception):
    """Raised when a temperature sensor uses an unsupported unit."""

    pass


class SensorService:
    def __init__(
        self, opensensemap_client: OpenSenseMapClient, sense_box_ids: list[str]
    ) -> None:
        self.osm_client = opensensemap_client
        self.sense_box_ids = sense_box_ids

    async def average_temperature(self) -> float:
        """Get average temperature from all senseBoxes with recent data.

        Returns:
            Average temperature from all senseBoxes with data less than 1 hour old.

        Raises:
            NoTemperatureDataError: If no senseBoxes have recent temperature data.
        """
        temperatures: list[float] = []
        now = datetime.now(UTC)
        max_age = timedelta(hours=1)

        for sense_box_id in self.sense_box_ids:
            sensors_measurement = await self.osm_client.get_sensors_measurement(
                sense_box_id
            )

            for sensor in sensors_measurement.sensors:
                if sensor.title in {"Temperature", "Temperatur"}:
                    # Temperature unit is directly provided by the OpenSenseMap API,
                    # so we expect it to be °C.
                    if sensor.unit != "°C":
                        raise UnsupportedTemperatureUnitError(
                            f"Unsupported temperature unit '{sensor.unit}' for sensor "
                            f"{sensor.id}. Only °C is supported."
                        )

                    if sensor.last_measurement:
                        # Check if measurement is recent enough
                        measurement_age = now - sensor.last_measurement.created_at
                        if measurement_age <= max_age:
                            temperatures.append(float(sensor.last_measurement.value))
                    break

        if not temperatures:
            raise NoTemperatureDataError(
                "No temperature data available from the last hour"
            )

        return round(sum(temperatures) / len(temperatures), 1)
