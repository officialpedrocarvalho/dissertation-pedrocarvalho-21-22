from html_matcher import MixedSimilarity, StyleSimilarity

from CollectDataAPI.models import WebPageIdentifier, WebPageIdentifierWebPage, WebSite
from CollectDataService.celery import app


@app.task
def create_identifiers(web_site, method, weight, similarity_offset):
    algorithm = MixedSimilarity(WebPageIdentifier(similarityMethod=method).get_similarity_method(), StyleSimilarity(),
                                weight)
    for web_page in WebSite.objects.get(pk=web_site).webpage_set.all().exclude(
            webpageidentifierwebpage__webPageIdentifier__similarityMethod=method):
        found = False
        for identifier in WebPageIdentifier.objects.filter(webPages__webSite=web_site, similarityMethod=method):
            matching = algorithm.similarity(web_page.pageStructure, identifier.pageStructure)
            print(matching, web_page.url, identifier.webPages.all().first().url)
            if matching >= similarity_offset:
                found = True
                WebPageIdentifierWebPage.objects.create(webPageIdentifier=identifier, webPage=web_page,
                                                        similarity=matching)
                break
        if not found:
            new = WebPageIdentifier.objects.create(pageStructure=web_page.pageStructure, similarityMethod=method)
            WebPageIdentifierWebPage.objects.create(webPageIdentifier=new, webPage=web_page, similarity=1.0)
    return WebPageIdentifier.objects.filter(webPages__webSite=web_site, similarityMethod=method).distinct()
