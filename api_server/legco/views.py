from django.shortcuts import render
from .models import *
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
# Create your views here.

class MeetingHansardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingHansard
        fields = ['date', 'meeting_type', 'source_url', 'key', 'id']



class MeetingHansardsView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, year=None, format=None):
        meetings = []
        if year is not None:
            meetings =  MeetingHansard.objects.filter(date__year=int(year))
        else:
            meetings = MeetingHansard.objects.all().select_related()

        serializer = MeetingHansardSerializer(meetings, many=True)
        return JsonResponse(serializer.data, safe=False)


