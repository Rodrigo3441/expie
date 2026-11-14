import pathlib
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
        

        




        
