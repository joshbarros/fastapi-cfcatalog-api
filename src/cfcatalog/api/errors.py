from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from cfcatalog.services.exceptions import InvalidReferenceError, NotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(InvalidReferenceError)
    async def invalid_reference_handler(_: Request, exc: InvalidReferenceError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
