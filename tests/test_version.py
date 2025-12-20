"""Unit tests for version module and endpoint."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from hivebox.main import app
from hivebox.services.version import version


class TestVersionFunction:
    """Tests for the version() function."""

    def test_version_not_empty(self):
        """Test that version() does not return an empty string."""
        result = version()
        assert len(result) > 0

    @patch("hivebox.services.version.importlib.metadata.version")
    def test_version_with_mocked_metadata(self, mock_version):
        """Test version() with mocked metadata."""
        mock_version.return_value = "1.2.3"
        result = version()
        assert result == "1.2.3"
        mock_version.assert_called_once_with("hivebox")


class TestVersionEndpoint:
    """Tests for the /version endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_get_version_returns_200(self, client):
        """Test that GET /version returns HTTP 200."""
        response = client.get("/version")
        assert response.status_code == 200

    def test_get_version_response_format(self, client):
        """Test that GET /version returns correct response format."""
        response = client.get("/version")
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], str)
        assert len(data["data"]) > 0

    @patch("hivebox.main.version")
    def test_get_version_returns_correct_version(self, mock_version, client):
        """Test that endpoint returns the version from version()."""
        mock_version.return_value = "2.3.4"
        response = client.get("/version")
        assert response.json() == {"data": "2.3.4"}

    def test_get_version_multiple_calls_consistent(self, client):
        """Test that multiple calls to /version return consistent results."""
        response1 = client.get("/version")
        response2 = client.get("/version")
        assert response1.json() == response2.json()
