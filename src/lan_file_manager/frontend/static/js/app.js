import {
    renameFile,
    deleteResource,
    loadDirectory,
    createNewDirectory,
    uploadFiles,
    moveFile
} from './api.js';

import {
    formatUnixTimestamp,
    normalizePathName,
    createDownloadButton,
    createRenameButton,
    createDeleteButton,
    createMoveButton,
    fileSizeToStringFormatted,
    encodePath
} from './helpers.js';

const dialogArea = document.getElementById("action_dialog")
const dialogTitle = document.getElementById("dialog_title");
const dialogContent = document.getElementById("dialog_content");
const dialogForm = document.getElementById("dialog_form");
const dialogErrorContainer = document.getElementById("dialog_error");
const dialogUploadList = document.getElementById("upload_file_list");
const dialogCancelButton = document.getElementById("dialog_cancel");
const dialogSubmitButton = document.getElementById("dialog_confirm");
const dialogCloseButton = document.getElementById("close_button");

const createDirButton = document.getElementById("create_dir_btn")

const uploadResourceButton = document.getElementById("upload_resource_btn");

const fileInput = document.getElementById("file_input");
const folderInput = document.getElementById("folder_input");

let currentDialogAction = null;
let currentFileName = null;
let currentPath = null;

let selectedFiles = [];

const uploadProgressItems = new Map();

function asdf(path) {
    return path
        .replace(/\/+/g, '/')
        .replace(/\/+$/, '') || '/';
}

dialogCancelButton.addEventListener("click", closeDialog);
dialogCloseButton.addEventListener("click", closeDialog);
dialogForm.addEventListener("submit", handleDialogSubmit);
createDirButton.addEventListener("click", (event) => {
    event.preventDefault();
    showCreateDirDialog(decodeURIComponent(window.location.pathname));
});

uploadResourceButton.addEventListener("click", (event) => {
    event.preventDefault();
    cleanUploadDialog();
    showUploadDialog(decodeURIComponent(window.location.pathname));
});

// events to allow drag and drop files (only files)
document.addEventListener("dragover", (event) => {
    event.preventDefault();
});

document.addEventListener("drop", (event) => {
    event.preventDefault();
    cleanUploadDialog();

    dialogUploadList.hidden = false;
    const files = Array.from(event.dataTransfer.files);

    if (!files.length) {
        closeDialog();
        return;
    };

    selectedFiles = files;
    currentPath = decodeURIComponent(window.location.pathname);

    showUploadDialog(currentPath);
    renderSelectedFiles(selectedFiles);
});

// whenever the pages updates, retrieve the folder content for that page
document.addEventListener("DOMContentLoaded", async () => {
    const currentPath = decodeURIComponent(window.location.pathname);

    const entries = await loadDirectory(currentPath);
    renderDirectory(entries, currentPath);
});

fileInput.addEventListener("change", handleFileSelection);
folderInput.addEventListener("change", handleFolderSelection);

async function handleDialogSubmit(event) {
    event.preventDefault();

    switch (currentDialogAction) {
        case "rename":
            try {
                const newName = document.getElementById("new_name").value;

                await renameFile(currentFileName, currentPath, newName);
                window.location.reload();
            } catch (error) {
                dialogErrorContainer.textContent = error.message;
                dialogErrorContainer.hidden = false;
            }
            break;

        case "delete":
            try {
                await deleteResource(currentFileName, currentPath);
                window.location.reload();
            } catch (error) {
                dialogErrorContainer.textContent = error.message;
                dialogErrorContainer.hidden = false;
                dialogContent.replaceChildren();
            }
            break;

        case "create_directory":
            try {
                const newDirectoryName = document.getElementById("new_directory").value;
                await createNewDirectory(currentPath, newDirectoryName);
                window.location.reload();
            } catch (error) {
                dialogErrorContainer.textContent = error.message;
                dialogErrorContainer.hidden = false;
            }
            break;
        case "upload":
            try {
                if (!selectedFiles.length) {
                    throw new Error("Please select at least one file.");
                }

                dialogCancelButton.disabled = true;
                dialogSubmitButton.disabled = true;

                const uploadMessage = document.createElement("p");
                uploadMessage.textContent = "Please wait while your files are being uploaded. The page will refresh automatically once the upload is complete.";
                dialogContent.replaceChildren(uploadMessage);

                await uploadFiles(selectedFiles, currentPath, (file, percentage) => {
                    const updateProgress = uploadProgressItems.get(file);
                    updateProgress(percentage);
                });

                selectedFiles = [];
                closeDialog();
                window.location.reload();
            } catch (error) {
                dialogErrorContainer.textContent = error.message;
                dialogErrorContainer.hidden = false;
                dialogContent.hidden = false;
            }
            break;
        case "move":
            try {
                const newDirectoryDestination = document.getElementById("destination_path").value;
                const normalizedPath = normalizePathName(currentPath);

                const sourcePath = normalizedPath + currentFileName;
                const destinationPath = newDirectoryDestination;

                await moveFile(sourcePath, destinationPath)
                window.location.reload();
            } catch (error) {
                dialogErrorContainer.textContent = error.message;
                dialogErrorContainer.hidden = false;
            }
            break;
    }
  
}

