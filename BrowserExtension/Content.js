//const servicePath = "https://webpagematcher.herokuapp.com";
const servicePath = "http://127.0.0.1:8000";
let previousUrl = window.location.href;

/**
 * Function that returns only the domain from the URL.
 *
 * @param {array} url contains domain and query parameters
 * @returns URL's domain
 */
function getUrl(url) {
  url = url.split("?");
  return url[0];
}

/**
 * Function that returns only the name of the query parameters from the URL, removing the values.
 *
 * @param {array} url contains domain and query parameters
 * @returns URL's query parameters names
 */
function getQueryParams(url) {
  url = url.split("?");
  let queryParams = url[1] ? url[1].split("&") : null;
  if (!queryParams) return queryParams;
  for (let index = 0; index < queryParams.length; index++) {
    queryParams[index] = queryParams[index].split("=")[0];
  }
  return queryParams;
}

/**
 * Function that gathers the web page HTML structure and converts the necessary elements to JSON.
 *
 * @returns web page structure in JSON.
 */
function getWebPageStructure() {
  return document.querySelector("body").outerHTML;
}

/**
 * Function that makes a HTTP POST request to the Collect Data Service to save the collected data.
 *
 * @param {*} data structure that cointains all the data attributes needed
 */
function saveData(data) {
  let http = new XMLHttpRequest();
  http.open("POST", servicePath + "/webPageSpecification", true);
  http.setRequestHeader("Content-Type", "application/json");
  http.onload = function () {
    console.log(this.status);
  };
  http.onerror = function () {
    console.log(this);
  };
  http.send(JSON.stringify(data));
}

/**
 * Event listner to detect whenever a new page is loaded or reloaded.
 */
window.addEventListener("load", (event) => {
  let url = getUrl(window.location.href);
  let queryParams = getQueryParams(window.location.href);
  let pageStructure = getWebPageStructure();
  saveData({ url, queryParams, pageStructure });
});

/**
 * Event listner to detect whenever a new page is loaded or reloaded.
 */
window.addEventListener("click", (event) => {
  href = window.location.href;
  if (href !== previousUrl) {
    previousUrl = href;
    let url = getUrl(window.location.href);
    let queryParams = getQueryParams(window.location.href);
    let pageStructure = getWebPageStructure();
    saveData({ url, queryParams, pageStructure });
  }
});
