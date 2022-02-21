from rest_framework.serializers import ModelSerializer

from CollectDataAPI.models import WebPage, WebSite


class WebSiteSerializer(ModelSerializer):
    class Meta:
        model = WebSite
        fields = ['domain', ]


class WebPageSerializer(ModelSerializer):
    class Meta:
        model = WebPage
        fields = ['webSite', 'url', 'queryParams', 'pageStructure']
