## Decision D-01 — Storage configuration
The application will have one configured root directory.

## Decision D-02 — Permanent deletion.
When a user deletes a file or directory:
- The item will be permanently removed.
- The interface must request confirmation before deletion.
- Deleting a non-empty directory must also be supported, with an appropriate warning.

## Decision D-03 — Large-file upload support.
- Large files, not just small documents.
- Temporary storage while uploads are in progress.
- Proper cleanup of incomplete uploads.
- Error handling for insufficient disk space and interrupted connections.

## Decision D-04 — Non-resumable uploads for the project.
If an upload is interrupted:
1. The upload is considered unsuccessful.
2. The incomplete temporary file is removed.
3. The user must initiate the upload again.
4. The original destination file, if one exists, remain intact.

## Out of scope

- Search bar functionality
- Resumable download and upload