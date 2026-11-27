// function to hadle unix timestamp and convert to the MM/DD/YYYY HH:MM:SS pattern
export function formatUnixTimestamp(timestamp) {
    const date = new Date(timestamp * 1000)
    const pad = (num) => String(num).padStart(2, "0")

    const month = pad(date.getMonth() + 1);
    const day = pad(date.getDate());
    const year = date.getFullYear();
    
    const hours = date.getHours();
    const formattedHours = hours % 12 || 12;
    const minutes = pad(date.getMinutes());
    const seconds = pad(date.getSeconds());
    const period = hours >= 12 ? "PM" : "AM";

    return `${month}/${day}/${year} ${formattedHours}:${minutes}:${seconds} ${period}`;
}

// function for path normalization
export function normalizePathName(path) {
    path = path.replace(/\/+/g, '/');

    return path === "/" ? "/" : `${path.replace(/\/+$/, '')}/`;
}

/*
Function for action buttons creation
*/
export function createDownloadButton(file, path){
    //create the download button
    const params = new URLSearchParams({
        path: `${path}${file.name}`
    });

    const downloadButton = document.createElement("a");
    downloadButton.href = `/api/download?${params}`;
    downloadButton.textContent = "Download"
    downloadButton.classList.add("download_button")
    
    return downloadButton
}

export function createRenameButton(file, path, onRename) {
    const renameButton = document.createElement("a");
    renameButton.textContent = "Rename";
    renameButton.href = "#";
    renameButton.classList.add("rename_button");


    renameButton.addEventListener("click", (event) => {
        event.preventDefault();
        onRename(file, path);
    });

    return renameButton;
}


export function createDeleteButton(file, path, onDelete) {
    const deleteButton = document.createElement("a");
    deleteButton.textContent = "Delete";
    deleteButton.href = "#"
    deleteButton.classList.add("delete_button");

    deleteButton.addEventListener("click", (event) => {
        event.preventDefault();
        onDelete(file, path);
    })

    return deleteButton;
}


export function createMoveButton(file, path, onMove){
    const moveButton = document.createElement("a");
    moveButton.textContent = "Move";
    moveButton.href = "#";
    moveButton.classList.add("move_button");

    moveButton.addEventListener("click", (event) => {
        event.preventDefault();
        onMove(file, path);
    })

    return moveButton;
}

export function fileSizeToStringFormatted(filesize) {
    const units = ["B", "KB", "MB", "GB"];
    let size = filesize;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`;
}

export function encodePath(path) {
    return path
        .split('/')
        .map(segment => encodeURIComponent(segment))
        .join('/');
}