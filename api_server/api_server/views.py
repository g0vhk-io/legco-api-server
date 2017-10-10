from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

class StatusView(APIView):
    renderer_classes = (JSONRenderer, )
    def post(self, request, format=None):
        return Response({'status': 'ok'})
