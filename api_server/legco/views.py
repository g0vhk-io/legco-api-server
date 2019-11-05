from django.shortcuts import render
from django.db.models import Count, Min, Max
from django.db.models import Q
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import JSONRenderer
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound
from haystack.query import SearchQuerySet
from rest_framework.pagination import LimitOffsetPagination
from datetime import date
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from legco.models import Meeting, Vote, Motion, Individual, IndividualVote, VoteSummary
from django.db.models import Q
from django.db.models.functions import ExtractMonth, ExtractYear
from .models import *
from .hansard import *
from .question import *
from .serializers import *


def get_present_count_by_key(from_year=None, to_year=None, key=None):
    if key is not None:
         query = MeetingHansard.objects.filter(
             (Q(members_present__individual__pk=key)))
    else:
         query = MeetingHansard.objects.all()
    from_year = None
    to_year = None
    if from_year is not None and to_year is not None:
        from_year = int(from_year)
        to_year = int(to_year)
        if from_year >= to_year:
            from_year = None
            to_year = None

    today = date.today()
    if from_year is None:
        from_year = today.year // 4 * 4
    if to_year is None:
        to_year = from_year + 4
    condition = Q(pk__isnull=True)
    for year in range(from_year, to_year):
        condition = condition | (Q(date__gt=date(year, 9, 10)) & Q(
            date__lte=date(year + 1, 9, 9)))
    query = query.filter(condition)
    meeting_total = query.count()
    present_total = query.all() \
        .values('members_present__individual__pk', 'members_present__individual__name_ch', 'members_present__individual__image') \
        .annotate(dcount=Count('members_present__individual__pk')).order_by('members_present__individual__pk')
    result = []
    for d in present_total:
        pk = d['members_present__individual__pk']
        name_ch = d['members_present__individual__name_ch']
        image = d['members_present__individual__image']
        dcount = d['dcount']
        if pk is None:
            continue
        result.append({'id': pk, 'name': name_ch, 'total': dcount,
                       'image': image, 'max': meeting_total})

    if key is not None:
        result = result[0]  # Fine to return error if there is None
    return result



class MeetingHansardsView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, year=None, format=None):
        meetings = []
        if year is not None:
            meetings = MeetingHansard.objects.filter((Q(date__year=int(year)) & Q(
                date__month__gte=9)) | (Q(date__year=int(year) + 1) & Q(date__month__lt=9)))
        else:
            meetings = MeetingHansard.objects.all()
        meetings = meetings.order_by('-date')
        vote_counts = {}
        present_counts = {}
        absent_counts = {}
        for m in meetings:
            present = [p for p in m.members_present.all()]
            absent = [p for p in m.members_absent.all()]
            votes = Vote.objects.prefetch_related('meeting').prefetch_related('motion').filter(
                Q(date__year=m.date.year) & Q(date__month=m.date.month) & Q(date__day=m.date.day))
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
        meeting = get_object_or_404(
            MeetingHansard.objects.select_related(), id=int(key))

        serializer = MeetingHansardDetailSerializer(meeting, many=False)
        return JsonResponse(serializer.data, safe=False)


class MeetingHansardUpsertView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        hansard,  created = upsert_hansard_json_into_db(request.data)
        output = {'created': created}
        return JsonResponse(output, safe=False)


