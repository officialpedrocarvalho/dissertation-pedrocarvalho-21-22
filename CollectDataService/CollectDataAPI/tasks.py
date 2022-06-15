from django.db.models import Count
from html_matcher import MixedSimilarity, StyleSimilarity

from CollectDataAPI.models import WebPageIdentifier, WebPageIdentifierWebPage, WebSite
from CollectDataService.celery import app


@app.task
def create_identifiers(web_site, method, weight, similarity_offset):
    algorithm = MixedSimilarity(WebPageIdentifier(similarityMethod=method).get_similarity_method(), StyleSimilarity(),
                                weight)
    web_pages = WebSite.objects.get(pk=web_site).webpage_set.all().exclude(
        webpageidentifierwebpage__webPageIdentifier__similarityMethod=method)
    for web_page in web_pages:
        found = False
        same_url = WebPageIdentifier.objects.filter(webPages__webSite=web_site, similarityMethod=method,
                                                    webPages__url=web_page.url)
        if same_url:
            print("SAME URL", web_page.url, same_url.first().url)
            WebPageIdentifierWebPage.objects.create(webPageIdentifier=same_url.first(), webPage=web_page,
                                                    similarity=1.0)
            continue
        identifiers = WebPageIdentifier.objects.filter(webPages__webSite=web_site, similarityMethod=method).annotate(
            count=Count('webPages')).order_by('-count').distinct()
        for identifier in identifiers:
            print("Here")
            matching = algorithm.similarity(web_page.pageStructure, identifier.pageStructure)
            print(matching, web_page.url, identifier.url)
            if matching >= similarity_offset:
                found = True
                WebPageIdentifierWebPage.objects.create(webPageIdentifier=identifier, webPage=web_page,
                                                        similarity=matching)
                break
        if not found:
            new = WebPageIdentifier.objects.create(pageStructure=web_page.pageStructure, similarityMethod=method,
                                                   url=web_page.url)
            WebPageIdentifierWebPage.objects.create(webPageIdentifier=new, webPage=web_page, similarity=1.0)
