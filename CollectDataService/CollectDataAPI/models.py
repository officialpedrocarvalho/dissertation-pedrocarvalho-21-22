from django.contrib.postgres.fields import ArrayField
from django.contrib.sessions.models import Session
from django.db import models
from html_matcher import LongestCommonSequence, LongestCommonSequenceOptimized, AllPathTreeEditDistance, \
    AllPathTreeEditDistanceOptimized
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class WebSite(models.Model):
    name = models.CharField(max_length=100, primary_key=True)


class Domain(models.Model):
    webSite = models.ForeignKey(WebSite, on_delete=models.CASCADE, to_field='name')
    domain = models.URLField(unique=True)


class WebPage(models.Model):
    webSite = models.ForeignKey(WebSite, on_delete=models.CASCADE, to_field='name')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    url = models.URLField()
    pageStructure = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class WebPageIdentifier(models.Model):
    class SimilarityMethods(models.TextChoices):
        LCS = '1', 'LCS'
        APTED = '2', 'APTED'
        LCS_OPTIMIZED = '3', 'LCS_Optimized'
        APTED_OPTIMIZED = '4', 'APTED_Optimized'

    webPages = models.ManyToManyField(WebPage, through='Matching')
    pageStructure = models.TextField()
    similarityMethod = models.CharField(max_length=2, choices=SimilarityMethods.choices,
                                        default=SimilarityMethods.LCS_OPTIMIZED)

    def get_similarity_method(self):
        if self.similarityMethod == '1':
            return LongestCommonSequence()
        elif self.similarityMethod == '2':
            return AllPathTreeEditDistance()
        elif self.similarityMethod == '3':
            return LongestCommonSequenceOptimized()
        elif self.similarityMethod == '4':
            return AllPathTreeEditDistanceOptimized()
        else:
            raise serializers.ValidationError("Similarity method does not exist")


class Matching(models.Model):
    webPage = models.ForeignKey(WebPage, on_delete=models.CASCADE)
    webPageIdentifier = models.ForeignKey(WebPageIdentifier, on_delete=models.CASCADE)
    similarity = models.DecimalField(decimal_places=2, max_digits=3)
    created_at = models.DateTimeField(auto_now_add=True)
