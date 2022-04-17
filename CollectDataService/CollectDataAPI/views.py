from django.contrib.sessions.models import Session
from django.http import HttpResponseBadRequest
from html_matcher import StyleSimilarity, MixedSimilarity
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from CollectDataAPI.models import WebSite, WebPage, Domain, WebPageIdentifier, Matching
from CollectDataAPI.serializers import WebSiteSerializer, WebPageSerializer, \
    DomainSerializer, WebPageIdentifierSerializer, WebPageIdentifierListSerializer
from CollectDataAPI.utils import split_by_character_in_position


class WebSiteViewSet(ModelViewSet):
    """
    API endpoint that allows WebSites to be viewed or edited.
    """
    queryset = WebSite.objects.all()
    serializer_class = WebSiteSerializer

    @action(detail=True, methods=['post'], url_path='webPage/similarity')
    def create_web_page_similarity_ids(self, request, pk=None):
        web_site = self.get_object()
        method = request.query_params.get('method')
        identifier = WebPageIdentifierSerializer(data={'similarityMethod': method})
        identifier.is_valid(raise_exception=True)
        style = StyleSimilarity()
        algorithm = MixedSimilarity(WebPageIdentifier(identifier).get_similarity_method(), style, 0.5)
        for web_page in web_site.webpage_set.all():
            found = False
            similarity_level = 0.0
            identifiers = WebPageIdentifier.objects.filter(webPages__webSite=web_site, similarityMethod=method)
            for identifier in identifiers:
                if Matching.objects.filter(webPage=web_page, webPageIdentifier=identifier):
                    found = True
                    break
                matching = algorithm.similarity(web_page.pageStructure, identifier.pageStructure)
                if matching >= 0.9 and matching > similarity_level:
                    similarity_level = matching
                    found = True
                    Matching.objects.create(webPageIdentifier=identifier, webPage=web_page, similarity=matching)
            if not found:
                identifier = WebPageIdentifier.objects.create(pageStructure=web_page.pageStructure,
                                                              similarityMethod=method)
                Matching.objects.create(webPageIdentifier=identifier, webPage=web_page, similarity=1.0)
        identifiers = WebPageIdentifier.objects.filter(webPages__webSite=web_site, similarityMethod=method).distinct()
        serializer = WebPageIdentifierListSerializer(identifiers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=self.get_success_headers(serializer.data))


class DomainViewSet(ModelViewSet):
    """
    API endpoint that allows Domains to be viewed or edited.
    """
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class WebPageViewSet(ModelViewSet):
    """
    API endpoint that allows WebPages to be viewed or edited.
    """
    queryset = WebPage.objects.all()
    serializer_class = WebPageSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = split_by_character_in_position(serializer.validated_data.get('url'), "/", 3)
        domain = Domain.objects.filter(domain=url).first()
        if domain:
            if not request.session.exists(request.session.session_key):
                request.session.create()
            session = Session.objects.get(session_key=request.session.session_key)
            serializer.save(session=session, webSite=domain.webSite)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return HttpResponseBadRequest("Invalid domain")
