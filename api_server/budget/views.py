from django.shortcuts import render
from rest_framework.response import Response
from .models import Reply, Meeting, Bureau
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.db.models import Q
# Create your views here.

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = '__all__'

class BureauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bureau
        fields = '__all__'

class RepliesView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, key=None, format=None):
        serializer = None
        if key is not None:
            reply = get_object_or_404(Reply, key=key)
            serializer = ReplySerializer(reply, many=False)
        else:
            replies = Reply.objects.all()
            for reply in replies:
                reply.question = reply.question[0:100]
                reply.answer = reply.answer[0:100]
            serializer = ReplySerializer(replies, many=True)
        return JsonResponse(serializer.data, safe=False)


class RepliesYearBureauView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, year=None, bureau=None, format=None):
        replies = []
        if year is not None and bureau is not None:
            replies = Reply.objects.filter(Q(year=int(year)) & Q(bureau=bureau))
        for reply in replies:
            reply.question = reply.question[0:100]
            reply.answer = reply.answer[0:100]
        serializer = ReplySerializer(replies, many=True)
        return JsonResponse(serializer.data, safe=False)



class MeetingSerializer(serializers.ModelSerializer):
    bureau = BureauSerializer()
    class Meta:
        model = Meeting
        fields = '__all__'

class MeetingsView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, year=None, format=None):
        meetings = []
        if year is not None:
            meetings =  Meeting.objects.filter(year=int(year)).select_related()
        else:
            meetings = Meeting.objects.all().select_related()

        serializer = MeetingSerializer(meetings, many=True)
        return JsonResponse(serializer.data, safe=False)
