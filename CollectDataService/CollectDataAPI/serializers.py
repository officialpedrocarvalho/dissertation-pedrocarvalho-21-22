from rest_framework.serializers import ModelSerializer

from CollectDataAPI.models import WebPageIdentifier, WebSite, Domain, WebPage


class WebSiteSerializer(ModelSerializer):
    class Meta:
        model = WebSite
        fields = ['name', ]


class DomainSerializer(ModelSerializer):
    class Meta:
        model = Domain
        fields = ['domain', 'webSite']


class WebPageIdentifierSerializer(ModelSerializer):
    class Meta:
        model = WebPageIdentifier
        fields = ['pageStructure']


class WebPageSerializer(ModelSerializer):
    class Meta:
        model = WebPage
        fields = ['url', 'queryParams', 'pageStructure']
