from rest_framework.serializers import ModelSerializer

from CollectDataAPI.models import WebPage, WebSite, Domain, WebPageSpecification


class WebSiteSerializer(ModelSerializer):
    class Meta:
        model = WebSite
        fields = ['address', ]


class DomainSerializer(ModelSerializer):
    class Meta:
        model = Domain
        fields = ['domain', ]


class WebPageSerializer(ModelSerializer):
    class Meta:
        model = WebPage
        fields = ['webSite', 'pageStructure']


class WebPageSpecificationSerializer(ModelSerializer):
    class Meta:
        model = WebPageSpecification
        fields = ['webPage', 'url', 'queryParams', 'pageStructure']
