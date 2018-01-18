from django.shortcuts import render
from rest_framework.response import Response
from .models import Reply
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from django.shortcuts import get_object_or_404
# Create your views here.

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
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
