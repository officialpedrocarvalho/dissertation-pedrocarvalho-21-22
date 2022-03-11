const servicePath = "http://127.0.0.1:8000";
const unwantedTags2 = [
  "SCRIPT",
  "LI",
  "TD",
  "TR",
  "SPAN",
  "B",
  "STRONG",
  "EM",
  "MARK",
  "SMALL",
  "DEL",
  "INS",
  "SUB",
  "SUP",
  "STYLE",
  "NOSCRIPT",
];

const unwantedTags = [
  "SCRIPT",
  "B",
  "STRONG",
  "EM",
  "MARK",
  "SMALL",
  "DEL",
  "INS",
  "SUB",
  "SUP",
  "STYLE",
  "NOSCRIPT",
];

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
  let structure = document.querySelector("body");
  return element(structure);
}

/**
 * Function that receives an HTML element and converts it to JSON. Specifies the element tag name and its elements children in an array.
 *
 * @param {*} e HTML element
 * @returns JSON element.
 */
const element = (e) => ({
  tag: e.tagName,
  classes: extractAttributes(e.attributes, "class"),
  id: extractAttributes(e.attributes, "id"),
  children: Array.from(e.childNodes, node)
    .filter(Boolean)
    .filter(function (e) {
      return !unwantedTags.includes(e["tag"]);
    }),
});

/**
 * Function that receives an HTML element and according to its element type returns a JSON convertion.
 *
 * @param {*} e HTML element
 * @returns JSON element
 */
const node = (e) => {
  switch (e?.nodeType) {
    case 1:
      return element(e);
  }
};

/**
 *
 * @param {*} name
 * @param {*} value
 * @returns
 */
const classes = ({ name, value }) => {
  switch (name) {
    case "class":
      return value.split(" ");
  }
};

const extractAttributes = (e, a) => {
  for (const [key, value] of Object.entries(e)) {
    if (value.name == a) {
      return value.value.split(" ");
    }
  }
  return [];
};

/**
 * Function that makes a HTTP POST request to the Collect Data Service to save the collected data.
 *
 * @param {*} data structure that cointains all the data attributes needed
 */
function saveData(data) {
  let http = new XMLHttpRequest();
  http.open("PUT", servicePath + "/webPageSpecification/1", true);
  http.setRequestHeader("Content-Type", "application/json");
  http.onload = function () {
    if (this.status === 201) {
      //console.log(this.response);
    }
    //console.log(this.response);
  };
  http.onerror = function () {
    console.log(this);
  };
  http.send(JSON.stringify(data));
}

/**
 * Event listner to detect whenever a new page is loaded or reloaded.
 */
/*window.addEventListener("load", (event) => {
  let url = getUrl(window.location.href);
  let queryParams = getQueryParams(window.location.href);
  let pageStructure = getWebPageStructure();
  console.log(pageStructure)
  saveData({ url, queryParams, pageStructure });
});*/

window.onload = function afterWebPageLoad() {
  setTimeout(function () {
    console.log("SENT REUEST");
    let url = getUrl(window.location.href);
    let queryParams = getQueryParams(window.location.href);
    let pageStructure = getWebPageStructure();
    saveData({ url, queryParams, pageStructure });
  }, 3000);
};

const tagName = (e) => {
  switch (e?.nodeType) {
    case 1:
      return e.tagName;
  }
};

function getPageStructure() {
  return document.querySelector("body").outerHTML;
  return Array.from(document.body.getElementsByTagName("*"), tagName).filter(
    function (e) {
      return ![].includes(e);
    }
  );
}

/*window.addEventListener("load", (event) => {
  let url = getUrl(window.location.href);
  let queryParams = getQueryParams(window.location.href);
  let pageStructure = getPageStructure();
  saveData({url,queryParams,pageStructure})
});*/
