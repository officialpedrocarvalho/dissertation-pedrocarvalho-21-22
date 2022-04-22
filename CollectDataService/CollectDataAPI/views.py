from django.contrib.sessions.models import Session
from django.http import HttpResponseBadRequest
from html_matcher import StyleSimilarity, MixedSimilarity
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from CollectDataAPI.models import WebSite, WebPage, Domain, WebPageIdentifier, WebPageIdentifierWebPage, Sequence, \
    SequenceIdentifier
from CollectDataAPI.serializers import WebSiteSerializer, WebPageSerializer, \
    DomainSerializer, WebPageIdentifierSerializer, WebPageIdentifierListSerializer, SequenceSerializer
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
        algorithm = MixedSimilarity(WebPageIdentifier(similarityMethod=method).get_similarity_method(),
                                    StyleSimilarity(), 0.7)
        for web_page in web_site.webpage_set.all().exclude(
                webpageidentifierwebpage__webPageIdentifier__similarityMethod=method):
            found = False
            for identifier in WebPageIdentifier.objects.filter(webPages__webSite=web_site, similarityMethod=method):
                matching = algorithm.similarity(web_page.pageStructure, identifier.pageStructure)
                print(matching, web_page.url, identifier.webPages.all().first().url)
                if matching >= 0.9:
                    found = True
                    WebPageIdentifierWebPage.objects.create(webPageIdentifier=identifier, webPage=web_page,
                                                            similarity=matching)
                    break
            if not found:
                new = WebPageIdentifier.objects.create(pageStructure=web_page.pageStructure, similarityMethod=method)
                WebPageIdentifierWebPage.objects.create(webPageIdentifier=new, webPage=web_page, similarity=1.0)
        identifiers = WebPageIdentifier.objects.filter(webPages__webSite=web_site, similarityMethod=method).distinct()
        serializer = WebPageIdentifierListSerializer(identifiers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=self.get_success_headers(serializer.data))

    @action(detail=True, methods=['post'], url_path='webPage/subsequences')
    def get_web_page_most_common_subsequences(self, request, pk=None):
        web_site = self.get_object()
        method = request.query_params.get('method')
        identifier = WebPageIdentifierSerializer(data={'similarityMethod': method})
        identifier.is_valid(raise_exception=True)
        matches = WebPageIdentifierWebPage.objects.filter(webPage__webSite=web_site,
                                                          webPageIdentifier__similarityMethod=method)
        sessions = list(matches.values_list("webPage__session_id", flat=True).distinct())
        Sequence.objects.all().delete()
        sequences = []
        for session in sessions:
            sequence = Sequence.objects.create()
            for matching in matches.order_by("webPage__created_at"):
                if matching.webPage.session.session_key == session:
                    SequenceIdentifier.objects.create(webPageIdentifier=matching.webPageIdentifier, sequence=sequence)
            sequences.append(sequence)
        return Response(SequenceSerializer(sequences, many=True).data, status=status.HTTP_200_OK)


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
        try:
            domain = Domain.objects.get(domain=url)
            if not request.session.exists(request.session.session_key):
                request.session.create()
            session = Session.objects.get(session_key=request.session.session_key)
            serializer.save(session=session, webSite=domain.webSite)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Domain.DoesNotExist:
            return HttpResponseBadRequest(f"Invalid domain: {url}")
