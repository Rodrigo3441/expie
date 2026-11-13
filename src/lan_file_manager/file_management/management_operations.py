import pathlib
from src.lan_file_manager.filesystem_access import directory_operations as filesystem_access

class FileManagement:
    def __init__(self, default_path: pathlib.Path):
        self.default_path = default_path.resolve()

    
    def is_requested_path_inside_root_path(self, requested_path: pathlib.Path):
        return requested_path.is_relative_to(self.default_path)


    def list_directory(self, requested_path_str: str) -> list[dict]:
        # convert api path into relative path
        if not requested_path_str.startswith('/'):
            raise ValueError('The requested path is not valid.')


        if len(requested_path_str) == 1:
            relative_requested_path_str = requested_path_str.replace('/', '.')
        else:
            relative_requested_path_str = requested_path_str.lstrip('/')

        
        relative_path = self.default_path / relative_requested_path_str
        relative_path = relative_path.resolve()

        if self.is_requested_path_inside_root_path(relative_path):
            if relative_path.exists():
                if relative_path.is_dir():
                    return filesystem_access.list_directory(relative_path)
                
                else:
                    raise NotADirectoryError('The requested path does not correspond to a directory.')
            else:
                raise FileNotFoundError('The requested path does not exist.')
        else:
            raise OSError('The requested path is outside the allowed path.')

        




        
