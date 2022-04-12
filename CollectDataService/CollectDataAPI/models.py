from django.contrib.postgres.fields import ArrayField
from django.contrib.sessions.models import Session
from django.db import models


class WebSite(models.Model):
    name = models.CharField(max_length=100, primary_key=True)


class Domain(models.Model):
    webSite = models.ForeignKey(WebSite, on_delete=models.CASCADE, to_field='name')
    domain = models.URLField(unique=True)


class WebPageIdentifier(models.Model):
    pageStructure = models.JSONField()


class WebPage(models.Model):
    webSite = models.ForeignKey(WebSite, on_delete=models.CASCADE, to_field='name')
    webPageIdentifier = models.ForeignKey(WebPageIdentifier, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    url = models.URLField()
    queryParams = ArrayField(models.CharField(max_length=100, null=True, blank=True), null=True, blank=True)
    pageStructure = models.JSONField()
    similarity = models.DecimalField(decimal_places=2, max_digits=3, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
