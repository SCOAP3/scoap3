from rest_framework import serializers

from scoap3.articles.models import Article, ArticleIdentifier


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"


class ArticleIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleIdentifier
        fields = "__all__"
