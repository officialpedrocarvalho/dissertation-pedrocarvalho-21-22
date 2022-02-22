from django.contrib.postgres.fields import ArrayField
from django.contrib.sessions.models import Session
from django.db import models


class WebSite(models.Model):
    name = models.CharField(max_length=100, primary_key=True)


class Domain(models.Model):
    domain = models.CharField(max_length=100, unique=True)
    webSite = models.ForeignKey(WebSite, on_delete=models.CASCADE, to_field='name')


class WebPage(models.Model):
    webSite = models.ForeignKey(WebSite, on_delete=models.CASCADE, to_field='name')
    pageStructure = models.JSONField()


class WebPageSpecification(models.Model):
    webPage = models.ForeignKey(WebPage, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    url = models.CharField(max_length=100)
    queryParams = ArrayField(models.CharField(max_length=10), null=True, blank=True)
    pageStructure = models.JSONField()
