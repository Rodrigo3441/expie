from fastapi import Request
from fastapi.responses import JSONResponse


async def handle_file_not_found(
        request: Request,
        exc: FileNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "The requested resource does not exist."
            }
        }
    )


async def handle_not_a_directory(
        request: Request,
        exc: NotADirectoryError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "NOT_A_DIRECTORY",
                "message": "The requested resource is not a directory."
            }
        }
    )


async def handle_permission_error(
        request: Request,
        exc: PermissionError
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "FORBIDDEN",
                "message": "The requested resource could not be accessed."
            }
        }
    )


async def handle_is_a_directory(
        request: Request,
        exc: IsADirectoryError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "NOT_A_FILE",
                "message": "It was expected a file."
            }
        }
    )


async def handle_value_error(
        request: Request,
        exc: ValueError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INVALID_VALUE",
                "message": "The received value does not match the expected entry."
            }
        }
    )


async def handle_unexpected_exception(
        request: Request,
        exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred."
            }
        }
    )