from collections import Counter

from apted import APTED, Config
from django.contrib.sessions.models import Session
from django.http import HttpResponseBadRequest
from html_similarity import similarity, style_similarity, structural_similarity
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from CollectDataAPI.models import WebSite, WebPageSpecification, Domain, WebPage
from CollectDataAPI.serializers import WebSiteSerializer, WebPageSpecificationSerializer, \
    DomainSerializer
from CollectDataAPI.utils import split_by_character_in_position, matching_ratio, matching_ratio_largest_sub_tree, \
    matching_ratio_tree_distance


class WebSiteViewSet(ModelViewSet):
    """
    API endpoint that allows WebSites to be viewed or edited.
    """
    queryset = WebSite.objects.all()
    serializer_class = WebSiteSerializer
    # permission_classes = [permissions.IsAuthenticated]


class DomainViewSet(ModelViewSet):
    """
    API endpoint that allows Domains to be viewed or edited.
    """
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    # permission_classes = [permissions.IsAuthenticated]


class WebPageSpecificationViewSet(ModelViewSet):
    """
    API endpoint that allows WebPageSpecifications to be viewed or edited.
    """
    queryset = WebPageSpecification.objects.all()
    serializer_class = WebPageSpecificationSerializer

    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        if not request.session.exists(request.session.session_key):
            request.session.create()
        session = Session.objects.get(session_key=request.session.session_key)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = split_by_character_in_position(serializer.validated_data.get('url'), "/", 3)
        domain = Domain.objects.filter(domain=url).first()
        if domain:
            web_site = domain.webSite
            web_pages = WebPage.objects.filter(webSite=web_site)
            similarity_level = 0.0
            page = None
            for web_page in web_pages:
                # matching = similarity(web_page.pageStructure, serializer.validated_data.get('pageStructure'), 0.3)
                apted = APTED(web_page.pageStructure, serializer.validated_data.get('pageStructure'), CustomConfig())
                matching = apted.compute_edit_distance()
                count = json_extract(web_page.pageStructure)
                count += json_extract(serializer.validated_data.get('pageStructure'))
                print(matching)
                print(count)
                print(1 - (matching / count))
                matching = 1 - (matching / count)
                if matching >= 0.9 and matching > similarity_level:
                    similarity_level = matching
                    page = web_page
            if similarity_level == 0.0:
                page = WebPage.objects.create(webSite=web_site,
                                              pageStructure=serializer.validated_data.get('pageStructure'))
                similarity_level = 1.0
            serializer.save(session=session, webPage=page, similarity=similarity_level)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return HttpResponseBadRequest("Invalid domain.")

    def count_elements(self, json, count=0):
        for element in json["children"]:
            self.count_elements(element, count + 1)
        return count


def json_extract(json):
    """Recursively fetch values from nested JSON."""
    values = []

    def extract(json, values):
        """Recursively search for values of key in JSON tree."""
        for element in json["children"]:
            values.append(element["tag"])
            extract(element, values)
        return values

    values = extract(json, values)
    return len(values)


def canonical_extraction(json):
    """Recursively builds a string representing the canonical form of a html web page structure."""
    values = []

    def extract(json, values):
        """Compares classes and id from the actual element with the previous one and:
            - if one of these matches the element is ignored"""
        if json["children"]:
            values.append("(")
        for count, element in enumerate(json["children"]):
            if count != 0:
                if len(element["classes"]) != 0:
                    if json["children"][count - 1]["tag"] != element["tag"] or set(
                            json["children"][count - 1]["classes"]) != set(element["classes"]):
                        values.append(element["tag"])
                        extract(element, values)
                elif len(element["id"]) != 0:
                    if json["children"][count - 1]["tag"] != element["tag"] or set(
                            json["children"][count - 1]["id"]) != set(element["id"]):
                        values.append(element["tag"])
                        extract(element, values)
                else:
                    values.append(element["tag"])
                    extract(element, values)
            else:
                values.append(element["tag"])
                extract(element, values)
        if json["children"]:
            values.append(")")
        return values

    values.append(json["tag"])
    values = extract(json, values)
    return ' '.join(values)


class CustomConfig(Config):
    def rename(self, node1, node2):
        """Compares attribute .value of trees"""
        return 1 if node1["tag"] != node2["tag"] else 0

    def children(self, node):
        """Get left and right children of binary tree"""
        return [x for x in node["children"] if x]
