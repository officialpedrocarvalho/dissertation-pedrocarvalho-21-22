from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from CollectDataAPI.models import Data
from CollectDataAPI.serializers import DataSerializer


class DataViewSet(ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Data.objects.all()
    serializer_class = DataSerializer
    # permission_classes = [permissions.IsAuthenticated]
