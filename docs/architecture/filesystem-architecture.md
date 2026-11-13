# Filesystem Access

## Purpose

Responsible for interacting directly with the Linux filesystem, providing low-level operations to the File Management component.

## Responsibilities

- List the contents of directories.
- Retrieve file and directory metadata.
- Read file contents.
- Write file contents.
- Create files and directories.
- Rename and move files and directories.
- Delete files and directories.
- Report filesystem errors while preserving relevant error information.

## Metadata

For each filesystem entry, provide:

| Attribute | Description |
|---|---|
| Name | File or directory name |
| Type | `FILE` or `DIRECTORY` |
| Extension | File extension, when applicable |
| Size | File size |
| Modified date | Last modification date |
| Hidden | Whether the entry is hidden |
| Internal path | Filesystem path used internally by the application |

## Responsibilities outside this component

- Handling HTTP requests and responses.
- Managing frontend behavior.
- Deciding which files can be previewed in the browser.
- Applying application-level rules, such as duplicate filename handling.
- Enforcing the application's configured storage boundary (handled by File Management).

## Error Handling

Filesystem Access should report filesystem errors while preserving their relevant information.

Examples include:

- File or directory not found.
- Permission denied.
- Insufficient disk space.
- Invalid filesystem operation.

Higher-level components are responsible for interpreting these errors and deciding how they should be communicated to the user.

## Design Decisions

- File types are initially identified using filename extensions.
- Internal filesystem paths must never be exposed directly to the browser.
- The component operates on Linux filesystem resources.
- Filesystem operations are invoked through direct function or class calls.