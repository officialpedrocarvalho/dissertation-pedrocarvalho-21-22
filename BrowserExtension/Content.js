//const servicePath = "https://webpagematcher.herokuapp.com";
const servicePath = "http://127.0.0.1:8000";
let previousUrl = window.location.href;

/**
 * Function that returns only the domain from the URL.
 *
 * @returns URL's domain
 */
function getUrl() {
  return window.location.href;
}

/**
 * Function that gathers the web page HTML structure and converts the necessary elements to JSON.
 *
 * @returns web page structure in JSON.
 */
function getWebPageStructure() {
  return document.documentElement.outerHTML;
}

/**
 * Function that makes a HTTP POST request to the Collect Data Service to save the collected data.
 *
 * @param {*} data structure that cointains all the data attributes needed
 */
function saveData(data) {
  let http = new XMLHttpRequest();
  http.open("POST", servicePath + "/webPage", true);
  http.withCredentials = true;
  http.setRequestHeader("Content-Type", "application/json");
  http.onload = function () {
    console.log("SUCCESS", this.status);
  };
  http.onerror = function () {
    console.log(this.status);
  };
  http.send(JSON.stringify(data));
}

/**
 * Event listner to detect whenever a new page is loaded or reloaded.
 */
window.addEventListener("load", (event) => {
  activateLoaderProtection();
  setTimeout(function () {
    let url = getUrl();
    let pageStructure = getWebPageStructure();
    saveData({ url, pageStructure });
    deactivateLoaderProtection();
  }, 2000);
});

/**
 * Event listner to detect whenever a new page is loaded or reloaded.
 */
window.addEventListener("click", (event) => {
  if (event.target.id != "my-protector-pedro-carvalho" && event.target.id != "my-spinner-pedro-carvalho") {
    setTimeout(function () {
      let url = getUrl();
      if (url !== previousUrl) {
        activateLoaderProtection();
        setTimeout(function () {
          let url = getUrl();
          previousUrl = url;
          let pageStructure = getWebPageStructure();
          saveData({ url, pageStructure });
          deactivateLoaderProtection();
        }, 2000);
      }
    }, 200);
  }
});

function activateLoaderProtection() {
  let protector = document.createElement("div");
  protector.id = "my-protector-pedro-carvalho";
  protector.classList.add("my-protector-pedro-carvalho");
  let spinner = document.createElement("div");
  spinner.id = "my-spinner-pedro-carvalho";
  spinner.classList.add("my-spinner-pedro-carvalho");
  protector.appendChild(spinner);
  let body = document.querySelector("body");
  body.parentNode.insertBefore(protector, body);
}

function deactivateLoaderProtection() {
  let protector = document.querySelector("#my-protector-pedro-carvalho");
  protector.remove();
}
