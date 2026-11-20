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
    createMoveButton
} from './helpers.js';

const dialogArea = document.getElementById("action_dialog")
const dialogTitle = document.getElementById("dialog_title");
const dialogContent = document.getElementById("dialog_content");
const dialogForm = document.getElementById("dialog_form");
const dialogErrorContainer = document.getElementById("dialog_error");
const dialogUploadList = document.getElementById("upload_file_list");
const dialogCancelButton = document.getElementById("dialog_cancel");
const dialogSubmitButton = document.getElementById("dialog_confirm");

const createDirButton = document.getElementById("create_dir_btn")

const uploadResourceButton = document.getElementById("upload_resource_btn");

const fileInput = document.getElementById("file_input");
const folderInput = document.getElementById("folder_input");

let currentDialogAction = null;
let currentFileName = null;
let currentPath = null;

let selectedFiles = [];

const uploadProgressItems = new Map();

dialogCancelButton.addEventListener("click", closeDialog);
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

    dialogUploadList.hidden = false;
    const files = Array.from(event.dataTransfer.files);

    if (!files.length) return;

    selectedFiles = files;
    currentPath = window.location.pathname;

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
                dialogSubmitButton.disabled = true
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
            }
            break;
        case "move":
            try {
                const newDirectoryDestination = document.getElementById("destination_path").value;
                const normalizedPath = normalizePathName(currentPath);

                const sourcePath = normalizedPath + currentFileName;
                const destinationPath = newDirectoryDestination;

                console.log(sourcePath);
                console.log(destinationPath);

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
    const container = document.createElement("div");
    container.classList.add("upload_file_item");

    const filename = document.createElement("span");
    filename.textContent = file.webkitRelativePath || file.name;

    const fileSize = document.createElement("span");
    fileSize.textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;

    const progress = document.createElement("progress");
    progress.max = 100;
    progress.value = 0;

    const percentage = document.createElement("span");
    percentage.textContent = "0%";

    container.append(filename, fileSize, progress, percentage);
    dialogUploadList.append(container);

    uploadProgressItems.set(file, (value) => {
        progress.value = value;
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
    inputRename.value = file.name;

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

    dialogContent.appendChild(inputCreateDir);

    openDialog();
}

function showUploadDialog(path){
    currentDialogAction = "upload";
    currentPath = path;
    
    dialogTitle.textContent = "Uploading files";

    const uploadFilesButton = document.createElement("button");
    uploadFilesButton.type = "button";
    uploadFilesButton.textContent = "Select files";

    uploadFilesButton.addEventListener("click", () => {
        fileInput.click();
    });

    const uploadFoldersButton = document.createElement("button");
    uploadFoldersButton.type = "button";
    uploadFoldersButton.textContent = "Select folders";

    uploadFoldersButton.addEventListener("click", () => {
        folderInput.click();
    });

    dialogContent.append(
        uploadFilesButton,
        uploadFoldersButton
    );

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
    inputDestination.value = `${path}`;
    dialogContent.appendChild(inputDestination);

    openDialog();
}

function createActionButtonsContainer(file, path){
    // create a div for the action buttons
    const actionButtons = document.createElement("div");
    actionButtons.classList.add("action_buttons");

    // append the action buttons inside the respective DIV
    actionButtons.append(createDownloadButton(file, path));
    actionButtons.append(createRenameButton(file, path, showRenameDialog));
    actionButtons.append(createDeleteButton(file, path, showDeleteDialog));
    actionButtons.append(createMoveButton(file, path, showMoveDialog));

    return actionButtons
}

// renders the directory content inside the web page
function renderDirectory(entries, path) {
    const normalizedPath = normalizePathName(path);

    const fileList = document.getElementById("file_list");
    fileList.replaceChildren();

    if (entries.length === 0){
        const fileListEmptyMessage = document.createElement("p");
        fileListEmptyMessage.textContent = "No files!";
        fileList.appendChild(fileListEmptyMessage);
        return;
    }

    entries.forEach((file) => {
        const container = document.createElement("div");
        let filename = null;
        container.classList.add("entry");

        if (file.type === "DIRECTORY") {
            container.classList.add("directory");

            filename = document.createElement("a");
            filename.textContent = file.name;
            filename.href = `${normalizedPath}${file.name}`;
        } else {
            container.classList.add("file");

            filename = document.createElement("span");
            filename.textContent = file.name;
        }

        // create a div for the type area
        const type = document.createElement("div");
        type.classList.add("entry_type");
        type.textContent = file.type;
        
        // create a div for the name area
        const name = document.createElement("div");
        name.classList.add("entry_info");
        name.appendChild(filename);
        
        // create a div for the datetime area
        const datetime = document.createElement("div");
        datetime.classList.add("datetime");
        datetime.textContent = formatUnixTimestamp(file.modified_at);

        
        const actionButtons = createActionButtonsContainer(file, normalizedPath);

        //apend the file entry section into the container
        container.appendChild(type);
        container.appendChild(name);
        container.appendChild(datetime);
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
    dialogArea.close();
    dialogUploadList.hidden = true;
}

async function return_content(path = "/") {
    const entries = await loadDirectory(path);
    renderDirectory(entries, path);
}



