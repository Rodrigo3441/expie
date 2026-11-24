from pathlib import Path


def validate_absolute_path(path: Path) -> None:
    if not path.is_absolute():
        raise ValueError(
            f"The configured storage path must be absolute: {path}"
        )


def validate_no_symlinks(path: Path) -> None:
    current_path = Path(path.anchor)

    for part in path.parts[1:]:
        current_path = current_path / part

        if current_path.is_symlink():
            raise ValueError(
                f"The configured storage path cannot contain symbolic links: {current_path}"
            )

def validate_path_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"The configured storage path does not exist: {path}"
        )


def validate_is_directory(path: Path) -> None:
    if not path.is_dir():
        raise NotADirectoryError(
            f"The configured storage path is not a directory: {path}"
        )


def validate_storage_isolation(
    storage_path: Path,
    project_path: Path
) -> None:
    storage_path = storage_path.resolve()
    project_path = project_path.resolve()

    if (
        storage_path == project_path
        or storage_path.is_relative_to(project_path)
        or project_path.is_relative_to(storage_path)
    ):
        raise ValueError(
            "The configured storage path cannot be the project directory, "
            "one of its descendants, or one of its ancestors."
        )


def validate_storage_path(
    storage_path: Path,
    project_path: Path
) -> None:
    validate_absolute_path(storage_path)
    validate_no_symlinks(storage_path)
    validate_path_exists(storage_path)
    validate_is_directory(storage_path)
    validate_storage_isolation(storage_path, project_path)