function handleFileSelection(event) {
    selectedFiles = Array.from(event.target.files);
    renderSelectedFiles(selectedFiles);
    event.target.value = "";
}

function handleFolderSelection(event) {
    selectedFiles = Array.from(event.target.files);
    renderSelectedFiles(selectedFiles);
    event.target.value = "";
}

function cleanUploadDialog(){
    selectedFiles = [];
    dialogUploadList.replaceChildren();
    dialogUploadList.hidden = false;
    dialogContent.replaceChildren();
}

function renderSelectedFiles(files) {
    dialogUploadList.replaceChildren();
    uploadProgressItems.clear();

    files.forEach((file) => {
        createUploadProgressItem(file);
    });
}

function createUploadProgressItem(file) {
    // create the container for each uploaded file
    const container = document.createElement("div");
    container.classList.add("upload_file_item");

    // create the column for the filename
    const filename = document.createElement("span");
    filename.classList.add("upload_file_name");
    filename.textContent = file.webkitRelativePath || file.name;
    filename.title = file.webkitRelativePath || file.name;

    // create the column for the file size
    const fileSize = document.createElement("span");
    fileSize.classList.add("upload_file_size");
    fileSize.textContent = fileSizeToStringFormatted(file.size);

    // create the column for progress bar
    const progressContainer = document.createElement("div");
    progressContainer.classList.add("upload_file_progress");

    // create the progress bar container
    const progress = document.createElement("div");
    progress.setAttribute("role", "progressbar");
    progress.classList.add("animate");
    
    // create the progress bar  
    const progressFill = document.createElement("div");
    progressFill.style.width = "0%";

    progress.append(progressFill);

    // create the percentage column
    const percentage = document.createElement("span");
    percentage.textContent = "0%";

    progressContainer.append(progress, percentage);
    container.append(filename, fileSize, progressContainer);

    dialogUploadList.append(container);

    uploadProgressItems.set(file, (value) => {
        progressFill.style.width = `${value}%`;
        percentage.textContent = `${value}%`;
    });
}

function showRenameDialog(file, path) {
    currentDialogAction = "rename";
    currentFileName = file.name;
    currentPath = path;

    dialogContent.replaceChildren();
    dialogTitle.textContent = "Renaming";

    const inputRename = document.createElement("input");
    inputRename.id = "new_name";
    inputRename.type = "text";
    inputRename.value = file.name;
    inputRename.setAttribute("maxlength", "255");

    dialogContent.appendChild(inputRename);

    openDialog();
}

function showDeleteDialog(file, path){
    currentDialogAction = "delete";
    currentFileName = file.name;
    currentPath = path;

    dialogContent.replaceChildren();
    dialogTitle.textContent = "Deleting";

    const deleteMessage = document.createElement('p');
    deleteMessage.textContent = `Are you sure you want to permanently delete ${currentFileName} ?`;
    deleteMessage.classList.add("delete_message");

    const deleteWarning = document.createElement('p');
    deleteWarning.classList.add("delete_warning");

    if (file.type === "DIRECTORY") {
    deleteWarning.textContent = "This directory and all its contents will be permanently deleted.";
    } else {
        deleteWarning.textContent = `This action cannot be undone.`;
    }

    dialogContent.appendChild(deleteMessage);
    dialogContent.appendChild(deleteWarning);

    openDialog();
}

async function showCreateDirDialog(path){
    currentDialogAction = "create_directory";
    currentPath = path;

    dialogContent.replaceChildren();
    dialogTitle.textContent = "Creating a new directory";

    const dialogParagraph = document.createElement("p");
    dialogParagraph.textContent = "Enter the name for the new folder."
    dialogContent.appendChild(dialogParagraph);

    const inputCreateDir = document.createElement("input");
    inputCreateDir.id = "new_directory";
    inputCreateDir.type = "text";
    inputCreateDir.setAttribute("maxlength", "255");

    dialogContent.appendChild(inputCreateDir);

    openDialog();
}

function showUploadDialog(path){
    currentDialogAction = "upload";
    currentPath = path;
    
    dialogTitle.textContent = "Uploading files";
    // dialogContent.replaceChildren();
    // message for the upload dialog
    const dialogContentMessage = document.createElement("p");
    dialogContentMessage.textContent = "Select files or a folder you want to upload."
    dialogContent.appendChild(dialogContentMessage);

    // container for the upload buttons 
    const uploadButtonsContainer = document.createElement("div");
    uploadButtonsContainer.classList.add("upload_button_container");

    // button for uploading FILES
    const uploadFilesButton = document.createElement("button");
    uploadFilesButton.type = "button";
    uploadFilesButton.textContent = "Choose files";

    uploadFilesButton.addEventListener("click", () => {
        fileInput.click();
    });

    // button for uploading A DIRECTORY
    const uploadFoldersButton = document.createElement("button");
    uploadFoldersButton.type = "button";
    uploadFoldersButton.textContent = "Choose a folder";

    uploadFoldersButton.addEventListener("click", () => {
        folderInput.click();
    });

    // append both button into the dialog content
    uploadButtonsContainer.append(
        uploadFilesButton,
        uploadFoldersButton
    );

    // append the upload button container into dialog content
    dialogContent.appendChild(uploadButtonsContainer);

    openDialog();
}

