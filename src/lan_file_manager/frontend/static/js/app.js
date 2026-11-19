const dialogArea = document.getElementById("action_dialog")
const dialogTitle = document.getElementById("dialog_title");
const dialogContent = document.getElementById("dialog_content");
const dialogForm = document.getElementById("dialog_form");
const dialogErrorContainer = document.getElementById("dialog_error");

let currentDialogAction = null;
let currentFile = null;
let currentPath = null;

document.getElementById("dialog_cancel").addEventListener("click", closeDialog);

dialogForm.addEventListener("submit", handleDialogSubmit);
async function handleDialogSubmit(event) {
    event.preventDefault();

    const newName = document.getElementById("new_name").value;

    switch (currentDialogAction) {
        case "rename":
             try {
                await renameFile(currentFile, currentPath, newName);
                window.location.reload();
            } catch (error) {
                const errorContainer = dialogErrorContainer;

                errorContainer.textContent = error.message;
                errorContainer.hidden = false;
            }
            break;
        case "delete":
            //handle deleting
            break;
        case "move":
            //handle moving
            break;
    }
  
}

async function renameFile(file, path = "/", newName) {
    const url = new URL("/api/rename", window.location.origin)

    const params = new URLSearchParams({
        path: path,
        old_name: file,
        new_name: newName
    });

    console.log("File current", file);
    console.log("New name", newName);
    console.log("CurrentPath", path);

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

    closeDialog();
    return response;
}

// function to hadle unix timestamp and convert to the MM/DD/YYYY HH:MM:SS pattern
function formatUnixTimestamp(timestamp) {
    const date = new Date(timestamp * 1000)
    const pad = (num) => String(num).padStart(2, '0')

    const month = pad(date.getMonth() + 1);
    const day = pad(date.getDate());
    const year = date.getFullYear();
    
    const hours = pad(date.getHours());
    const minutes = pad(date.getMinutes());
    const seconds = pad(date.getSeconds());

    return `${month}/${day}/${year} ${hours}:${minutes}:${seconds}`;
}

// requests the directory information from fastapi
async function loadDirectory(path = "/") {
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

function showRenameDialog(file, path) {
    currentDialogAction = "rename";
    currentFile = file.name;
    currentPath = path;

    dialogContent.replaceChildren();
    dialogTitle.textContent = "Renaming";

    const inputRename = document.createElement('input');
    inputRename.id = "new_name";
    inputRename.value = file.name;

    dialogContent.appendChild(inputRename);

    openDialog();
}

function createDownloadButton(file, path){
    //create the download button
    const params = new URLSearchParams({
        path: `${path}${file.name}`
    });

    const downloadButton = document.createElement('a');
    downloadButton.href = `/api/download?${params}`;
    downloadButton.textContent = 'Download'
    downloadButton.classList.add("download_button")
    
    return downloadButton
}

function createRenameButton(file, path) {
    const renameButton = document.createElement('a');
    renameButton.textContent = 'Rename';
    renameButton.href = '#';
    renameButton.classList.add("rename_button");


    renameButton.addEventListener('click', () => {
        event.preventDefault();
        showRenameDialog(file, path);
    });

    return renameButton;
}

function createActionButtonsContainer(file, path){
    // create a div for the action buttons
    const actionButtons = document.createElement('div');
    actionButtons.classList.add('action_buttons');

    // append the action buttons inside the respective DIV
    actionButtons.append(createDownloadButton(file, path));
    actionButtons.append(createRenameButton(file, path))

    return actionButtons
}

// renders the directory content inside the web page
function renderDirectory(entries, path) {
    const normalizedPath = path === "/" ? "/" : `${path}/`;

    const fileList = document.getElementById("file_list");
    fileList.replaceChildren();

    entries.forEach((file) => {
        const container = document.createElement('div');
        let filename = null;
        container.classList.add('entry');

        if (file.type === "DIRECTORY") {
            container.classList.add("directory");

            filename = document.createElement('a');
            filename.textContent = file.name;
            filename.href = `${normalizedPath}${file.name}`;
        } else {
            container.classList.add("file");

            filename = document.createElement('span');
            filename.textContent = file.name;
        }

        // create a div for the type area
        const type = document.createElement('div');
        type.classList.add('entry_type')
        type.textContent = file.type;
        
        // create a div for the name area
        const name = document.createElement('div');
        name.classList.add('entry_info')
        name.appendChild(filename)
        
        // create a div for the datetime area
        const datetime = document.createElement('div');
        datetime.classList.add('datetime')
        datetime.textContent = formatUnixTimestamp(file.modified_at)

        
        actionButtons = createActionButtonsContainer(file, normalizedPath);

        //apend the file entry section into the container
        container.appendChild(type);
        container.appendChild(name);
        container.appendChild(datetime);
        container.appendChild(actionButtons);
        
        fileList.append(container)
    })

}

async function return_content(path = '/') {
    const entries = await loadDirectory(path);
    renderDirectory(entries, path);
}

function openDialog() {
    dialogErrorContainer.textContent = "";
    dialogErrorContainer.hidden = true;
    dialogArea.showModal();
}

function closeDialog() {
    dialogArea.close()
}


document.addEventListener("DOMContentLoaded", async () => {
    const currentPath = window.location.pathname;

    const entries = await loadDirectory(currentPath);
    renderDirectory(entries, currentPath);
});