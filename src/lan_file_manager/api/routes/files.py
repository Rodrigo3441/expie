from fastapi import APIRouter, Depends, UploadFile, File
from ...file_management.management_operations import FileManagement
from ..dependencies import return_file_management
from pydantic import BaseModel

router = APIRouter(prefix='/api/files')

class ResponseModel(BaseModel):
    success: bool
    data: list[dict] | None
    error: dict | None


@router.get('/', response_model=ResponseModel)
def list_directory_content(
    file_management: FileManagement = Depends(return_file_management),
    path: str =  '/'
):

    data = file_management.list_directory(path)

    return {
        "success": True,
        "data": data,
        "error": None
    }
 


@router.post('/')
def upload_file(
    file_management: FileManagement = Depends(return_file_management),
    file: UploadFile = File(...),
    path: str = '/'
):
    try:
        file_management.upload_file(file.file, path, file.filename)
        file.close()
        
    finally:
        file.close()

    return {
            "success": True,
            "data": None,
            "error": None
    }


@router.patch('/')
def rename_file(
    file_management: FileManagement = Depends(return_file_management)
):
    pass

@router.patch('/move')
def move_file(
    file_management: FileManagement = Depends(return_file_management)
):
    pass

@router.delete('/')
def delete_file(
    file_management: FileManagement = Depends(return_file_management)
):
    pass