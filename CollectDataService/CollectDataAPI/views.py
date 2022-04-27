from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404
from html_matcher import StyleSimilarity, MixedSimilarity
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from spmf import Spmf

from CollectDataAPI.models import WebSite, WebPage, Domain, WebPageIdentifier, WebPageIdentifierWebPage, Sequence, \
    SequenceIdentifier
from CollectDataAPI.serializers import WebSiteSerializer, WebPageSerializer, \
    DomainSerializer, WebPageIdentifierSerializer, WebPageIdentifierListSerializer, SequenceSerializer
from CollectDataAPI.utils import split_by_character_in_position, get_subsequences_gte


def create_identifiers(web_site, method):
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
    return WebPageIdentifier.objects.filter(webPages__webSite=web_site, similarityMethod=method).distinct()


def build_sequences(web_site, method):
    Sequence.objects.all().delete()
    matches = WebPageIdentifierWebPage.objects.filter(webPage__webSite=web_site,
                                                      webPageIdentifier__similarityMethod=method)
    sessions = list(matches.values_list("webPage__session_id", flat=True).distinct())
    sequences = []
    for session in sessions:
        sequence = Sequence.objects.create()
        for matching in matches.order_by("webPage__created_at"):
            if matching.webPage.session.session_key == session:
                SequenceIdentifier.objects.create(webPageIdentifier=matching.webPageIdentifier, sequence=sequence)
        sequences.append(sequence)
    return sequences


def get_sequence(identifiers, support):
    sequence = Sequence.objects.create(support=support)
    sequence.webPageIdentifiers.set(identifiers)
    return sequence


def build_sub_sequences(sequences, min_length, min_support):
    count_sequences = dict()
    for sequence in sequences:
        for sub_sequence in get_subsequences_gte(sequence.webPageIdentifiers.all(), min_length):
            count_sequences[sub_sequence] = count_sequences.get(sub_sequence, 0) + 1
    return [get_sequence(k, v) for k, v in count_sequences.items() if float(v) >= min_support]


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
        identifiers = create_identifiers(web_site, method)
        serializer = WebPageIdentifierListSerializer(identifiers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=self.get_success_headers(serializer.data))

    @action(detail=True, methods=['post'], url_path='webPage/subsequences')
    def get_web_page_most_common_subsequences(self, request, pk=None):
        web_site = self.get_object()
        length = int(request.query_params.get('length'))
        support = int(request.query_params.get('support'))
        method = request.query_params.get('method')
        identifier = WebPageIdentifierSerializer(data={'similarityMethod': method})
        identifier.is_valid(raise_exception=True)
        sequences = build_sequences(web_site, method)
        sub_sequences = build_sub_sequences(sequences, length, support)
        serializer = SequenceSerializer(sub_sequences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=self.get_success_headers(serializer.data))

    @action(detail=True, methods=['post'], url_path='webPage/testing')
    def testing(self, request, pk=None):
        input_direct = [
            [[1], [2], [3], [4], [9], [7], [8], [1], [4], [6]],
            [[1], [2], [3], [4], [5], [4], [6], [7], [8]],
            [[1], [2], [3], [4], [6], [8], [3], [7], [4]],
            [[1], [2], [3], [5], [4], [7], [8], [6], [9]],
            [[1], [2], [4], [5], [9], [7], [6], [7], [8]]
        ]
        spmf = Spmf("PrefixSpan", input_direct=input_direct, output_filename="output.txt", arguments=[0.7])
        spmf.run()
        return Response(status=status.HTTP_200_OK)


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
        domain = get_object_or_404(Domain, domain=url)
        if not request.session.exists(request.session.session_key):
            request.session.create()
        session = Session.objects.get(session_key=request.session.session_key)
        serializer.save(session=session, webSite=domain.webSite)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
