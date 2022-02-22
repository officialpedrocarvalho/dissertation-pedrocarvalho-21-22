from django.contrib.postgres.fields import ArrayField
from django.contrib.sessions.models import Session
from django.db import models


class WebSite(models.Model):
    address = models.CharField(max_length=100)


class Domain(models.Model):
    domain = models.CharField(max_length=100)
    webSite = models.ForeignKey(WebSite, on_delete=models.CASCADE)


class WebPage(models.Model):
    webSite = models.ForeignKey(WebSite, on_delete=models.CASCADE)
    pageStructure = models.JSONField()


class WebPageSpecification(models.Model):
    webPage = models.ForeignKey(WebPage, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    url = models.CharField(max_length=100)
    queryParams = ArrayField(models.CharField(max_length=10), null=True, blank=True)
    pageStructure = models.JSONField()
