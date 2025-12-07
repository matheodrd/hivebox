"""Unit tests for version module and endpoint."""

from unittest.mock import patch

from hivebox.version import version


class TestVersionFunction:
    """Tests for the version() function."""

    def test_version_not_empty(self):
        """Test that version() does not return an empty string."""
        result = version()
        assert len(result) > 0

    @patch("hivebox.version.importlib.metadata.version")
    def test_version_with_mocked_metadata(self, mock_version):
        """Test version() with mocked metadata."""
        mock_version.return_value = "1.2.3"
        result = version()
        assert result == "1.2.3"
        mock_version.assert_called_once_with("hivebox")
