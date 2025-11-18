from typing import Final

from fastapi import Request
from fastapi.responses import JSONResponse


class ServiceError(Exception):
    """Base exception for all service-layer errors."""

    status_code: Final[int] = 400

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.__doc__)

    @property
    def message(self) -> str:
        return self.__doc__ or ""


class TopicNotFoundError(ServiceError):
    """Topic not found, it may be expired."""

    status_code: Final[int] = 404


class ForbiddenActionError(ServiceError):
    """Only topic admin can perform this action."""

    status_code: Final[int] = 403


def exception_handler(request: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
