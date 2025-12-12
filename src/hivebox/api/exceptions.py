from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with custom format and centralised logging (well, not yet)."""
    # TODO: Add logging here when implementing logging system

    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
