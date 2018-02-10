from django.shortcuts import render
from .models import News
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class NewsView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request):
        paginator = LimitOffsetPagination()
        result = News.objects.order_by('-date')
        result_page = paginator.paginate_queryset(result, request)
        serializer = NewsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
