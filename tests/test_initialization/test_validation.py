import pytest
from pathlib import Path

from src.lan_file_manager.initialization.validation import (
    validate_absolute_path,
    validate_no_symlinks,
    validate_path_exists,
    validate_is_directory,
    validate_storage_isolation,
    validate_storage_path,
)


def test_validate_absolute_path_accepts_absolute_path(tmp_path):
    validate_absolute_path(tmp_path)


def test_validate_absolute_path_rejects_relative_path():
    with pytest.raises(ValueError):
        validate_absolute_path(Path("storage"))


def test_validate_no_symlinks_accepts_normal_path(tmp_path):
    storage_path = tmp_path / "storage"
    storage_path.mkdir()

    validate_no_symlinks(storage_path)


def test_validate_no_symlinks_rejects_symlink(tmp_path):
    storage_path = tmp_path / "storage"
    storage_path.mkdir()

    symlink_path = tmp_path / "storage_link"
    symlink_path.symlink_to(storage_path)

    with pytest.raises(ValueError):
        validate_no_symlinks(symlink_path)


def test_validate_no_symlinks_rejects_parent_symlink(tmp_path):
    real_parent = tmp_path / "real"
    real_parent.mkdir()

    storage_path = real_parent / "storage"
    storage_path.mkdir()

    symlink_parent = tmp_path / "linked"
    symlink_parent.symlink_to(real_parent, target_is_directory=True)

    with pytest.raises(ValueError):
        validate_no_symlinks(symlink_parent / "storage")


def test_validate_path_exists_accepts_existing_path(tmp_path):
    validate_path_exists(tmp_path)


def test_validate_path_exists_rejects_missing_path(tmp_path):
    missing_path = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        validate_path_exists(missing_path)


def test_validate_is_directory_accepts_directory(tmp_path):
    validate_is_directory(tmp_path)


def test_validate_is_directory_rejects_file(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.touch()

    with pytest.raises(NotADirectoryError):
        validate_is_directory(file_path)


def test_validate_storage_isolation_accepts_separate_directory(tmp_path):
    project_path = tmp_path / "expie"
    storage_path = tmp_path / "storage"

    project_path.mkdir()
    storage_path.mkdir()

    validate_storage_isolation(storage_path, project_path)


@pytest.mark.parametrize("storage_location", ["same", "inside", "outside"])
def test_validate_storage_isolation_rejects_project_overlap(
    tmp_path,
    storage_location
):
    project_path = tmp_path / "expie"
    project_path.mkdir()

    if storage_location == "same":
        storage_path = project_path
    elif storage_location == "inside":
        storage_path = project_path / "storage"
        storage_path.mkdir()
    else:
        storage_path = tmp_path

    with pytest.raises(ValueError):
        validate_storage_isolation(storage_path, project_path)


def test_validate_storage_path_accepts_valid_configuration(tmp_path):
    project_path = tmp_path / "expie"
    storage_path = tmp_path / "storage"

    project_path.mkdir()
    storage_path.mkdir()

    validate_storage_path(storage_path, project_path)


def test_validate_storage_path_rejects_project_directory(tmp_path):
    project_path = tmp_path / "expie"
    project_path.mkdir()

    with pytest.raises(ValueError):
        validate_storage_path(project_path, project_path)
