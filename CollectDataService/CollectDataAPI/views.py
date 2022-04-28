import itertools

from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404
from html_matcher import StyleSimilarity, MixedSimilarity
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from CollectDataAPI.models import WebSite, WebPage, Domain, WebPageIdentifier, WebPageIdentifierWebPage, Sequence, \
    SequenceIdentifier
from CollectDataAPI.serializers import WebSiteSerializer, WebPageSerializer, \
    DomainSerializer, WebPageIdentifierSerializer, WebPageIdentifierListSerializer, SequenceSerializer
from CollectDataAPI.utils import split_by_character_in_position, get_subsequences_gte


def create_identifiers(web_site, method, weight, similarity_offset):
    algorithm = MixedSimilarity(WebPageIdentifier(similarityMethod=method).get_similarity_method(),
                                StyleSimilarity(), weight)
    for web_page in web_site.webpage_set.all().exclude(
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


def get_significant_sub_sequences(sub_sequences):
    significant_sub_sequences = [sequence for sequence in sub_sequences]
    for a, b in itertools.combinations(sub_sequences, 2):
        if set(a.webPageIdentifiers.all()).issubset(b.webPageIdentifiers.all()):
            significant_sub_sequences.remove(a) if a in significant_sub_sequences else None
        elif set(b.webPageIdentifiers.all()).issubset(a.webPageIdentifiers.all()):
            significant_sub_sequences.remove(b) if b in significant_sub_sequences else None
    return significant_sub_sequences


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
        weight = float(request.query_params.get('weight'))
        similarity_offset = float(request.query_params.get('offset'))
        identifier = WebPageIdentifierSerializer(data={'similarityMethod': method})
        identifier.is_valid(raise_exception=True)
        identifiers = create_identifiers(web_site, method, weight, similarity_offset)
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
        #significant_sub_sequences = get_significant_sub_sequences(sub_sequences)
        serializer = SequenceSerializer(sub_sequences, many=True)
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
        domain = get_object_or_404(Domain, domain=url)
        if not request.session.exists(request.session.session_key):
            request.session.create()
        session = Session.objects.get(session_key=request.session.session_key)
        serializer.save(session=session, webSite=domain.webSite)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
