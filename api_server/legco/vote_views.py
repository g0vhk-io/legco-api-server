import traceback as tb
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from .serializers import *
from .vote import *


class MeetingVoteUpsertView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    @transaction.atomic
    def put(self, request):
        print(request.data)
        try:
            results = upsert_votes_into_db(request.data['url'])
            results = [{'meeting': MeetingSerializer(r['meeting'], many=False).data,
                'votes': [{'vote': VoteSerializer(q['vote']).data,
                           'summaries': VoteSummarySerializer(q['summaries'], many=True).data,
                           'individual_votes': IndividualVoteSerializer(q['individual_votes'], many=True).data}
                           for q in r['votes']
                         ] ,
                'is_created': r['is_created']} for r in results]
            return JsonResponse(results, safe=False)
        except Exception as e:
            tb.print_exc()
            m = repr(e)
            print(m)
            return JsonResponse({'message': m}, safe=False)