class QuestionUpsertView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        question,  created = upsert_question_json_into_db(request.data)
        output = {'created': created, 'key': None if question is None else question.pk}
        return JsonResponse(output, safe=False)


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
        votes = Vote.objects.prefetch_related(
            'meeting').prefetch_related('motion')
        if date is not None:
            year, month, day = [int(s) for s in date.split('-')]
            votes = votes.filter(Q(date__year=year) & Q(
                date__month=month) & Q(date__day=day))
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
        overall_result = ''
        key = int(key)
        individual_votes = IndividualVote.objects.prefetch_related(
            'individual').filter(vote__id=key)
        vote = Vote.objects.prefetch_related(
            'meeting').prefetch_related('motion').get(pk=key)
        summaries = VoteSummary.objects.filter(vote__id=key)
        total_count = individual_votes.count()
        for summary in summaries:
            yes_count += summary.yes_count
            no_count += summary.no_count
            abstain_count += summary.abstain_count
            present_count += summary.present_count
            if summary.summary_type == VoteSummary.OVERALL:
                overall_result = summary.result
        absent_count = total_count - present_count
        present_vote_count = present_count - yes_count - no_count - abstain_count
        yes_individuals = [
            iv.individual for iv in individual_votes if iv.result == 'YES']
        no_individuals = [
            iv.individual for iv in individual_votes if iv.result == 'NO']
        other_individuals = [
            iv.individual for iv in individual_votes if iv.result not in ['YES', 'NO']]
        serializer = IndividualVoteSerializer(individual_votes, many=True)
        vote_serializer = VoteSerializer(vote, many=False)
        vote_summary_serializer = VoteSummarySerializer(summaries, many=True)
        return JsonResponse({'vote': vote_serializer.data, 'individual_votes': serializer.data, 'summaries': vote_summary_serializer.data, 'yes_count': yes_count, 'no_count': no_count, 'abstain_count': abstain_count, 'absent_count': absent_count, 'overall_result': overall_result, 'present_vote_count': present_vote_count, 'id': key}, safe=False)


class LatestVotesView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, key=None):
        size = int(request.query_params.get('size', 5))
        condition = (Q(individual_id=key) & ~Q(result='ABSENT'))
        individual_votes = IndividualVote.objects.filter(condition) \
            .prefetch_related('vote').order_by('-vote__date', '-vote__time')[:size]  # .order_by('-vote__date', '-vote__time')
        result = []
        for d in individual_votes:
            # vote = individual_votes.vote
            #voteDate = str(individual_votes.date)
            #motion = individual_votes.name_ch
            voteResult = VoteSummary.objects.filter(vote_id=d.vote.id)[0]
            result.append({'date': d.vote.date, 'time': d.vote.time,
                           'motion': d.vote.motion.name_ch, 'vote': d.result, 'result': voteResult.result})
        return JsonResponse(result[0:size], safe=False)


class AbsentView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, format=None):
        size = int(request.query_params.get('size', 5))
        query = MeetingHansard.objects.all()
        from_year = None
        to_year = None
        if 'from' in request.query_params and 'to' in request.query_params:
            from_year = int(request.query_params['from'])
            to_year = int(request.query_params['to'])
            if from_year >= to_year:
                from_year = None
                to_year = None

        today = date.today()
        if from_year is None:
            from_year = today.year // 4 * 4
        if to_year is None:
            to_year = from_year + 4
        condition = Q(pk__isnull=True)
        for year in range(from_year, to_year):
            condition = condition | (Q(date__gt=date(year, 9, 10)) & Q(
                date__lte=date(year + 1, 9, 9)))
        query = query.filter(condition)
        meeting_total = query.count()
        absent_total = query.all() \
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
            result.append({'id': pk, 'name': name_ch, 'total': dcount,
                           'image': image, 'max': meeting_total})
        return JsonResponse(result[0:size], safe=False)


class PresentCountView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, key=None, format=None):
         from_year = request.query_params.get('from', None)
         to_year = request.query_params.get('to', None)
         result = get_present_count_by_key(from_year, to_year, key)
         return JsonResponse(result, safe=False)


class IndividualView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, key=None, format=None):
        condition = (Q(individual_id=key))
        from_year = None
        to_year = None
        if 'from' in request.query_params and 'to' in request.query_params:
            from_year = int(request.query_params['from'])
            to_year = int(request.query_params['to'])
            if from_year >= to_year:
                from_year = None
                to_year = None
        today = date.today()
        if from_year is None:
            from_year = today.year // 4 * 4
        if to_year is None:
            to_year = from_year + 4
        condition = Q(pk__isnull=True)
        for year in range(from_year, to_year):
            condition = condition | (Q(date__gt=date(year, 9, 10)) & Q(
                date__lte=date(year + 1, 9, 9)))

        voteCounts = IndividualVote.objects.filter(individual_id=key).values('result') \
            .annotate(dcount=Count('result'))

        result = {}
        for voteCount in voteCounts:
            result[voteCount['result'].lower()] = voteCount['dcount']
        individual = Individual.objects.get(pk=key)
        serializer = IndividualSerializer(individual, many=False)
        data = serializer.data
        data.update(result)
        return JsonResponse(data, safe=False)


