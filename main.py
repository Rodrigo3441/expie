from fastapi import FastAPI, APIRouter, Request
from contextlib import asynccontextmanager
from src.lan_file_manager.api.routes import (files, directories, downloads)
from src.lan_file_manager.api.exception_handlers import (
    handle_file_not_found,
    handle_not_a_directory,
    handle_permission_error,
    handle_is_a_directory,
    handle_value_error,
    handle_unexpected_exception,
    handle_file_exists_exception
)

import pathlib

from src.lan_file_manager.config.config import get_config
from src.lan_file_manager.file_management.management_operations import FileManagement

def load_default_path_config() -> pathlib.Path:
    config = get_config()
    return pathlib.Path(config['default_path'])

def load_default_chunk_size_config() -> int:
    config = get_config()
    return config['default_chunk_size']

default_path = load_default_path_config()
default_chunk_size = load_default_chunk_size_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # global variable for startup
    app.state.file_management = FileManagement(default_path, default_chunk_size)
    yield


app = FastAPI(lifespan=lifespan)

# include the api endpoints for the application
app.include_router(files.router)
app.include_router(directories.router)
app.include_router(downloads.router)

# include the exception handlers for the application
app.add_exception_handler(FileNotFoundError, handle_file_not_found)
app.add_exception_handler(NotADirectoryError, handle_not_a_directory)
app.add_exception_handler(PermissionError, handle_permission_error)
app.add_exception_handler(IsADirectoryError, handle_is_a_directory)
app.add_exception_handler(ValueError, handle_value_error)
app.add_exception_handler(Exception, handle_unexpected_exception)
app.add_exception_handler(FileExistsError, handle_file_exists_exception)





