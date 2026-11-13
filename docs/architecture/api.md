# API Architecture

## Purpose

Responsible for receiving HTTP requests from the Web Interface, validating request structures, communicating with File Management and returning appropriate HTTP responses.

## Responsibilities

- Receive HTTP requests.
- Validate request structure, required fields and data types.
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
| `data` | Contains the operation result, or `null` if unsuccessful. |
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

Batch operations may return `success: false` with partial results in `data` when their overall status is `PARTIAL_SUCCESS`.

File streaming responses do not follow this JSON structure.

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/files` | List directory contents. |
| POST | `/api/files` | Upload files and directories. |
| GET | `/api/files/download` | Download a file. |
| GET | `/api/directories/download` | Download a directory as a ZIP archive. |
| POST | `/api/directories` | Create a directory. |
| PATCH | `/api/files` | Rename a file or directory. |
| PATCH | `/api/files/move` | Move files or directories. |
| DELETE | `/api/files` | Delete files or directories. |

### Directory Listing

`GET /api/files`

- Optional query parameter: `path`.
- Without a path, lists the configured storage root.
- Returns directory entries and their metadata.

Example:

`GET /api/files?path=/Movies/`

### File Upload

`POST /api/files`

- Receives files using multipart form data.
- Supports individual files, multiple files and directory uploads.
- Preserves nested and empty directories.
- Uses relative paths to reconstruct directory structures.
- Supports conflict decisions: `OVERWRITE`, `KEEP_BOTH` and cancellation.
- Batch operations may partially succeed.

### File Download

`GET /api/files/download?path=/Movies/movie.mp4`

- Streams the requested file.
- Returns appropriate content type and download headers.

### Directory Download

`GET /api/directories/download?path=/Movies/Action`

- Generates a ZIP archive.
- Preserves the directory structure.
- Streams the resulting archive.

### Directory Creation

`POST /api/directories`

Example request:

```json
{
    "path": "/Movies",
    "name": "Documentaries"
}
```

Creates one directory per request.

### Rename

`PATCH /api/files`

Example request:

```json
{
    "path": "/Movies/movie.mp4",
    "new_name": "favorite-movie.mp4"
}
```

Supports files and directories.

### Move

`PATCH /api/files/move`

- Receives one or multiple source paths.
- Receives one destination directory.
- Supports partial success.
- Reports individual operation results.

### Delete

`DELETE /api/files`

- Supports single and batch deletion.
- Deletion is permanent.
- The configured storage root cannot be deleted.
- User confirmation is handled by the Web Interface.

## Filename Conflict Handling

When a destination filename already exists:

1. The API returns `409 Conflict`.
2. The Web Interface asks the user what to do.
3. The user can choose `OVERWRITE`, `KEEP_BOTH` or cancel.
4. The frontend sends the decision through the same endpoint.

For batch operations, conflicts are handled individually.

File Management is responsible for checking conflicts again when executing operations to prevent race conditions.

## HTTP Status Codes

| Status | Meaning |
|---|---|
| `200 OK` | Successful operation. |
| `201 Created` | Resource successfully created. |
| `400 Bad Request` | Invalid request structure or data. |
| `403 Forbidden` | Operation not permitted. |
| `404 Not Found` | Requested resource does not exist. |
| `409 Conflict` | Resource conflict, such as an existing filename. |
| `413 Content Too Large` | Upload exceeds the configured limit. |
| `500 Internal Server Error` | Unexpected server error. |

## Responsibilities Outside This Component

- Implementing application business rules.
- Enforcing storage boundaries.
- Handling filename conflict policies.
- Performing direct Linux filesystem operations.
- Managing frontend interactions and confirmation dialogs.
- Loading configuration files.

## Design Decisions

- REST over HTTP.
- Resource-oriented endpoint organization.
- Relative filesystem paths as resource identifiers.
- Standard JSON response structure for ordinary API responses.
- Streaming for file transfers.
- Direct communication with File Management.
- API validation is limited to request structure and data types.
- File Management handles application-level validation and rules.