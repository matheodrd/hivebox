from typing import Callable, cast

from fastapi import FastAPI, Depends, HTTPException, Request, Response

from hivebox.api.exceptions import http_exception_handler
from hivebox.api.schemas import SuccessResponse
from hivebox.clients.opensensemap.interface import OpenSenseMapClient
from hivebox.clients.opensensemap.http import (
    OpenSenseMapHTTP,
    SenseBoxNotFoundError,
    OpenSenseMapAPIError,
)
from hivebox.services.version import version
from hivebox.services.sensor import SensorService, NoTemperatureDataError

SENSE_BOX_IDS = [
    "59592d0994f05200114428e8",
    "5f745eb5821102001b03fc8b",
    "5fb7de317a70a5001c6af2da",
]

app = FastAPI(title="Hivebox")

# Weird trick here :
# I need to cast `http_exception_handler` because Pyright is rigid
# and wants a function with `Exception`, but I use `HTTPException` in mine.
ExceptionHandlerType = Callable[[Request, Exception], Response]

app.add_exception_handler(
    HTTPException, cast(ExceptionHandlerType, http_exception_handler)
)


def get_opensensemap_client() -> OpenSenseMapClient:
    return OpenSenseMapHTTP()


def get_sensor_service(client=Depends(get_opensensemap_client)) -> SensorService:
    return SensorService(
        opensensemap_client=client,
        sense_box_ids=SENSE_BOX_IDS,
    )


@app.get("/version")
async def get_version() -> SuccessResponse[str]:
    return SuccessResponse(data=version())


@app.get("/temperature")
async def get_temperature(
    sensor: SensorService = Depends(get_sensor_service),
) -> SuccessResponse[float]:
    try:
        temp = await sensor.average_temperature()
        return SuccessResponse(data=temp)
    except NoTemperatureDataError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except SenseBoxNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OpenSenseMapAPIError as e:
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")
