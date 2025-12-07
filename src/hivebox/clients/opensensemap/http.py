import httpx

from hivebox.clients.opensensemap.schemas import (
    SenseBox,
    SensorsMeasurement,
    new_sense_box,
    new_sensors_measurement,
)


class OpenSenseMapError(Exception):
    """Base exception for OpenSenseMap client errors."""

    pass


class SenseBoxNotFoundError(OpenSenseMapError):
    """Raised when a senseBox is not found."""

    pass


class OpenSenseMapAPIError(OpenSenseMapError):
    """Raised when OpenSenseMap API returns an error."""

    pass


class OpenSenseMapHTTP:
    def __init__(self, base_url: str = "https://api.opensensemap.org") -> None:
        self.client = httpx.AsyncClient(base_url=base_url)

    async def get_sense_box(self, sense_box_id: str) -> SenseBox:
        """Get a senseBox from OpenSenseMap API.

        Args:
            sense_box_id: The ID of the senseBox to get

        Returns:
            A SenseBox object containing the senseBox data

        Raises:
            SenseBoxNotFoundError: If the senseBox is not found (404)
            OpenSenseMapAPIError: If the API request fails
        """
        try:
            response = await self.client.get(f"/boxes/{sense_box_id}")
            response.raise_for_status()
            return new_sense_box(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SenseBoxNotFoundError(
                    f"senseBox '{sense_box_id}' not found"
                ) from e
            raise OpenSenseMapAPIError(
                f"OpenSenseMap API error: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            raise OpenSenseMapAPIError(
                f"Failed to connect to OpenSenseMap API: {e}"
            ) from e

    async def get_sensors_measurement(self, sense_box_id: str) -> SensorsMeasurement:
        """Get sensors measurement from OpenSenseMap API.

        Args:
            sense_box_id: The ID of the senseBox to get sensors for

        Returns:
            A SensorsMeasurement object containing the sensors data

        Raises:
            SenseBoxNotFoundError: If the senseBox is not found (404)
            OpenSenseMapAPIError: If the API request fails
        """
        try:
            response = await self.client.get(f"/boxes/{sense_box_id}/sensors")
            response.raise_for_status()
            return new_sensors_measurement(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SenseBoxNotFoundError(
                    f"senseBox '{sense_box_id}' not found"
                ) from e
            raise OpenSenseMapAPIError(
                f"OpenSenseMap API error: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            raise OpenSenseMapAPIError(
                f"Failed to connect to OpenSenseMap API: {e}"
            ) from e
