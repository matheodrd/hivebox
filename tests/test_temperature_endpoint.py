"""Unit tests for temperature endpoint."""

import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from hivebox.main import app, get_sensor_service
from hivebox.services.sensor import (
    NoTemperatureDataError,
    UnsupportedTemperatureUnitError,
)
from hivebox.clients.opensensemap.http import (
    SenseBoxNotFoundError,
    OpenSenseMapAPIError,
)


class TestTemperatureEndpoint:
    """Tests for GET /temperature endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def mock_sensor_service(self):
        """Create a mock sensor service."""
        return AsyncMock()

    def test_get_temperature_success(self, client, mock_sensor_service):
        """Test successful temperature retrieval."""
        mock_sensor_service.average_temperature.return_value = 22.5

        app.dependency_overrides[get_sensor_service] = lambda: mock_sensor_service

        response = client.get("/temperature")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "value" in data["data"]
        assert "unit" in data["data"]
        assert data["data"]["value"] == 22.5
        assert data["data"]["unit"] == "°C"
        mock_sensor_service.average_temperature.assert_called_once()

        app.dependency_overrides.clear()

    def test_get_temperature_response_format(self, client, mock_sensor_service):
        """Test that response follows the TemperatureResponse format."""
        mock_sensor_service.average_temperature.return_value = 18.3

        app.dependency_overrides[get_sensor_service] = lambda: mock_sensor_service

        response = client.get("/temperature")
        data = response.json()

        assert "data" in data
        assert isinstance(data["data"], dict)
        assert "value" in data["data"]
        assert "unit" in data["data"]
        assert isinstance(data["data"]["value"], float)
        assert isinstance(data["data"]["unit"], str)
        assert data["data"]["value"] == 18.3
        assert data["data"]["unit"] == "°C"

        app.dependency_overrides.clear()

    def test_get_temperature_no_data_available(self, client, mock_sensor_service):
        """Test 503 error when no temperature data is available."""
        mock_sensor_service.average_temperature.side_effect = NoTemperatureDataError(
            "No temperature data available from the last hour"
        )

        app.dependency_overrides[get_sensor_service] = lambda: mock_sensor_service

        response = client.get("/temperature")

        assert response.status_code == 503
        assert "message" in response.json()
        assert "No temperature data available" in response.json()["message"]

        app.dependency_overrides.clear()

    def test_get_temperature_sensebox_not_found(self, client, mock_sensor_service):
        """Test 404 error when senseBox is not found."""
        mock_sensor_service.average_temperature.side_effect = SenseBoxNotFoundError(
            "senseBox 'test-id' not found"
        )

        app.dependency_overrides[get_sensor_service] = lambda: mock_sensor_service

        response = client.get("/temperature")

        assert response.status_code == 404
        assert "message" in response.json()
        assert "not found" in response.json()["message"].lower()

        app.dependency_overrides.clear()

    def test_get_temperature_external_api_error(self, client, mock_sensor_service):
        """Test 502 error when OpenSenseMap API fails."""
        mock_sensor_service.average_temperature.side_effect = OpenSenseMapAPIError(
            "OpenSenseMap API error: 500"
        )

        app.dependency_overrides[get_sensor_service] = lambda: mock_sensor_service

        response = client.get("/temperature")

        assert response.status_code == 502
        assert "message" in response.json()
        assert "External API error" in response.json()["message"]

        app.dependency_overrides.clear()

    def test_get_temperature_error_response_format(self, client, mock_sensor_service):
        """Test that error responses follow the standard format."""
        mock_sensor_service.average_temperature.side_effect = NoTemperatureDataError(
            "Test error"
        )

        app.dependency_overrides[get_sensor_service] = lambda: mock_sensor_service

        response = client.get("/temperature")
        data = response.json()

        assert "message" in data
        assert isinstance(data["message"], str)

        app.dependency_overrides.clear()

    def test_get_temperature_different_values(self, client, mock_sensor_service):
        """Test endpoint with various temperature values."""
        test_values = [0.0, -5.5, 15.3, 30.0, 42.7]

        app.dependency_overrides[get_sensor_service] = lambda: mock_sensor_service

        for temp in test_values:
            mock_sensor_service.average_temperature.return_value = temp
            response = client.get("/temperature")

            assert response.status_code == 200
            assert response.json()["data"]["value"] == temp
            assert response.json()["data"]["unit"] == "°C"

        app.dependency_overrides.clear()

    def test_get_temperature_unsupported_unit_error(self, client, mock_sensor_service):
        """Test 500 error when temperature unit is not supported."""
        mock_sensor_service.average_temperature.side_effect = UnsupportedTemperatureUnitError(  # noqa: E501
            "Unsupported temperature unit '°F' for sensor sensor-123. Only °C is supported."  # noqa: E501
        )

        app.dependency_overrides[get_sensor_service] = lambda: mock_sensor_service

        response = client.get("/temperature")

        assert response.status_code == 500
        assert "message" in response.json()
        assert "Unsupported temperature unit" in response.json()["message"]
        assert "°F" in response.json()["message"]

        app.dependency_overrides.clear()
