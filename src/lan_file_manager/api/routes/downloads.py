from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from ...file_management.management_operations import FileManagement
from ...api.dependencies import return_file_management
from ...config.config import get_config
import mimetypes
import os

router = APIRouter()
CHUNK_SIZE = get_config()['default_chunk_size']


def generate_file_chunks(requested_resource):
    with requested_resource.open('rb') as resource:
        while chunk := resource.read(CHUNK_SIZE):
            yield chunk


def remove_temp_zip_file(zip_file_path):
    os.remove(zip_file_path)


@router.get('/api/download', response_class=StreamingResponse)
def download_file(
    background_tasks: BackgroundTasks,
    file_management: FileManagement = Depends(return_file_management),
    path: str = '/'
    ):
    is_request_a_dir = file_management.is_requested_path_a_dir(path)

    filename = ''

    # if-else statement to handle the filename in case it is either a folder or a single file
    if is_request_a_dir:
        requested_resource = file_management.create_directory_zip(path)
        background_tasks.add_task(remove_temp_zip_file, requested_resource)
        content_type = 'application/zip'
        if path == '/':
            filename = 'download.zip' 
        else:
            filename = f'{path.rstrip('/').split('/')[-1]}.zip'
    else:
        requested_resource = file_management.open_file(path)
        filename = requested_resource.name
        content_type, _ = mimetypes.guess_type(filename)
        content_type = content_type or 'application/octet-stream'
        

    
    return StreamingResponse(
        generate_file_chunks(requested_resource),
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': content_type
        },
        background=background_tasks
    )

    