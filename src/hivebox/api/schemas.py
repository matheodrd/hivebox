from pydantic import BaseModel


class SuccessResponse[T](BaseModel):
    data: T
