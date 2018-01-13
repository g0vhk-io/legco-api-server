from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from haystack.query import SearchQuerySet   
from django.http import HttpResponse
import json

class StatusView(APIView):
    renderer_classes = (JSONRenderer, )
    def post(self, request, format=None):
        return Response({'status': 'ok'})

class PartyView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, format=None):
        result = SearchQuerySet().filter(content='民')
        offset = int(request.GET.get('offset','0')) 
        limit = int(request.GET.get('limit','10'))
        sort = request.GET.get('sort', "")
        order = request.GET.get('order', "")
        if sort != "" and order != "":
            if order == 'desc':
                result = result.order_by("-" + sort)
            else:
                result = result.order_by(sort)
        total = result.count()
        result = result[offset:(offset+limit)]
        return HttpResponse(json.dumps({'total': total, 'rows':[{'score': x.score, 'id': x.object.id, 'name_ch': x.object.name_ch } for x in result][0:100]}))
