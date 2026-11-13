# File Management

## Purpose

Responsible for coordinating file and directory operations, enforcing application rules and ensuring all operations remain within the configured storage root.

## Responsibilities

- Validate paths and enforce storage boundaries.
- Coordinate directory listing and metadata retrieval.
- Coordinate file uploads and downloads.
- Create, rename, move and delete files and directories.
- Generate ZIP archives for directory downloads.
- Handle filename conflicts and overwrite policies.
- Interpret filesystem errors and report operation results.

## Uploads and Downloads

- Use streaming to avoid loading entire files into memory.
- Store incomplete uploads in unique, hidden temporary files inside the destination directory.
- Finalize uploads only after successful completion.
- Preserve existing files until replacement uploads are complyreaete.
- Clean up incomplete uploads.

## Conflict Handling

When a destination filename already exists, allow the user to:

- Overwrite the existing file.
- Keep both files using an available filename.
- Cancel or skip the operation.

Batch operations may partially succeed.

## Operation Results

Initial result statuses:

- `SUCCESS`
- `PARTIAL_SUCCESS`
- `FAILURE`

Results should include relevant successful operations, failed entries and error information.

## Responsibilities outside this component

- Handling HTTP requests and responses.
- Managing frontend interactions and confirmation dialogs.
- Performing low-level Linux filesystem operations.
- Loading configuration files.

## Design Decisions

- All operations must remain within the configured storage root.
- Filesystem Access performs actual filesystem operations.
- File Management enforces application-level rules.
- Deletion is permanent and requires user confirmation.
- Batch operations allow partial success.
- Additional result statuses may be introduced when necessary.