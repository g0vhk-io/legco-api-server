from django.shortcuts import render
from .models import *
from django.db.models import Count
from django.db.models import Q
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from api_server.views import IndividualSerializer
from haystack.query import SearchQuerySet
from rest_framework.pagination import LimitOffsetPagination
from datetime import date
# Create your views here.


class VoteSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteSummary
        fields = '__all__'



class IndividualVoteSerializer(serializers.ModelSerializer):
    individual = IndividualSerializer(read_only=True, many=False)
    class Meta:
        model = IndividualVote
        fields = '__all__'



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

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['keyword']

class QuestionSerializer(serializers.ModelSerializer):
    individual = IndividualSerializer(read_only=True, many=False)
    keywords = KeywordSerializer(read_only=True, many=True)
    class Meta:
        model = Question
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
    def get(self, request, date=None, year=None, format=None):
        votes = Vote.objects.prefetch_related('meeting').prefetch_related('motion')
        if date is not None:
            year, month, day = [int(s) for s in date.split('-')]
            votes = votes.filter(Q(date__year = year) & Q(date__month = month) & Q(date__day = day))
        elif year is not None:
            year = int(year)
            votes = votes.filter(date__year=year)
        else:
            votes = []
        serializer = VoteSerializer(votes, many=True)
        return JsonResponse(serializer.data, safe=False)

class VoteDetailView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, key=None, format=None):
        yes_count = 0
        no_count = 0
        present_count = 0
        abstain_count = 0
        absent_count = 0
        overall_result = ""
        key = int(key)
        individual_votes = IndividualVote.objects.prefetch_related('individual').filter(vote__id = key)
        vote = Vote.objects.prefetch_related('meeting').prefetch_related('motion').get(pk = key)
        summaries = VoteSummary.objects.filter(vote__id = key)
        total_count = individual_votes.count()
        for summary in summaries:
            yes_count += summary.yes_count
            no_count  += summary.no_count
            abstain_count += summary.abstain_count
            present_count += summary.present_count
            if summary.summary_type == VoteSummary.OVERALL:
                overall_result = summary.result
        absent_count = total_count - present_count
        present_vote_count = present_count - yes_count - no_count - abstain_count
        yes_individuals = [iv.individual for iv in individual_votes if iv.result == "YES"]
        no_individuals = [iv.individual for iv in individual_votes if iv.result == "NO"]
        other_individuals = [iv.individual for iv in individual_votes if iv.result not in ["YES", "NO"]]
        serializer = IndividualVoteSerializer(individual_votes, many=True)
        vote_serializer = VoteSerializer(vote, many=False)
        vote_summary_serializer = VoteSummarySerializer(summaries, many=True)
        return JsonResponse({'vote': vote_serializer.data, 'individual_votes': serializer.data, 'summaries': vote_summary_serializer.data, 'yes_count': yes_count, 'no_count': no_count, 'abstain_count': abstain_count, 'absent_count': absent_count, 'overall_result': overall_result, 'present_vote_count': present_vote_count, 'id': key}, safe=False)


class AbsentView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, format=None):
        size = int(request.query_params.get("size", 5))
        query = MeetingHansard.objects.all()
        from_year = None
        to_year = None
        if "from" in request.query_params and "to" in request.query_params:
            from_year = int(request.query_params["from"])
            to_year = int(request.query_params["to"])
            if from_year >= to_year:
                from_year = None
                to_year = None

        today = date.today()
        if from_year is None:
            from_year = int(today.year / 4) * 4
        if to_year is None:
            to_year = from_year + 4
        condition = Q(pk__isnull=True)
        for year in range(from_year, to_year):
            condition = condition | (Q(date__gt=date(year, 9, 10)) & Q(date__lte=date(year + 1, 9, 9)))
        query = query.filter(condition)
        meeting_total = query.count()
        absent_total =  query.all() \
        .values('members_absent__individual__pk', 'members_absent__individual__name_ch', 'members_absent__individual__image') \
        .annotate(dcount=Count('members_absent__individual__pk')).order_by('-dcount')
        result = []
        for d in absent_total:
            pk = d['members_absent__individual__pk']
            name_ch = d['members_absent__individual__name_ch']
            image = d['members_absent__individual__image']
            dcount = d['dcount']
            if pk is None:
                continue
            result.append({'id': pk, 'name': name_ch, 'total': dcount, 'image': image, 'max': meeting_total})
        return JsonResponse(result[0:size], safe=False)

class SpeakView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, from_year=None, to_year=None, format=None):
        size = int(request.query_params.get("size", 5))
        today = date.today()
        from_year = None
        to_year = None
        if "from" in request.query_params and "to" in request.query_params:
            from_year = int(request.query_params["from"])
            to_year = int(request.query_params["to"])
            if from_year >= to_year:
                from_year = None
                to_year = None
        if from_year is None:
            from_year = int(today.year / 4) * 4
        if to_year is None:
            to_year = from_year + 4
        condition = Q(pk__isnull=True)
        for year in range(from_year, to_year):
            condition = condition | (Q(hansard__date__gt=date(year, 9, 10)) & Q(hansard__date__lte=date(year + 1, 9, 9)))
        query = MeetingSpeech.objects.filter(condition)
        speech_total =  query.values('individual__pk', 'individual__name_ch', 'individual__image').annotate(dcount=Count('individual__pk')).order_by('-dcount')
        result = []
        m = max([d['dcount'] for d in speech_total])
        for d in speech_total:
            pk = d['individual__pk']
            name_ch = d['individual__name_ch']
            dcount = d['dcount']
            image = d['individual__image']
            result.append({'id': pk, 'name': name_ch, 'total': dcount, 'max': m, 'image': image})
        return JsonResponse(result[0:size], safe=False)

class ImportantMotionView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, format=None):
        data = []
        motions = ImportantMotion.objects.select_related('motion').values_list('motion__name_ch', 'motion__vote__date', 'motion__vote__pk').order_by('-motion__vote__date')
        summaries = VoteSummary.objects.filter(Q(vote__pk__in = [m[2] for m in motions]) & Q(summary_type = VoteSummary.OVERALL))
        result_dict = {s.vote_id: s.result for s in summaries}
        for motion in motions:
            data.append({'title_ch': motion[0], 'date': motion[1], 'id': motion[2], 'result': result_dict[motion[2]]})
        return JsonResponse({'data':data}, safe=False)


class QuestionSearchView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, keyword=None, format=None):
        if keyword is not None:
            words = keyword.split(' ')
            result = SearchQuerySet()
            for word in words:
                print(word)
                result = result.filter(content__exact=word)
            result = result.models(Question)
            result = result.order_by('-year')
        paginator = LimitOffsetPagination()
        result = paginator.paginate_queryset(result, request)
        result = [r.object for r in result]
        serializer = QuestionSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

class QuestionView(APIView):
    renderer_classes = (JSONRenderer, )
    def get(self, request, key=None, format=None):
        question = get_object_or_404(Question.objects, key=key)
        serializer = QuestionSerializer(question, many=False)
        return JsonResponse(serializer.data, safe=False)

