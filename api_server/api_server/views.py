from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from haystack.query import SearchQuerySet   
from django.http import HttpResponse, JsonResponse
import json
from legco.models import *
from rest_framework import serializers

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ('name_ch', 'name_en', 'id')

class IndividualSerializer(serializers.ModelSerializer):
    party = PartySerializer(many=False, read_only=True)
    class Meta:
        model = Party
        fields = ('name_ch', 'name_en', 'id', 'image', 'party')

class StatusView(APIView):
    renderer_classes = (JSONRenderer, )
    def post(self, request, format=None):
        return Response({'status': 'ok'})

class PartyView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, format=None):
        parties = Party.objects.all()
        serializer = PartySerializer(parties, many=True)
        return JsonResponse(serializer.data, safe=False)

class IndividualView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, format=None):
        individuals = Individual.objects.all()
        serializer = IndividualSerializer(individuals, many=True)
        return JsonResponse(serializer.data, safe=False)


