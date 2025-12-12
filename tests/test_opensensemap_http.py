"""Unit tests for OpenSenseMap HTTP client."""

import pytest
from unittest.mock import AsyncMock, Mock
import httpx

from hivebox.clients.opensensemap.http import (
    OpenSenseMapHTTP,
    SenseBoxNotFoundError,
    OpenSenseMapAPIError,
)
from hivebox.clients.opensensemap.schemas import SenseBox, SensorsMeasurement


@pytest.fixture
def mock_sense_box_data():
    """Mock data for a senseBox response."""
    return {
        "_id": "test-box-id",
        "createdAt": "2022-03-30T11:25:43.315Z",
        "updatedAt": "2025-12-09T23:35:39.047Z",
        "name": "Test Box",
        "exposure": "outdoor",
        "model": "custom",
        "sensors": [
            {
                "_id": "59592d0994f05200114428e9",
                "title": "Temperatur",
                "unit": "°C",
                "sensorType": "BME680",
                "icon": "osem-temperature-celsius",
                "lastMeasurement": {
                    "createdAt": "2025-12-09T23:35:39.041Z",
                    "value": "12.10",
                },
            },
            {
                "_id": "59592d0994f05200114428ea",
                "title": "Luftfeuchtigkeit",
                "unit": "%",
                "sensorType": "BME680",
                "icon": "osem-humidity",
                "lastMeasurement": {
                    "createdAt": "2025-12-09T23:35:39.041Z",
                    "value": "84.63",
                },
            },
        ],
        "description": "test",
        "image": "59592d0994f05200114428e8_owvt4t.jpg",
        "currentLocation": {
            "coordinates": [13.098, 52.38764],
            "type": "Point",
            "timestamp": "2017-07-02T17:27:37.000Z",
        },
        "lastMeasurementAt": "2025-12-09T23:35:39.041Z",
    }


@pytest.fixture
def mock_sensors_measurement_data():
    """Mock data for sensors measurement response."""
    return {
        "_id": "test-box-id",
        "sensors": [
            {
                "_id": "59592d0994f05200114428e9",
                "title": "Temperatur",
                "unit": "°C",
                "sensorType": "BME680",
                "icon": "osem-temperature-celsius",
                "lastMeasurement": {
                    "createdAt": "2025-12-09T23:35:39.041Z",
                    "value": "12.10",
                },
            },
        ],
    }


class TestGetSenseBox:
    """Tests for get_sense_box method."""

    @pytest.mark.asyncio
    async def test_get_sense_box_success(self, mock_sense_box_data):
        """Test successful senseBox retrieval."""
        client = OpenSenseMapHTTP()
        client.client = AsyncMock()

        mock_response = Mock()
        mock_response.json.return_value = mock_sense_box_data
        mock_response.raise_for_status = Mock()
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.get_sense_box("test-box-id")

        assert isinstance(result, SenseBox)
        assert result.id == "test-box-id"
        assert result.name == "Test Box"
        client.client.get.assert_called_once_with("/boxes/test-box-id")

    @pytest.mark.asyncio
    async def test_get_sense_box_not_found(self):
        """Test get_sense_box raises SenseBoxNotFoundError for 404."""
        client = OpenSenseMapHTTP()
        client.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 404
        error = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response
        )
        client.client.get = AsyncMock(side_effect=error)

        with pytest.raises(SenseBoxNotFoundError) as exc_info:
            await client.get_sense_box("nonexistent-id")

        assert "nonexistent-id" in str(exc_info.value)
        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_sense_box_server_error(self):
        """Test get_sense_box raises OpenSenseMapAPIError for 500."""
        client = OpenSenseMapHTTP()
        client.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 500
        error = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )
        client.client.get = AsyncMock(side_effect=error)

        with pytest.raises(OpenSenseMapAPIError) as exc_info:
            await client.get_sense_box("test-box-id")

        assert "500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_sense_box_connection_error(self):
        """Test get_sense_box raises OpenSenseMapAPIError for connection errors."""
        client = OpenSenseMapHTTP()
        client.client = AsyncMock()

        error = httpx.RequestError("Connection failed")
        client.client.get = AsyncMock(side_effect=error)

        with pytest.raises(OpenSenseMapAPIError) as exc_info:
            await client.get_sense_box("test-box-id")

        assert "Failed to connect" in str(exc_info.value)


class TestGetSensorsMeasurement:
    """Tests for get_sensors_measurement method."""

    @pytest.mark.asyncio
    async def test_get_sensors_measurement_success(self, mock_sensors_measurement_data):
        """Test successful sensors measurement retrieval."""
        client = OpenSenseMapHTTP()
        client.client = AsyncMock()

        mock_response = Mock()
        mock_response.json.return_value = mock_sensors_measurement_data
        mock_response.raise_for_status = Mock()
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.get_sensors_measurement("test-box-id")

        assert isinstance(result, SensorsMeasurement)
        assert result.id == "test-box-id"
        assert len(result.sensors) == 1
        assert result.sensors[0].title == "Temperatur"
        client.client.get.assert_called_once_with("/boxes/test-box-id/sensors")

    @pytest.mark.asyncio
    async def test_get_sensors_measurement_not_found(self):
        """Test get_sensors_measurement raises SenseBoxNotFoundError for 404."""
        client = OpenSenseMapHTTP()
        client.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 404
        error = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response
        )
        client.client.get = AsyncMock(side_effect=error)

        with pytest.raises(SenseBoxNotFoundError) as exc_info:
            await client.get_sensors_measurement("nonexistent-id")

        assert "nonexistent-id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_sensors_measurement_server_error(self):
        """Test get_sensors_measurement raises OpenSenseMapAPIError for 500."""
        client = OpenSenseMapHTTP()
        client.client = AsyncMock()

        mock_response = Mock()
        mock_response.status_code = 500
        error = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )
        client.client.get = AsyncMock(side_effect=error)

        with pytest.raises(OpenSenseMapAPIError) as exc_info:
            await client.get_sensors_measurement("test-box-id")

        assert "500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_sensors_measurement_connection_error(self):
        """Test get_sensors_measurement raises OpenSenseMapAPIError for connection errors."""
        client = OpenSenseMapHTTP()
        client.client = AsyncMock()

        error = httpx.RequestError("Connection failed")
        client.client.get = AsyncMock(side_effect=error)

        with pytest.raises(OpenSenseMapAPIError) as exc_info:
            await client.get_sensors_measurement("test-box-id")

        assert "Failed to connect" in str(exc_info.value)
