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
                "message": str(exc)
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
                "message": "The specified path is not a valid directory."
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
                "message": "Access denied. You don't have the required permissions to perform this operation."
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
                "message": str(exc)
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
                "message": str(exc)
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


async def handle_file_exists_exception(
        request: Request, 
        exc: FileExistsError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "RESOURCE_ALREADY_EXISTS",
                "message": str(exc)
            }
        }
    )

async def handle_os_error(
        request: Request,
        exc: OSError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "FILESYSTEM_ERROR",
                "message": "The requested filesystem operation could not be completed."
            }
        }
    )