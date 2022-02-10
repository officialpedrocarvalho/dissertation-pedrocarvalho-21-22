let xhr = new XMLHttpRequest();
let uuid;
let path;
let block;
const basePath = "http://10.227.107.156:8080";
let dragPath = null;

let timer = 0;
let delay = 200;
let prevent = false;

let keyPressMode = false;
let keyArray = [];


document.addEventListener("DOMContentLoaded", function () {
    var data = sessionStorage.getItem('uuid');
    // generate unique identifier if there is no uuid stored
    if (data === null) {
        uuid = generateUuid();
        sessionStorage.setItem('uuid', uuid);
        sessionStorage.setItem('elementPos', 0);
        data = sessionStorage.getItem('uuid');
    }
  //  console.log("ready!", data);

});

document.addEventListener("click", function (ev) {
    checkPasswordInput(ev);
    checkInputToSave();
    // the delay allows to detect a double click before
    // saving the first click as a simple click
    timer = setTimeout(function () {
        if (!prevent) {
            getMouseElement(ev);
        }
        prevent = false;
    }, delay);
});

document.addEventListener("dblclick", function (ev) {
    checkInputToSave();
    clearTimeout(timer);
    getMouseElement(ev);
    prevent = true;
});

document.addEventListener("dragstart", function (ev) {
    checkInputToSave();
    dragPath = createXPathFromElement(ev.srcElement);
});

document.addEventListener("drop", function (ev) {
    if (dragPath !== null) {
        getDragAndDropElement(dragPath, ev);
    }
});

// the key's value is saved in a key array to be saved in the DB when the input is deselected
document.addEventListener("keypress", function (ev) {
    keyPressMode = true;
    buildKeyArray(ev.key);
});

// detect backspace, delete, tab and enter
document.addEventListener("keyup", function (ev) {
    if (ev.which === 8 || ev.which === 46 || ev.which === 9 || ev.which === 13) {
        buildKeyArray(ev.key);
    }
});

document.addEventListener("paste", function (ev) {
    getPasteElement(ev, ev.clipboardData.getData('Text'));
});

// check if there is any input data to save - when an input
// is deselected by a click in other place, its data should be saved
function checkInputToSave() {
    if (keyPressMode) {
        if (keyArray.length > 0) {
            getKeyboardElement(keyArray);
        }
        keyArray = [];
        keyPressMode = false;
    }
}

// avoid to save password field
function checkPasswordInput(ev) {
    if (ev.srcElement.type === "password") {
        block = true;
    }
    else {
        block = false;
    }
}

// join the input values in an array
function buildKeyArray(key) {
    if (!block) {
        let keyType = getKeyType(key);
        keyArray.push(keyType);
    }
}

// to avoid retrieve sensitive data,
// input values are converted in char or string according to its length
// "special" keys are also saved (backspace, tab, enter, delete);
function getKeyType(key) {
    let keyType;
    if (/^[a-zA-Z]+$/.test(key)) {
        if (key.length === 1) {
            keyType = 'char';
        }
        else if (key === "Backspace" || key === "Tab" || key === "Enter" || key === "Delete") {
            keyType = key;
        }
        else if (key.length > 1) {
            keyType = 'string';
        }
    }
    else if (key === " ") {
        keyType = 'space';
    }
    else if (!isNaN(key)) {
        keyType = 'num';
    }
    return keyType;
}

function getMouseElement(ev) {
    path = createXPathFromElement(ev.srcElement);
    getPathId(path, ev.type);
}

// function called after the getPathId, to save the mouse interaction in the DB
function callbackFromGetPathIdMouseEvent(idFromCallback, action) {
    let actionId = getActionId(action);

    let elementPos = parseInt(sessionStorage.getItem('elementPos')) + 1;
    sessionStorage.setItem('elementPos', elementPos);

    if (elementPos === 1) {
        saveNodeOnDataBase(path, idFromCallback, sessionStorage.getItem('uuid'), sessionStorage.getItem('elementPos'), action, actionId, getFormattedUrl(window.location.href));
    }
    else {
        saveRelationshipOnDatabase(path, idFromCallback, sessionStorage.getItem('uuid'), sessionStorage.getItem('elementPos'), action, actionId, getFormattedUrl(window.location.href));
    }
}

function getDragAndDropElement(dragPath, ev) {
    let dropArray = [];
    let dropPath = createXPathFromElement(ev.srcElement);
    dropArray.push(dropPath);
    const action = "dragAndDrop";

    getPathId(dragPath, action, dropArray);

}

// function called after the getPathId, to save the drag and drop interaction in the DB
function callbackFromGetPathIdDragEvent(idFromCallback, action, dropPath) {
    let actionId = getActionId(action);
    let elementPos = parseInt(sessionStorage.getItem('elementPos')) + 1;
    sessionStorage.setItem('elementPos', elementPos);

    if (elementPos === 1) {
        saveNodeOnDataBase(dragPath, idFromCallback, sessionStorage.getItem('uuid'), sessionStorage.getItem('elementPos'), action, actionId, getFormattedUrl(window.location.href), dropPath);
    }
    else {
        saveRelationshipOnDatabase(dragPath, idFromCallback, sessionStorage.getItem('uuid'), sessionStorage.getItem('elementPos'), action, actionId, getFormattedUrl(window.location.href), dropPath);
    }
}

