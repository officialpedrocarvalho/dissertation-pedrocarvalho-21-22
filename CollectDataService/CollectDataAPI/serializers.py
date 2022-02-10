from rest_framework.serializers import HyperlinkedModelSerializer

from CollectDataAPI.models import Data


class DataSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Data
        fields = ['url', ]
