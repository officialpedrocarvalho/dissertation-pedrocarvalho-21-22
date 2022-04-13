from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from CollectDataAPI.views import WebSiteViewSet, DomainViewSet, WebPageViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'domain', DomainViewSet)
router.register(r'webSite', WebSiteViewSet)
router.register(r'webPage', WebPageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
