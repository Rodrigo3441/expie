import pathlib
from tempfile import NamedTemporaryFile


# ======================================
# Listing directories operations
# ======================================
def list_directory(folder_path: pathlib.Path) -> list[dict]:
    """
    List the contents of a directory.

    Args:
        folder_path (pathlib.Path): The path of the directory to list.

    Returns:
        list[dict]: A list of dictionaries containing information about each item in the directory.
    """

    directory_contents = []
    for item in folder_path.iterdir():
        item_metadata = item.stat()

        item_info = {
            'name': item.name,
            'type': 'DIRECTORY' if item.is_dir() else 'FILE',
            'extension': item.suffix if item.is_file() else None,
            'size': item_metadata.st_size if item.is_file() else None,
            'modified_at': item_metadata.st_mtime
        }
        directory_contents.append(item_info)

    return directory_contents

# ======================================
# Uploading files operations
# ======================================
def create_directory(folder_path: pathlib.Path) -> None:
    """
    Create a directory within a specified path

    Args:
        folder_path (pathlib.Path): The path of the directory to create

    """
    folder_path.mkdir(parents=True, exist_ok=True)


def create_temp_file(destination_dir: pathlib.Path) -> pathlib.Path:
    """
    Create a temporary file for the uploaded file before replacing the original one
    """
    with NamedTemporaryFile(
        mode='w+b',
        suffix='.tmp',
        dir=destination_dir,
        delete=False
    ) as temp:
        temp_path = pathlib.Path(temp.name)

    return temp_path


def write_to_temp_file(temp_path: pathlib.Path, chunk: bytes) -> None:
    """
    Write a chunck of bytes to the temporary file
    """
    with temp_path.open('r+b') as temp_file:
        temp_file.seek(0, 2)
        temp_file.write(chunk)


def finalize_upload(
    temp_path: pathlib.Path,
    destination_path: pathlib.Path
) -> None:
    """
    Renames the file to the final one
    """
    temp_path.replace(destination_path)


def delete_temp_file(temp_path: pathlib.Path) -> None:
    temp_path.unlink()


# ======================================
# Download operations
# ======================================