from rest_framework.serializers import ModelSerializer

from CollectDataAPI.models import WebPage, WebSite, Domain, WebPageSpecification


class WebSiteSerializer(ModelSerializer):
    class Meta:
        model = WebSite
        fields = ['name', ]


class DomainSerializer(ModelSerializer):
    class Meta:
        model = Domain
        fields = ['domain', 'webSite']


class WebPageSerializer(ModelSerializer):
    class Meta:
        model = WebPage
        fields = ['webSite', 'pageStructure']


class WebPageSpecificationSerializer(ModelSerializer):
    class Meta:
        model = WebPageSpecification
        fields = ['url', 'queryParams', 'pageStructure']