function showMoveDialog(file, path) {
    currentDialogAction = "move";
    currentFileName = file.name;
    currentPath = path;

    dialogContent.replaceChildren();
    dialogTitle.textContent = "Moving";

    const dialogParagraph = document.createElement("p");
    dialogParagraph.textContent = "Enter the new resource destination folder"
    dialogContent.appendChild(dialogParagraph);

    const inputDestination = document.createElement("input");
    inputDestination.id = "destination_path";
    inputDestination.type = "text";
    inputDestination.value = `${path}`;
    dialogContent.appendChild(inputDestination);

    openDialog();
}

function createActionButtonsContainer(file, path) {
    // Create the action buttons column
    const actionButtons = document.createElement("td");
    actionButtons.classList.add("action_buttons");

    // Create the list
    const actionButtonsList = document.createElement("ul");
    actionButtonsList.classList.add("action_buttons_list");

    // Create individual list items
    const downloadItem = document.createElement("li");
    downloadItem.append(createDownloadButton(file, path));

    const renameItem = document.createElement("li");
    renameItem.append(createRenameButton(file, path, showRenameDialog));

    const deleteItem = document.createElement("li");
    deleteItem.append(createDeleteButton(file, path, showDeleteDialog));

    const moveItem = document.createElement("li");
    moveItem.append(createMoveButton(file, path, showMoveDialog));

    // Append items to the list
    actionButtonsList.append(
        downloadItem,
        renameItem,
        deleteItem,
        moveItem
    );

    actionButtons.append(actionButtonsList);

    return actionButtons;
}

// renders the directory content inside the web page
function renderDirectory(entries, path) {
    // path -> ///test#//tmp || /test#/tmp
    // normalized path -> /test#/tmp
    // encodedPath -> /test%23/tmp
    const normalizedPath = normalizePathName(path); 
    const encodedPath = encodePath(normalizedPath);
    
    if (window.location.pathname !== encodedPath) {
        window.history.replaceState(null, '', encodedPath);
    }
    
    const fileList = document.getElementById("file_list");
    fileList.replaceChildren();

    if (entries.length === 0){
        const fileListEmptyMessage = document.createElement("p");
        fileListEmptyMessage.classList.add("no_file_message");
        fileListEmptyMessage.textContent = "No files!";
        fileList.appendChild(fileListEmptyMessage);
        return;
    }

    // Sorts the folder contend for displaying folders first
    let orderedEntries = entries.toSorted((a, b) => {
        if (a.type === "DIRECTORY" && b.type === "FILE") {
            return -1;
        } else if (a.type === "FILE" && b.type === "DIRECTORY") {
            return 1;
        } else {
            return a.name.localeCompare(b.name);
        }
    });

    orderedEntries.forEach((file) => {
        let container = document.createElement("tr");
        container.classList.add("entry");

        // define the filename link
        let filename = document.createElement("a");
        filename.textContent = file.name;
        filename.href = `${encodedPath}${encodeURIComponent(file.name)}`;

        if (file.type === "DIRECTORY") {
            container.classList.add("directory");
        } else {
            container.classList.add("file");
            filename.setAttribute("target", "_blank");
        }

        // create a column for the name area
        const name = document.createElement("td");
        name.classList.add("entry_name");

        const filenameContainer = document.createElement("div");
        filenameContainer.classList.add("filename_container");  

        filenameContainer.appendChild(filename);
        name.appendChild(filenameContainer);

        // create a column for the type area
        const type = document.createElement("td");
        type.classList.add("entry_type");
        type.textContent = file.type;
        
        // create a column for the datetime area
        const datetime = document.createElement("td");
        datetime.classList.add("entry_datetime");
        datetime.textContent = formatUnixTimestamp(file.modified_at);

        // create a column for the size area
        const size = document.createElement("td");
        size.classList.add("entry_size");
        size.textContent = file.type === "FILE" ? fileSizeToStringFormatted(file.size) : "n/a";
        
        const actionButtons = createActionButtonsContainer(file, normalizedPath);

        //apend the file entry section into the container
        // container.appendChild(type);
        container.appendChild(name);
        container.appendChild(datetime);
        container.appendChild(size);
        container.appendChild(actionButtons);
        
        
        fileList.append(container)
    })
}



function openDialog() {
    dialogErrorContainer.textContent = "";
    dialogErrorContainer.hidden = true;
    dialogCancelButton.disabled = false;
    dialogSubmitButton.disabled = false;
    dialogArea.showModal();
}

function closeDialog() {
    dialogContent.replaceChildren()
    dialogUploadList.hidden = true;
    dialogArea.close();
}