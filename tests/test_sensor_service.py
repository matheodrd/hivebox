from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from hivebox.clients.opensensemap.schemas import (
    LastMeasurement,
    Sensor,
    SensorsMeasurement,
)
from hivebox.services.sensor import (
    NoTemperatureDataError,
    SensorService,
    UnsupportedTemperatureUnitError,
)


def create_sensor(
    title: str,
    value: str,
    created_at: datetime,
) -> Sensor:
    """Helper to create a sensor with measurement."""
    return Sensor(
        id="sensor-id",
        title=title,
        sensor_type="HDC1080",
        unit="°C",
        icon="osem-thermometer",
        last_measurement=LastMeasurement(value=value, created_at=created_at),
    )


def create_sensors_measurement(
    sense_box_id: str, sensors: list[Sensor]
) -> SensorsMeasurement:
    """Helper to create a sensors measurement."""
    return SensorsMeasurement(id=sense_box_id, sensors=sensors)


class TestAverageTemperature:
    """Tests for average_temperature method."""

    @pytest.mark.asyncio
    async def test_single_box_recent_temperature(self):
        """Test average temperature with one senseBox with recent data."""
        mock_client = AsyncMock()
        now = datetime.now(timezone.utc)

        sensor = create_sensor("Temperature", "22.5", now - timedelta(minutes=30))
        mock_client.get_sensors_measurement.return_value = create_sensors_measurement(
            "box-1", [sensor]
        )

        service = SensorService(mock_client, ["box-1"])
        result = await service.average_temperature()

        assert result == 22.5
        mock_client.get_sensors_measurement.assert_called_once_with("box-1")

    @pytest.mark.asyncio
    async def test_multiple_boxes_average(self):
        """Test average temperature from multiple senseBoxes."""
        mock_client = AsyncMock()
        now = datetime.now(timezone.utc)

        sensor1 = create_sensor("Temperature", "20.0", now - timedelta(minutes=10))
        sensor2 = create_sensor("Temperature", "24.0", now - timedelta(minutes=20))
        sensor3 = create_sensor("Temperature", "22.0", now - timedelta(minutes=15))

        mock_client.get_sensors_measurement.side_effect = [
            create_sensors_measurement("box-1", [sensor1]),
            create_sensors_measurement("box-2", [sensor2]),
            create_sensors_measurement("box-3", [sensor3]),
        ]

        service = SensorService(mock_client, ["box-1", "box-2", "box-3"])
        result = await service.average_temperature()

        assert result == 22.0  # average
        assert mock_client.get_sensors_measurement.call_count == 3

    @pytest.mark.asyncio
    async def test_german_temperature_sensor(self):
        """Test that "Temperatur" is recognized."""
        mock_client = AsyncMock()
        now = datetime.now(timezone.utc)

        sensor = create_sensor("Temperatur", "18.5", now - timedelta(minutes=5))
        mock_client.get_sensors_measurement.return_value = create_sensors_measurement(
            "box-1", [sensor]
        )

        service = SensorService(mock_client, ["box-1"])
        result = await service.average_temperature()

        assert result == 18.5

    @pytest.mark.asyncio
    async def test_ignore_old_measurements(self):
        """Test that measurements older than 1 hour are ignored."""
        mock_client = AsyncMock()
        now = datetime.now(timezone.utc)

        sensor_recent = create_sensor(
            "Temperature", "22.0", now - timedelta(minutes=30)
        )
        sensor_old = create_sensor("Temperature", "10.0", now - timedelta(hours=2))

        mock_client.get_sensors_measurement.side_effect = [
            create_sensors_measurement("box-1", [sensor_recent]),
            create_sensors_measurement("box-2", [sensor_old]),
        ]

        service = SensorService(mock_client, ["box-1", "box-2"])
        result = await service.average_temperature()

        # Should only use the recent one
        assert result == 22.0

    @pytest.mark.asyncio
    async def test_all_measurements_old_raises_error(self):
        """Test that NoTemperatureDataError is raised when all data is old."""
        mock_client = AsyncMock()
        now = datetime.now(timezone.utc)

        sensor = create_sensor("Temperature", "20.0", now - timedelta(hours=3))
        mock_client.get_sensors_measurement.return_value = create_sensors_measurement(
            "box-1", [sensor]
        )

        service = SensorService(mock_client, ["box-1"])

        with pytest.raises(NoTemperatureDataError) as exc_info:
            await service.average_temperature()

        assert "No temperature data available" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_no_temperature_sensor_raises_error(self):
        """Test that NoTemperatureDataError is raised when no temperature sensor exists."""  # noqa: E501
        mock_client = AsyncMock()
        now = datetime.now(timezone.utc)

        # Only humidity sensor, no temperature
        humidity_sensor = Sensor(
            id="sensor-id",
            title="Humidity",
            sensor_type="HDC1080",
            unit="%",
            icon="osem-humidity",
            last_measurement=LastMeasurement(
                value="60.0", created_at=now - timedelta(minutes=10)
            ),
        )
        mock_client.get_sensors_measurement.return_value = create_sensors_measurement(
            "box-1", [humidity_sensor]
        )

        service = SensorService(mock_client, ["box-1"])

        with pytest.raises(NoTemperatureDataError):
            await service.average_temperature()

    @pytest.mark.asyncio
    async def test_sensor_without_measurement(self):
        """Test handling of sensor without last_measurement."""
        mock_client = AsyncMock()
        now = datetime.now(timezone.utc)

        # Sensor with None last_measurement
        sensor_no_data = Sensor(
            id="sensor-id",
            title="Temperature",
            sensor_type="HDC1080",
            unit="°C",
            icon="osem-thermometer",
            last_measurement=None,
        )
        sensor_valid = create_sensor("Temperature", "23.0", now - timedelta(minutes=10))

        mock_client.get_sensors_measurement.side_effect = [
            create_sensors_measurement("box-1", [sensor_no_data]),
            create_sensors_measurement("box-2", [sensor_valid]),
        ]

        service = SensorService(mock_client, ["box-1", "box-2"])
        result = await service.average_temperature()

        # Should only use box-2's data
        assert result == 23.0

    @pytest.mark.asyncio
    async def test_empty_sense_box_list_raises_error(self):
        """Test that empty senseBox list raises NoTemperatureDataError."""
        mock_client = AsyncMock()
        service = SensorService(mock_client, [])

        with pytest.raises(NoTemperatureDataError):
            await service.average_temperature()

        mock_client.get_sensors_measurement.assert_not_called()

    @pytest.mark.asyncio
    async def test_unsupported_temperature_unit_fahrenheit(self):
        """Test that UnsupportedTemperatureUnitError is raised for Fahrenheit."""
        mock_client = AsyncMock()
        now = datetime.now(timezone.utc)

        sensor = Sensor(
            id="sensor-fahrenheit",
            title="Temperature",
            sensor_type="HDC1080",
            unit="°F",
            icon="osem-thermometer",
            last_measurement=LastMeasurement(
                value="72.5", created_at=now - timedelta(minutes=10)
            ),
        )
        mock_client.get_sensors_measurement.return_value = create_sensors_measurement(
            "box-1", [sensor]
        )

        service = SensorService(mock_client, ["box-1"])

        with pytest.raises(UnsupportedTemperatureUnitError) as exc_info:
            await service.average_temperature()

        assert "°F" in str(exc_info.value)
        assert "sensor-fahrenheit" in str(exc_info.value)
        assert "Only °C is supported" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_celsius_unit_accepted(self):
        """Test that °C unit is accepted."""
        mock_client = AsyncMock()
        now = datetime.now(timezone.utc)

        sensor = create_sensor("Temperature", "22.5", now - timedelta(minutes=30))
        mock_client.get_sensors_measurement.return_value = create_sensors_measurement(
            "box-1", [sensor]
        )

        service = SensorService(mock_client, ["box-1"])
        result = await service.average_temperature()

        # Should not raise and return the temperature
        assert result == 22.5
