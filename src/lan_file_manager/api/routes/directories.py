from fastapi import APIRouter, Depends
from ...file_management.management_operations import FileManagement
from ...api.dependencies import return_file_management

router = APIRouter(prefix='/api/directories')

@router.get('/download')
async def download_directory_zip(
    file_management: FileManagement = Depends(return_file_management)
    ):
    pass

@router.post('/')
async def create_directory(
    file_management: FileManagement = Depends(return_file_management)
    ):
    pass