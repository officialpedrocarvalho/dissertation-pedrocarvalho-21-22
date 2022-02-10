/**
 * Function that recevies a URL and separates it from its query parameters
 * 
 * @param {string} href 
 * @returns separately url without query parameters and query parameters
 */
function getPageURL(href) {
  href = href.split("?");
  let url = href[0];
  let queryParams = href[1].split("&");
  for (let index = 0; index < queryParams.length; index++) {
    queryParams[index] = queryParams[index].split("=")[0];
  }
  return { url, queryParams };
}

console.log(getPageURL(window.location.href));