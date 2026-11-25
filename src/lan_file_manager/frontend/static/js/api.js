import {
    normalizePathName
} from './helpers.js';

// api call for renaming the file
export async function renameFile(file, path = "/", newName) {
    const url = new URL("/api/rename", window.location.origin)

    const params = new URLSearchParams({
        path: path,
        old_name: file,
        new_name: newName
    });

    url.search = params.toString();

    const response = await fetch(url, {method: "PATCH"});

    if (!response.ok) {
        const responseJson = await response.json();
        throw new Error(responseJson.error.message);
    }

    const responseJson = await response.json();

    if (!responseJson.success) {
        throw new Error(responseJson.error.message);
    }

    return response;
}

// api call for deleting a resource
export async function deleteResource(file, path = "/") {
    const url = new URL("/api/delete", window.location.origin);

    const params = new URLSearchParams({
        path: path,
        name: file
    });

    url.search = params.toString();

    const response = await fetch(url, {method: "DELETE"});

    if (!response.ok) {
        const responseJson = await response.json();
        throw new Error(responseJson.error.message);
    }

    const responseJson = await response.json();

    if (!responseJson.success) {
        throw new Error(responseJson.error.message);
    }

    return response;
}

export async function createNewDirectory(path = "/", name) {
    const url = new URL("/api/create", window.location.origin);

    const params = {
        name: name,
        path: path
    }

    url.search = new URLSearchParams(params).toString();

    const response = await fetch(url, {method: "POST"});

    if (!response.ok) {
        const responseJson = await response.json();
        throw new Error(responseJson.error.message);
    }

    const responseJson = await response.json()

    if (!responseJson.success) {
        throw new Error(responseJson.error.message);
    }

    return responseJson;
}

// requests the directory information from fastapi
export async function loadDirectory(path = "/") {
    const url = new URL("/api/contents", window.location.origin)

    const params = {
        path: path 
    };

    url.search = new URLSearchParams(params).toString()

    const response = await fetch(url)

    if (!response.ok) {
        const responseJson = await response.json();
        throw new Error(responseJson.error.message);
    }

    const responseJson = await response.json()

    if (!responseJson.success) {
        throw new Error(responseJson.error.message)
    }

    return responseJson.data
}


async function uploadFile(file, path, onProgress){
    const url = new URL("/api/upload", window.location.origin);
    url.searchParams.set("path", path);

    const formData = new FormData();
    formData.append("file", file, file.name);

    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.open("POST", url);

        xhr.upload.addEventListener("progress", (event) => {
            if (event.lengthComputable) {
                const percentage = Math.round(
                    (event.loaded / event.total) * 100
                );
                onProgress(percentage);
            }
        });

        xhr.addEventListener("load", () => {
            try {
                const responseJson = JSON.parse(xhr.responseText);

                if (xhr.status < 200 || xhr.status >= 300) {
                    throw new Error(responseJson.error.message);
                }

                if (!responseJson.success) {
                    throw new Error(responseJson.error.message);
                }

                resolve(responseJson);

            } catch (error) {
                reject(error);
            }
        });

        xhr.addEventListener("error", () => {
            reject(new Error("Network error during upload."));
        });

        xhr.send(formData);
    });
}

export async function uploadFiles(files, path, onFileProgress){
    const normalizedPath = normalizePathName(path);

    const uploads = files.map((file) => {
        const relativePath = file.webkitRelativePath;
        const pathParts = relativePath.split("/");

        const filename = pathParts.pop();
        const relativeDirectory = pathParts.join("/");

        const destinationPath = `${normalizedPath}${relativeDirectory}`;

        return uploadFile(
            file, 
            destinationPath,
            (percentage) => onFileProgress(file, percentage)
        );
    })

    return await Promise.allSettled(uploads);
}

// API call for moving a file or directory
export async function moveFile(sourcePath, destinationPath) {
    const url = new URL("/api/move", window.location.origin);

    const params = new URLSearchParams({
        source_path: sourcePath,
        destination_path: destinationPath
    });

    url.search = params.toString();

    const response = await fetch(url, { method: "PATCH" });

    if (!response.ok) {
        const responseJson = await response.json();
        throw new Error(responseJson.error.message);
    }

    const responseJson = await response.json();

    if (!responseJson.success) {
        throw new Error(responseJson.error.message);
    }

    return response;
}