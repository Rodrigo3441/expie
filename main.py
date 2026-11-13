from fastapi import FastAPI, APIRouter, Request
from contextlib import asynccontextmanager
from src.lan_file_manager.api.routes import (files, directories)

import pathlib

from src.lan_file_manager.config.config import get_config
from src.lan_file_manager.file_management.management_operations import FileManagement

def load_default_path_config() -> pathlib.Path:
    config = get_config()
    return pathlib.Path(config['default_path'])


default_path = load_default_path_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # global variable for startup
    app.state.file_management = FileManagement(default_path)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(files.router)
app.include_router(directories.router)

@app.get('/')
async def read_root(request: Request):
    return request.app.state.file_management.list_directory('/')




