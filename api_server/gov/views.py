from django.shortcuts import render
from rest_framework import pagination
from .models import *
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from rest_framework.pagination import LimitOffsetPagination
from django.http import HttpResponse, JsonResponse


class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = '__all__'

class ConsultationView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request):
        paginator = LimitOffsetPagination()
        result = Consultation.objects.order_by('-date')
        result_page = paginator.paginate_queryset(result, request)
        serializer = ConsultationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
