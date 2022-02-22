from django.contrib.sessions.models import Session
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from CollectDataAPI.models import WebSite, WebPageSpecification, Domain
from CollectDataAPI.serializers import WebSiteSerializer, WebPageSpecificationSerializer, \
    DomainSerializer


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
        serializer.save(session=session)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
