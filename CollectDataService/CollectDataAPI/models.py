from django.contrib.postgres.fields import ArrayField
from django.db import models


class Data(models.Model):
    domain = models.CharField(max_length=100)
    queryParams = ArrayField(models.CharField(max_length=10), null=True, blank=True)
