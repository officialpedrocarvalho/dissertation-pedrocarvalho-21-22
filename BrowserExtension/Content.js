const servicePath = "http://127.0.0.1:8000";

/**
 * Function that recevies a URL and separates its domain from its query parameters.
 *
 * @param {string} url
 * @returns domain and query parameters
 */
function getPageURL(url) {
  url = url.split("?");
  let domain = getDomain(url);
  let queryParams = getQueryParams(url);
  return { domain, queryParams };
}

/**
 * Function that returns only the domain from the URL.
 * 
 * @param {array} url contains domain and query parameters
 * @returns URL's domain
 */
function getDomain(url) {
  return url[0];
}

/**
 * Function that returns only the name of the query parameters from the URL, removing the values.
 * 
 * @param {array} url contains domain and query parameters
 * @returns URL's query parameters names
 */
function getQueryParams(url) {
  let queryParams = url[1] ? url[1].split("&") : null;
  if (!queryParams) return queryParams;
  for (let index = 0; index < queryParams.length; index++) {
    queryParams[index] = queryParams[index].split("=")[0];
  }
  return queryParams;
}

/**
 * Function that makes a HTTP POST request to the Collect Data Service to save the collected data.
 * 
 * @param {*} data structure that cointains all the data attributes needed
 */
function saveData(data) {
  let http = new XMLHttpRequest();
  http.open("POST", servicePath + "/data", true);
  http.setRequestHeader("Content-Type", "application/json");
  http.onload = function () {
    if (this.status === 201) {
      console.log(this.response);
    }
  };
  http.onerror = function () {
    console.log(this);
  };
  http.send(JSON.stringify(data));
}

saveData(getPageURL(window.location.href));
