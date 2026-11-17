import pathlib
import io
import os
import zipfile
import tempfile
from src.lan_file_manager.filesystem_access import directory_operations as filesystem_access

CHUNK_SIZE = 1024 * 1024

class FileManagement:
    def __init__(self, default_path: pathlib.Path):
        self.default_path = default_path.resolve()

    
    def __is_requested_path_inside_root_path(self, requested_path: pathlib.Path) -> bool:
        return requested_path.is_relative_to(self.default_path)

    def __resolve_path_name(self, relative_path: str) -> pathlib.Path:
        relative_path = self.default_path / relative_path
        return relative_path.resolve()

    def is_requested_path_a_dir(self, path: str) -> bool:
        '''
        Checks whether the requested path points to a directory within the allowed storage root.
        '''
        if not path.startswith('/'):
            raise ValueError('The requested path is not valid.')

        relative_path = self.__convert_path_name_into_relative(path)
        resolved_path = self.__resolve_path_name(relative_path)

        if not self.__is_requested_path_inside_root_path(resolved_path):
            raise PermissionError('The requested path is outside the allowed path.')

        if not resolved_path.exists():
            raise FileNotFoundError('The requested path could not be found.')

        return resolved_path.is_dir()


    def __convert_path_name_into_relative(self, requested_path_str: str) -> str:
        """
        Check whether a path string points to the root directory or not
        It also removes the leading slash (/)
        """
        if len(requested_path_str) == 1:
            relative_requested_path_str = requested_path_str.replace('/', '.')
        else:
            relative_requested_path_str = requested_path_str.lstrip('/')

        return relative_requested_path_str


    def list_directory(self, requested_path_str: str) -> list[dict]:
        """
        Lists the contents of a directory inside the configured storage root.

        Validates the requested API path, resolves it to an absolute
        filesystem path, and ensures it remains within the allowed root
        before delegating the directory listing to Filesystem Access.

        Args:
        requested_path_str: Directory path relative to the storage root,
            using the API path format (e.g. '/', '/Photos').

        Returns:
        A list of dictionaries containing the directory entries' metadata.

        Raises:
        ValueError: If the requested path does not follow the API path format.
        FileNotFoundError: If the requested directory does not exist.
        NotADirectoryError: If the requested path is not a directory.
        PermissionError: If the requested path is outside the storage root.
        """
        if not requested_path_str.startswith('/'):
            raise ValueError('The requested path is not valid.')
        
        relative_requested_path_str = self.__convert_path_name_into_relative(requested_path_str)
        
        resolved_path = self.__resolve_path_name(relative_requested_path_str)

        if self.__is_requested_path_inside_root_path(resolved_path):
            if resolved_path.exists():
                if resolved_path.is_dir():
                    return filesystem_access.list_directory(resolved_path)
                
                else:
                    raise NotADirectoryError('The requested path does not correspond to a directory.')
            else:
                raise FileNotFoundError('The requested path does not exist.')
        else:
            raise PermissionError('The requested path is outside the allowed path.')


    def upload_file(
            self,
            file_stream,
            destination_dir: str,
            filename: str
    ) -> None:
        """
        Upload a file into the configured storage directory.

        Validates the destination path and filename, creates missing
        destination directories, and streams the uploaded content into
        a temporary file.

        Once the upload completes, the temporary file replaces the
        destination file. Existing files are automatically overwritten.

        If the upload fails, the temporary file is removed, preserving
        any previously existing destination file.

        Args:
            file_stream: Binary stream containing the uploaded file.
            destination_dir: Destination directory relative to the storage root.
            filename: Name of the uploaded file.

        Raises:
            ValueError: If the destination path or filename is invalid.
            PermissionError: If the destination is outside the storage root.
            NotADirectoryError: If the destination path is not a directory.
            IsADirectoryError: If the destination filename already refers to a directory.
            OSError: If a filesystem operation fails.
        """
        if not destination_dir.startswith('/'):
            raise ValueError('The requested path is not valid.')

        if not filename or '/' in filename or '\\' in filename:
            raise ValueError('The filename is invalid.')


        relative_requested_path_str = self.__convert_path_name_into_relative(destination_dir)

        resolved_path = self.__resolve_path_name(relative_requested_path_str)

        if self.__is_requested_path_inside_root_path(resolved_path):
            if not resolved_path.exists():
                filesystem_access.create_directory(resolved_path)

                
            if not resolved_path.is_dir():
                raise NotADirectoryError('The destination path is not a directory.')

            filename_destination = resolved_path / filename

            if filename_destination.exists() and filename_destination.is_dir():
                raise IsADirectoryError('This file cannot be uploaded.')


            if self.__is_requested_path_inside_root_path(filename_destination):
                temp_file_path = filesystem_access.create_temp_file(resolved_path)

                try:
                    while True:
                        chunk = file_stream.read(CHUNK_SIZE)
                        if not chunk:
                            break

                        filesystem_access.write_to_temp_file(temp_file_path, chunk)

                    filesystem_access.finalize_upload(temp_file_path, filename_destination)
                    
                except Exception:
                    filesystem_access.delete_temp_file(temp_file_path)
                    raise 

            else:
                raise PermissionError('The requested file destination path is outside the allowed path.')
        else:
            raise PermissionError('The requested path is outside the allowed path.')
        

    def open_file(self, path: str) -> pathlib.Path:
        """
        Validates the requested path and returns the file's resolved path.
        Raises an exception if the path is invalid, outside the allowed directory,
        does not exist, or points to a directory.
        """
        if not path.startswith('/'):
            raise ValueError('The requested path is not valid.')
        
        relative_requested_path_str = self.__convert_path_name_into_relative(path)
        
        resolved_path = self.__resolve_path_name(relative_requested_path_str)

        if not self.__is_requested_path_inside_root_path(resolved_path):
            raise PermissionError('The requested path is outside the allowed path.')
        
        if not resolved_path.exists():
            raise FileNotFoundError('The requested file could not be found.')
        
        if resolved_path.is_dir():
            raise IsADirectoryError('The requested file is actually a directory.')

                
        return resolved_path


    def create_directory_zip(self, path: str) -> pathlib.Path:
        """
        Validates the requested directory and creates a temporary ZIP archive
        containing its contents. Returns the path to the generated ZIP file.
        """
        if not path.startswith('/'):
            raise ValueError('The requested path is not valid.')
        
        relative_requested_path_str = self.__convert_path_name_into_relative(path)
                
        resolved_path = self.__resolve_path_name(relative_requested_path_str)

        if not self.__is_requested_path_inside_root_path(resolved_path):
            raise PermissionError('The requested folder is outside the allowed path.')

        if not resolved_path.exists():
            raise FileNotFoundError('The requested folder could not be found.')

        if not resolved_path.is_dir():
            raise NotADirectoryError('The requested path is not a directory.')

        temp_zip_file = tempfile.NamedTemporaryFile(mode='w+b', suffix='.zip', delete=False, dir=tempfile.gettempdir())
        temp_zip_path = pathlib.Path(temp_zip_file.name)
        temp_zip_file.close()

        try:
            with zipfile.ZipFile(file=temp_zip_path, mode='w', allowZip64=True) as zip_file:
                for file_path in resolved_path.rglob('*'):
                    zip_file.write(file_path, arcname=file_path.relative_to(resolved_path))

        except Exception:
            os.remove(temp_zip_path)
            raise 

        return temp_zip_path


    def create_dir(self, path: str, name: str) -> None:
        """
        Creates a new directory inside an existing folder after validating
        the directory name and ensuring the destination is inside the configured storage root.
        """
        if not path.startswith('/'):
            raise ValueError('The requested path is not valid.')

        if not name:
            raise ValueError('The folder name cannot be empty.')

        if '/' in name or name in ('.','..') or '\\' in name:
            raise ValueError('The folder name is invalid.')


        relative_requested_path_str = self.__convert_path_name_into_relative(path)
        resolved_path = self.__resolve_path_name(relative_requested_path_str)

        if not resolved_path.exists():
            raise FileNotFoundError('The current path does not exist.')

        if not resolved_path.is_dir():
            raise NotADirectoryError('The current path is not a folder.')

        final_folder_path = resolved_path / name
        final_resolved_path = self.__resolve_path_name(final_folder_path)
    
        if not self.__is_requested_path_inside_root_path(final_resolved_path):
            raise PermissionError('The requested path for folder creation is outside the allowed path.')
        
        filesystem_access.create_directory(final_resolved_path)


    def delete_resource(self, path: str, name: str) -> None:
        """
        Deletes a file or directory after validating the requested path
        and ensuring the resource is inside the configured storage root.
        """
        if not path.startswith('/'):
            raise ValueError('The requested path is not valid.')

        relative_requested_path_str = self.__convert_path_name_into_relative(path)     
        resolved_path = self.__resolve_path_name(relative_requested_path_str)

        if not resolved_path.exists():
            raise FileNotFoundError('The current path does not exist.')

        if not resolved_path.is_dir():
            raise NotADirectoryError('The current path is not a folder.')

        if name is None:
            final_resolved_path = resolved_path
        else:
            if '/' in name or '\\' in name or name in ('.','..'):
                raise ValueError('The filename is invalid.')
            
            final_resolved_path = self.__resolve_path_name(resolved_path / name)

        if final_resolved_path == self.default_path:
            raise PermissionError('Cannot delete the storage root directory.')

        if not self.__is_requested_path_inside_root_path(final_resolved_path):
            raise PermissionError('The requested folder is outside the allowed path.')

        if not final_resolved_path.exists():
            raise FileNotFoundError('The requested folder could not be found.')

        if final_resolved_path.is_dir():
            filesystem_access.delete_directory(final_resolved_path)
        else:
            filesystem_access.delete_file(final_resolved_path)