class SpeakView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, from_year=None, to_year=None, format=None):
        size = int(request.query_params.get('size', 5))
        today = date.today()
        from_year = None
        to_year = None
        if 'from' in request.query_params and 'to' in request.query_params:
            from_year = int(request.query_params['from'])
            to_year = int(request.query_params['to'])
            if from_year >= to_year:
                from_year = None
                to_year = None
        if from_year is None:
            from_year = today.year // 4 * 4
        if to_year is None:
            to_year = from_year + 4
        condition = Q(pk__isnull=True)
        for year in range(from_year, to_year):
            condition = condition | (Q(hansard__date__gt=date(year, 9, 10)) & Q(
                hansard__date__lte=date(year + 1, 9, 9)))
        query = MeetingSpeech.objects.filter(condition)
        speech_total = query.values('individual__pk', 'individual__name_ch', 'individual__image').annotate(
            dcount=Count('individual__pk')).order_by('-dcount')
        result = []
        m = max([d['dcount'] for d in speech_total])
        for d in speech_total:
            pk = d['individual__pk']
            name_ch = d['individual__name_ch']
            dcount = d['dcount']
            image = d['individual__image']
            result.append({'id': pk, 'name': name_ch,
                           'total': dcount, 'max': m, 'image': image})
        return JsonResponse(result[0:size], safe=False)


class ImportantMotionView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, format=None):
        data = []
        motions = ImportantMotion.objects.select_related('motion').values_list(
            'motion__name_ch', 'motion__vote__date', 'motion__vote__pk').order_by('-motion__vote__date')
        summaries = VoteSummary.objects.filter(
            Q(vote__pk__in=[m[2] for m in motions]) & Q(summary_type=VoteSummary.OVERALL))
        result_dict = {s.vote_id: s.result for s in summaries}
        for motion in motions:
            data.append({'title_ch': motion[0], 'date': motion[1],
                         'id': motion[2], 'result': result_dict[motion[2]]})
        return JsonResponse({'data': data}, safe=False)


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

class CouncilView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, key=None, format=None):
        councils = list(Council.objects.all())
        serializer = CouncilSerializer(councils, many=True)
        return JsonResponse(serializer.data, safe=False)


class CouncilByYearAndTypeView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, year, member_type, format=None):
        year = int(year)
        member_types = [5] + list(range(7,35))
        if member_type == 'KLE':
            member_types = [1]
        if member_type == 'NTW':
            member_types = [2]
        if member_type == 'ISLAND':
            member_type = [3]
        if member_type == 'KLW':
            member_type = [4]
        if member_type == 'NTE':
            member_type = [6]
        members = list(CouncilMember.objects.filter(Q(council__start_year=int(year)) & Q(membership_type__pk__in=member_types)))
        presents = {x['id']: {'total':x['total'], 'max': x['max']} for x in  get_present_count_by_key(from_year=year,to_year=year + 4)}
        for member in members:
            pk = member.id
            if pk in presents:
               member.total_present = presents[pk]['total']
               member.max_present = presents[pk]['max']
            else:
               member.total_present = 0
               member.max_present = 0
        serializer = CouncilMemberSerializer(members, many=True)
        return JsonResponse(serializer.data, safe=False)


class StatView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, model, format=None):
        model = model.lower()
        model_mapping = {'hansard': MeetingHansard, 'question': Question, 'vote': Vote, 'meeting': Meeting}
        key_mapping = {'hansard': 'id', 'question': 'key', 'vote': 'id', 'meeting': 'id'}
        model_class_name = model_mapping.get(model, None)
        pk_field = key_mapping.get(model, None)
        if model_class_name is None:
            return HttpResponseNotFound('%s not supported.' % model)
        stat_by_month = model_class_name.objects.annotate(month=ExtractMonth('date'), year=ExtractYear('date'))
        stat_by_month = stat_by_month.values('year', 'month').annotate(total=Count(pk_field)).order_by('year', 'month')

        stat_by_month = [l for l in stat_by_month]
        min_max = model_class_name.objects.all().aggregate(min_date=Min('date'), max_date=Max('date'))
        min_date = min_max['min_date']
        max_date = min_max['max_date']
        return JsonResponse({'month_level': stat_by_month, 'latest': max_date, 'earliest': min_date}, safe=False)
