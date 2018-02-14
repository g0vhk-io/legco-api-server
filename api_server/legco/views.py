from django.shortcuts import render
from .models import *
from django.db.models import Q
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from api_server.views import IndividualSerializer
from haystack.query import SearchQuerySet
from rest_framework.pagination import LimitOffsetPagination
# Create your views here.


class MotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motion
        fields = '__all__'


class VoteSerializer(serializers.ModelSerializer):
    motion = MotionSerializer(read_only=True, many=False)
    class Meta:
        model = Vote
        fields = '__all__'

class MeetingPersonelSerializer(serializers.ModelSerializer):
    individual = IndividualSerializer(read_only=True, many=False)
    class Meta:
        model = MeetingPersonel
        fields = '__all__'

class MeetingSpeechSerializer(serializers.ModelSerializer):
    individual = IndividualSerializer(read_only=True, many=False)
    others_individual = IndividualSerializer(read_only=True, many=True)
    class Meta:
        model = MeetingSpeech
        fields = '__all__'

class MeetingHansardSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingHansard
        fields = ['date', 'meeting_type', 'source_url', 'key', 'id']

class MeetingHansardDetailSerializer(serializers.ModelSerializer):
    members_present = MeetingPersonelSerializer(read_only=True, many=True)
    members_absent = MeetingPersonelSerializer(read_only=True, many=True)
    public_officers = MeetingPersonelSerializer(read_only=True, many=True)
    clerks = MeetingPersonelSerializer(read_only=True, many=True)
    speeches = MeetingSpeechSerializer(read_only=True, many=True)
    class Meta:
        model = MeetingHansard
        fields = '__all__'



class MeetingHansardsView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, year=None, format=None):
        meetings = []
        if year is not None:
            meetings =  MeetingHansard.objects.filter((Q(date__year=int(year)) & Q(date__month__gte=9)) | (Q(date__year=int(year) + 1) & Q(date__month__lt=9)))
        else:
            meetings = MeetingHansard.objects.all()
        meetings = meetings.order_by('-date')
        vote_counts = {}
        present_counts = {}
        absent_counts = {}
        for m in meetings:
            present = [p for p in m.members_present.all()]
            absent =  [p for p in m.members_absent.all()]
            votes = Vote.objects.prefetch_related('meeting').prefetch_related('motion').filter(Q(date__year = m.date.year) & Q(date__month = m.date.month) & Q(date__day = m.date.day))
            vote_counts[m.id] = len(votes)
            present_counts[m.id] = len(present)
            absent_counts[m.id] = len(absent)

        serializer = MeetingHansardSummarySerializer(meetings, many=True)
        output = serializer.data
        for meeting in output:
            meeting['vote_count'] = vote_counts[meeting['id']]
            meeting['present_count'] = present_counts[meeting['id']]
            meeting['absent_count'] = absent_counts[meeting['id']]
        return JsonResponse(output, safe=False)

class MeetingHansardView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, key=None, format=None):
        print(key)
        meeting = get_object_or_404(MeetingHansard.objects.select_related(), id=int(key))

        serializer = MeetingHansardDetailSerializer(meeting, many=False)
        return JsonResponse(serializer.data, safe=False)

class MeetingSpeechSearchView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, keyword=None, format=None):
        if keyword is not None:
            words = keyword.split(' ')
            result = SearchQuerySet()
            for word in words:
                print(word)
                result = result.filter(content__exact=word)
            result = result.models(MeetingSpeech)
            result = result.order_by('-year')
        paginator = LimitOffsetPagination()
        result = paginator.paginate_queryset(result, request)
        result = [r.object for r in result]
        serializer = MeetingSpeechSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

class VoteSearchView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, date=None, format=None):
        year, month, day = [int(s) for s in date.split('-')]
        print(year, month, day)
        votes = Vote.objects.prefetch_related('meeting').prefetch_related('motion').filter(Q(date__year = year) & Q(date__month = month) & Q(date__day = day))
        serializer = VoteSerializer(votes, many=True)
        return JsonResponse(serializer.data, safe=False)


