from fastapi import FastAPI, APIRouter, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
from src.lan_file_manager.api.routes import (files, directories, downloads, error_pages)
from src.lan_file_manager.api.dependencies import return_file_management
from src.lan_file_manager.initialization.validation import validate_storage_path
from src.lan_file_manager.api.exception_handlers import (
    handle_file_not_found,
    handle_not_a_directory,
    handle_permission_error,
    handle_is_a_directory,
    handle_value_error,
    handle_unexpected_exception,
    handle_file_exists_exception,
    handle_os_error
)

import pathlib
import sys

from src.lan_file_manager.config.config import get_config
from src.lan_file_manager.file_management.management_operations import FileManagement

# avoids tracebacks on console
sys.tracebacklimit = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()

    default_path = pathlib.Path(config['default_path'])
    default_chunk_size = config['default_chunk_size']
    default_project_path = pathlib.Path(__file__).resolve().parent

    validate_storage_path(default_path, default_project_path)
    app.state.templates = templates
    app.state.file_management = FileManagement(default_path, default_chunk_size)
    yield

# including the html page resources
BASE_DIR = pathlib.Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / 'src' / 'lan_file_manager' / 'frontend'

app = FastAPI(lifespan=lifespan, openapi_url=None)

app.mount(
    '/static',
    StaticFiles(directory=FRONTEND_DIR / 'static'),
    name='static'
)

templates = Jinja2Templates(directory=FRONTEND_DIR / 'templates')


# include the api endpoints for the application
app.include_router(files.router)
app.include_router(directories.router)
app.include_router(downloads.router)
app.include_router(error_pages.router)

# include the exception handlers for the application
app.add_exception_handler(FileNotFoundError, handle_file_not_found)
app.add_exception_handler(NotADirectoryError, handle_not_a_directory)
app.add_exception_handler(PermissionError, handle_permission_error)
app.add_exception_handler(IsADirectoryError, handle_is_a_directory)
app.add_exception_handler(ValueError, handle_value_error)
app.add_exception_handler(Exception, handle_unexpected_exception)
app.add_exception_handler(FileExistsError, handle_file_exists_exception)
app.add_exception_handler(OSError, handle_os_error)

@app.get('/', response_class=HTMLResponse)
@app.get('/{path:path}', response_class=HTMLResponse)
async def serve_frontend(
    request: Request, 
    path: str = '',
    file_management: FileManagement = Depends(return_file_management)
):

    requested_path = '/' + path

    try:
        if file_management.is_requested_path_a_dir(requested_path):
            return templates.TemplateResponse(
                request=request,
                name='index.html',
                context={}
            )

        requested_path = file_management.open_file(requested_path)
        return FileResponse(requested_path)

    except FileNotFoundError:
        return templates.TemplateResponse(
            request=request,
            name='404.html',
            context={},
            status_code=404
        )

