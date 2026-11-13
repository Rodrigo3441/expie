import pathlib

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
