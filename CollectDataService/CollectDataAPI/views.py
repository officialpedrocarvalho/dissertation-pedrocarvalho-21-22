from django.contrib.sessions.models import Session
from django.db.models import Count
from django.shortcuts import get_object_or_404
from html_matcher import StyleSimilarity, MixedSimilarity
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from CollectDataAPI.tasks import create_identifiers

from CollectDataAPI.models import WebSite, WebPage, Domain, WebPageIdentifier, WebPageIdentifierWebPage, Sequence, \
    SequenceIdentifier
from CollectDataAPI.serializers import WebSiteSerializer, WebPageSerializer, \
    DomainSerializer, WebPageIdentifierSerializer, WebPageIdentifierListSerializer, SequenceSerializer
from CollectDataAPI.utils import split_by_character_in_position, get_subsequences_gte


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
    [SequenceIdentifier.objects.create(webPageIdentifier=identifier, sequence=sequence) for identifier in identifiers]
    return sequence


def build_subsequences(sequences, min_length, min_support):
    count_sequences = dict()
    for sequence in sequences:
        for sub_sequence in get_subsequences_gte(sequence.webPageIdentifiers.all(), min_length):
            count_sequences[sub_sequence] = count_sequences.get(sub_sequence, 0) + 1
    return [get_sequence(k, v) for k, v in count_sequences.items() if float(v) >= min_support]


def contains_subsequence(subsequence, sequence):
    sub = "".join(map(str, subsequence.values_list("pk", flat=True)))
    seq = "".join(map(str, sequence.values_list("pk", flat=True)))
    return sub in seq


def get_significant_subsequences(subsequences):
    subsequences = list(Sequence.objects.filter(id__in={instance.id for instance in subsequences}).annotate(
        count=Count('webPageIdentifiers')).order_by('-count'))
    insignificant_subsequences = []
    for i in range(len(subsequences)):
        if subsequences[i] in insignificant_subsequences:
            continue
        for j in range(i + 1, len(subsequences)):
            if subsequences[j] in insignificant_subsequences:
                continue
            if contains_subsequence(subsequences[i].webPageIdentifiers.all(), subsequences[j].webPageIdentifiers.all()):
                insignificant_subsequences.append(subsequences[i])
            elif contains_subsequence(subsequences[j].webPageIdentifiers.all(),
                                      subsequences[i].webPageIdentifiers.all()):
                insignificant_subsequences.append(subsequences[j])
    return [subsequence for subsequence in subsequences if subsequence not in insignificant_subsequences]


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
        identifiers = create_identifiers.delay(web_site.pk, method, weight, similarity_offset)
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
        print("1")
        subsequences = build_subsequences(sequences, length, support)
        print("2")
        significant_subsequences = get_significant_subsequences(subsequences)
        print("3")
        serializer = SequenceSerializer(significant_subsequences, many=True)
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
