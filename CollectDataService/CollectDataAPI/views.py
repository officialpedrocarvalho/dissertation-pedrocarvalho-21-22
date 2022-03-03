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
                matching = similarity(web_page.pageStructure, serializer.validated_data.get('pageStructure'), 0.3)
                print(matching)
                if matching >= 0.4 & matching > similarity_level:
                    similarity_level = matching
                    page = web_page
            if similarity_level == 0.0:
                page = WebPage.objects.create(webSite=web_site,
                                              pageStructure=serializer.validated_data.get('pageStructure'))
            serializer.save(session=session, webPage=page, similarity=similarity_level)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return HttpResponseBadRequest("Invalid domain.")
