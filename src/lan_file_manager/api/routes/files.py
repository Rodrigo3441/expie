from fastapi import APIRouter, Depends, UploadFile, File
from ...file_management.management_operations import FileManagement
from ..dependencies import return_file_management
from pydantic import BaseModel

router = APIRouter()

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
 


@router.post('/api/upload')
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


@router.patch('/api/rename')
def rename_file(
    path: str,
    old_name: str,
    new_name: str,
    file_management: FileManagement = Depends(return_file_management)
):
    file_management.rename_resource(path, old_name, new_name)

    return {
        "success": True,
        "data": None,
        "error": None
    }


@router.patch('/api/move')
def move_resource(
    source_path: str,
    destination_path: str,
    file_management: FileManagement = Depends(return_file_management)
):
    file_management.move_resource(source_path, destination_path)

    return {
        "success": True,
        "data": None,
        "error": None
    }


@router.delete('/api/delete')
def delete_file(
    path: str,
    name: str | None = None,
    file_management: FileManagement = Depends(return_file_management)
):

    file_management.delete_resource(path, name)

    return {
            "success": True,
            "data": None,
            "error": None
    }