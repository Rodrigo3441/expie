from fastapi import APIRouter, Depends
from ...file_management.management_operations import FileManagement
from ...api.dependencies import return_file_management

router = APIRouter(prefix='/api')


@router.post('/create')
def create_directory(
    name: str,
    path: str = '/',
    file_management: FileManagement = Depends(return_file_management)
    ):

    file_management.create_dir(path, name)

    return {
            "success": True,
            "data": None,
            "error": None
    }
