# API Architecture

## Purpose

Responsible for receiving HTTP requests from the Web Interface, validating request structures, communicating with File Management, and returning appropriate HTTP responses.

## Responsibilities

- Receive HTTP requests.
- Validate request structure, required fields, and data types.
- Forward operations to File Management.
- Translate operation results into HTTP responses.
- Handle HTTP-specific errors and status codes.
- Stream file uploads and downloads.

## Communication

- REST API over HTTP.
- JSON for standard requests and responses.
- Multipart form data for file uploads.
- Streaming for file downloads.
- Direct function or class calls to communicate with File Management.

## Resource Identification

- Files and directories are identified by paths relative to the configured storage root.
- The actual server filesystem paths must never be exposed to the browser.
- Path validation and storage boundary enforcement belong to File Management.
- The virtual root path `/` represents the configured storage directory.

## Standard JSON Response

Ordinary JSON responses follow this structure:

```json
{
    "success": true,
    "data": {},
    "error": null
}
```

| Field | Description |
|---|---|
| `success` | Indicates whether the operation succeeded completely. |
| `data` | Contains the operation result, or `null` if there is no result. |
| `error` | Contains error details, or `null` if successful. |

For errors:

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "RESOURCE_NOT_FOUND",
        "message": "The requested resource does not exist."
    }
}
```

HTTP status codes remain authoritative. The JSON structure complements them.

File streaming responses do not follow this JSON structure.

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/contents` | List directory contents. |
| POST | `/api/upload` | Upload files and directories. |
| GET | `/api/download` | Download a file or a directory. |
| POST | `/api/create` | Create a directory. |
| PATCH | `/api/rename` | Rename a file or directory. |
| PATCH | `/api/move` | Move files or directories. |
| DELETE | `/api/delete` | Delete files or directories. |

### Directory Listing

`GET /api/contents`

- Optional query parameter: `path`.
- Without a path, lists the configured storage root.
- Returns directory entries and their metadata.
- Internal filesystem paths are never exposed.

Example:

`GET api/contents?path=/Movies`

### File and Directory Upload

`POST /api/upload`

- Receives files using multipart form data.
- Processes one file per HTTP request.
- The frontend can initiate multiple requests for directory uploads.
- Uses relative destination paths to reconstruct directory structures.
- Automatically creates missing destination directories.
- Existing files with the same name are automatically replaced.
- Existing directories are merged rather than replaced.
- Files not included in the upload remain untouched.
- File and directory name conflicts are rejected.
- Empty directories are created separately using the directory creation endpoint.

### File and Directory Download

`GET /api/download`

- Receives a resource path through the `path` query parameter.
- If the requested resource is a file, streams the file directly.
- If the requested resource is a directory, generates a ZIP archive.
- ZIP archives preserve the directory structure.
- Returns appropriate content types and download headers.
- Temporary ZIP files are removed after the response finishes.

Examples:

`GET /api/download?path=/Movies/movie.mp4`

`GET /api/download?path=/Movies/Action`

### Directory Creation

`POST /api/create`

- Receives the parent directory path and new directory name.
- Creates one directory per request.
- Existing directories are accepted without creating duplicates.

Example:

`POST /api/create?path=/Movies&name=Documentaries`

### Rename

`PATCH /api/rename`

- Receives the parent directory path, current resource name, and new resource name.
- Supports both files and directories.
- Rejects renaming when the destination name already exists.
- Renaming a resource to its current name is treated as a no-op.

Example:

`PATCH /api/rename?path=/Movies&old_name=movie.mp4&new_name=favorite-movie.mp4`

### Move

`PATCH /api/move`

- Receives the source resource path and destination directory path.
- Supports both files and directories.
- Preserves the original resource name.
- Rejects moves when the destination already contains a resource with the same name.
- Prevents moving a directory into itself or one of its subdirectories.
- The configured storage root cannot be moved.

Example:

`PATCH /api/move?source_path=/Movies/movie.mp4&destination_path=/Backups`

### Delete

`DELETE /api/delete`

- Supports deleting individual files and directories.
- Directory deletion is recursive, including non-empty directories.
- Deletion is permanent.
- The configured storage root cannot be deleted.
- User confirmation is handled by the Web Interface.

Example:

`DELETE /api/delete?path=/Movies&name=movie.mp4`

## Filename Conflict Handling

The current conflict policy is:

| Situation | behavior |
|---|---|
| Uploading a file with an existing filename | Automatically overwrite the existing file. |
| Uploading into an existing directory | Merge directory contents. |
| File conflicts with a directory | Reject the operation. |
| Directory conflicts with a file | Reject the operation. |
| Renaming to an existing resource name | Reject the operation. |
| Moving into a directory containing the same resource name | Reject the operation. |

File Management is responsible for validating conflicts and enforcing these policies.

## HTTP Status Codes

| Status | Meaning |
|---|---|
| `200 OK` | Successful operation. |
| `400 Bad Request` | Invalid request parameters, invalid values, or resource conflicts. |
| `403 Forbidden` | Operation not permitted. |
| `404 Not Found` | Requested resource does not exist. |
| `500 Internal Server Error` | Unexpected server error. |

File transfer errors are also translated into appropriate HTTP responses.

## Responsibilities Outside This Component

- Implementing application business rules.
- Enforcing storage boundaries.
- Handling filename conflict policies.
- Performing direct filesystem operations.
- Managing frontend interactions and confirmation dialogs.
- Loading configuration files.

## Design Decisions

- REST over HTTP.
- Action-oriented endpoint organization.
- Relative filesystem paths as resource identifiers.
- Standard JSON response structure for ordinary API responses.
- Streaming for file transfers.
- One resource per download request.
- One file per upload request.
- Direct communication with File Management.
- API validation is limited to request structure and data types.
- File Management handles application-level validation and rules.
