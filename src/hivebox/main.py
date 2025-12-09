from typing import Callable, cast

from fastapi import FastAPI, HTTPException, Request, Response

from hivebox.api.exceptions import http_exception_handler
from hivebox.api.schemas import SuccessResponse
from hivebox.services.version import version

app = FastAPI(title="Hivebox")

# Weird trick here :
# I need to cast `http_exception_handler` because Pyright is rigid
# and wants a function with `Exception`, but I use `HTTPException` in mine.
ExceptionHandlerType = Callable[[Request, Exception], Response]

app.add_exception_handler(
    HTTPException, cast(ExceptionHandlerType, http_exception_handler)
)


@app.get("/version", response_model=SuccessResponse[str])
async def get_version() -> SuccessResponse[str]:
    return SuccessResponse(data=version())
