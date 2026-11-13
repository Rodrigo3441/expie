from fastapi import Request
from src.lan_file_manager.file_management.management_operations import FileManagement

def return_file_management(request: Request) -> FileManagement:
    return request.app.state.file_management