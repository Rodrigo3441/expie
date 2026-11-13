from fastapi import APIRouter, Depends
from ...file_management.management_operations import FileManagement
from ..dependencies import return_file_management

router = APIRouter(prefix='/api/files')

@router.get('/')
async def list_directory_content(
    file_management: FileManagement = Depends(return_file_management),
    path: str =  '/'
):
   try:
        data = file_management.list_directory(path)

        return {
            "success": True,
            "data": data,
            "error": None
        }
   except Exception as e:
        return {
            "success": False,
            "data": [],
            "error": e.args
        }


@router.post('/')
async def upload_files(
    file_management: FileManagement = Depends(return_file_management)
):
    pass

@router.get('/download')
async def download_file(
    file_management: FileManagement = Depends(return_file_management)
):
    pass

@router.patch('/')
async def rename_file(
    file_management: FileManagement = Depends(return_file_management)
):
    pass

@router.patch('/move')
async def move_file(
    file_management: FileManagement = Depends(return_file_management)
):
    pass

@router.delete('/')
async def delete_file(
    file_management: FileManagement = Depends(return_file_management)
):
    pass