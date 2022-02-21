from django.contrib.sessions.models import Session
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from CollectDataAPI.models import WebPage, WebSite
from CollectDataAPI.serializers import WebPageSerializer, WebSiteSerializer


class WebSiteViewSet(ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = WebSite.objects.all()
    serializer_class = WebSiteSerializer
    # permission_classes = [permissions.IsAuthenticated]


class WebPageViewSet(ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = WebPage.objects.all()
    serializer_class = WebPageSerializer

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
