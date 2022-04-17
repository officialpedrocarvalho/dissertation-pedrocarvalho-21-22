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
  let url = getUrl();
  let pageStructure = getWebPageStructure();
  saveData({ url, pageStructure });
});

/**
 * Event listner to detect whenever a new page is loaded or reloaded.
 */
window.addEventListener("click", (event) => {
  let url = getUrl();
  if (url !== previousUrl) {
    previousUrl = url;
    let pageStructure = getWebPageStructure();
    saveData({ url, pageStructure });
  }
});
