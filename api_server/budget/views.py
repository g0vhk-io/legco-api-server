from django.shortcuts import render
from rest_framework.response import Response
from .models import Reply, Meeting, Bureau
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.db.models import Q
from haystack.query import SearchQuerySet
from django.utils.html import strip_tags
from django.template import loader
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
    def get(self, request, key=None, keyword=None, format=None):
        serializer = None
        if key is not None:
            reply = get_object_or_404(Reply, key=key)
            serializer = ReplySerializer(reply, many=False)
        elif keyword is not None:
            offset = int(request.GET.get('offset','0')) 
            limit = int(request.GET.get('limit','10'))
            result = SearchQuerySet().filter(content=keyword).models(Reply)
            result = result[offset:(offset+limit)]
            result = [r.object for r in result]
            for reply in result:
                reply.question = strip_tags(reply.question)[0:100]
                reply.answer = strip_tags(reply.answer)[0:100]
            serializer = ReplySerializer(result, many=True)
        else:
            serializer = ReplySerializer([], many=True)
        return JsonResponse(serializer.data, safe=False)


class RepliesKeywordView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, keyword=None, format=None):
        result = []
        total = 0
        offset = int(request.GET.get('offset','0')) 
        limit = int(request.GET.get('limit','10'))
        if keyword is not None:
            result = SearchQuerySet().filter(content=keyword).models(Reply)
            total = result.count()
            result = result[offset:(offset+limit)]
            result = [r.object for r in result]
            for reply in result:
                reply.question = strip_tags(reply.question)[0:100]
                reply.answer = strip_tags(reply.answer)[0:100]
        serializer = ReplySerializer(result, many=True)
        return JsonResponse({'data': serializer.data, 'total': total , 'limit': limit, 'offset': offset}, safe=False)

class RepliesYearBureauView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, year=None, bureau=None, format=None):
        replies = []
        total = 0
        if year is not None and bureau is not None:
            offset = int(request.GET.get('offset','0')) 
            limit = int(request.GET.get('limit','10'))
            replies = Reply.objects.filter(Q(year=int(year)) & Q(bureau=bureau))
            total = replies.count()
            replies = replies[offset:(offset + limit)]

        for reply in replies:
            reply.question = strip_tags(reply.question)[0:100]
            reply.answer = strip_tags(reply.answer)[0:100]
        serializer = ReplySerializer(replies, many=True)
        return JsonResponse({'data': serializer.data, 'total': total , 'limit': limit, 'offset': offset}, safe=False)



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

class SharerView(APIView):
    def get(self, request, key=None):
        reply = get_object_or_404(Reply, key=key)
        template = loader.get_template('budget/sharer.html')
        context = {
          'url': 'http://budgetq.g0vhk.io/reply/' + key,
          'title': str(reply.year) + '年開支預算問題/' + reply.head + '/' + reply.member,
          'description': reply.member + ':' + strip_tags(reply.question)[0:100],
          'image': 'http://budgetq.g0vhk.io/gov_bg.png'
        }
        return HttpResponse(template.render(context, request))