function getPasteElement(ev, pasteInput) {
    let keyType = getKeyType(pasteInput);
    const action = "input";
    getPathId(path, action, keyType);
}

function getKeyboardElement(keyArray) {
    const action = "input";
    getPathId(path, action, keyArray);

}

// function called after the getPathId, to save the input interaction in the DB
function callbackFromGetPathIdInputEvent(idFromCallback, action, inputValue) {
    let actionId = getActionId(action);
    let elementPos = parseInt(sessionStorage.getItem('elementPos')) + 1;
    sessionStorage.setItem('elementPos', elementPos);

    if (elementPos === 1) {
        saveNodeOnDataBase(path, idFromCallback, sessionStorage.getItem('uuid'), elementPos, action, actionId, getFormattedUrl(window.location.href), inputValue);
    }
    else {
        saveRelationshipOnDatabase(path, idFromCallback, sessionStorage.getItem('uuid'), elementPos, action, actionId, getFormattedUrl(window.location.href), inputValue);
    }
}

// save just one node in the DB
function saveNodeOnDataBase(path, pathId, session, elementPos, action, actionId, url, value = null) {
    xhr.open("POST", basePath + '/node/add', true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({
        path: path,
        pathId: pathId,
        session: session,
        elementPos: elementPos,
        action: action,
        actionId: actionId,
        url: url,
        value: value
    }));
}

// save one node and its relationship with the previous one
function saveRelationshipOnDatabase(path, pathId, session, elementPos, action, actionId, url, value = null) {
    xhr.open("POST", basePath + '/relationship/add', true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({
        path: path,
        pathId: pathId,
        session: session,
        elementPos: elementPos,
        action: action,
        actionId: actionId,
        url: url,
        value: value
    }));
}

// function to generate a unique id to represent the session
function generateUuid() {
    function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    }

    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
        s4() + '-' + s4() + s4() + s4();
}


function createXPathFromElement(elm) {
    var allNodes = document.getElementsByTagName('*');
    for (var segs = []; elm && elm.nodeType == 1; elm = elm.parentNode) {
        if (elm.hasAttribute('id')) {
            var uniqueIdCount = 0;
            for (var n = 0; n < allNodes.length; n++) {
                if (allNodes[n].hasAttribute('id') && allNodes[n].id == elm.id) uniqueIdCount++;
                if (uniqueIdCount > 1) break;
            }
            ;
            if (uniqueIdCount == 1) {
                segs.unshift('id("' + elm.getAttribute('id') + '")');
                return segs.join('/');
            } else {
                segs.unshift(elm.localName.toLowerCase() + '[@id="' + elm.getAttribute('id') + '"]');
            }
        } else if (elm.hasAttribute('class')) {
            segs.unshift(elm.localName.toLowerCase() + '[@class="' + elm.getAttribute('class') + '"]');
        } else {
            for (i = 1, sib = elm.previousSibling; sib; sib = sib.previousSibling) {
                if (sib.localName == elm.localName) i++;
            }
            ;
            segs.unshift(elm.localName.toLowerCase() + '[' + i + ']');
        }
        ;
    }
    ;
    return segs.length ? '/' + segs.join('/') : null;
}

// two requests are made in this function:
// the first one aims to check if there is already a path id to the interaction: (path, action, url)
// if the interaction has not an id yet, a second request is made to get the last id set,
// increasing one to the highest value already defined.
function getPathId(path, action, optionalValue) {
    let formattedUrl = getFormattedUrl(window.location.href);
    let id = null;
    xhr.open("POST", basePath + '/pathId', true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({
        path: path,
        action: action,
        url: formattedUrl
    }));
    xhr.onload = function () {
        let responseJson = JSON.parse(xhr.response);
        if (responseJson.records.length > 0) {
            id = responseJson.records[0]._fields[0];
            setId(id, action, optionalValue);
        }
        else {
            let lastId = null;
            xhr.open("GET", basePath + '/lastId', true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.onload = function () {
                let responseJson = JSON.parse(xhr.response);
                if (responseJson.records.length > 0) {
                    id = responseJson.records[0]._fields[0];
                    setId(id + 1, action, optionalValue);
                }
                else {
                    setId(1, action, optionalValue);
                }
            };
            xhr.send('');
        }
    };
}

function getFormattedUrl(url){
    return url.split('?',1);

}
// after getting the id, it's called the function responsible to save the interaction
// according to the type of action performed
function setId(idValue, action, optionalValue) {
    switch (action) {
        case "click":
            callbackFromGetPathIdMouseEvent(idValue, action);
            break;
        case "dblclick":
            callbackFromGetPathIdMouseEvent(idValue, action);
            break;
        case "dragAndDrop":
            callbackFromGetPathIdDragEvent(idValue, action, optionalValue);
            break;
        case "input":
            callbackFromGetPathIdInputEvent(idValue, action, optionalValue);
            break;
        default:
            break;
    }
}

// get a representative id of the action performed
function getActionId(actionType) {
    let actionId;
    switch (actionType) {
        case "click":
            actionId = 1;
            break;
        case "dragAndDrop":
            actionId = 2;
            break;
        case "input":
            actionId = 3;
            break;
        case "dblclick":
            actionId = 4;
            break;
        default:
            break;
    }
    return actionId;
}