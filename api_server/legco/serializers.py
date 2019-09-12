from rest_framework import serializers
from legco.models import Meeting, Vote, Motion, Individual, IndividualVote, VoteSummary, MeetingPersonel, MeetingSpeech, MeetingHansard, Keyword
from legco.models import Question, CouncilMembershipType, Council, CouncilMember
from api_server.views import IndividualSerializer


class VoteSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteSummary
        fields = '__all__'


class IndividualVoteSerializer(serializers.ModelSerializer):
    individual = IndividualSerializer(read_only=True, many=False)
    class Meta:
        model = IndividualVote
        fields = ['result', 'individual']


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


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
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

class CouncilMembershipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouncilMembershipType
        fields = '__all__'

class CouncilMemberSerializer(serializers.ModelSerializer):
    member = IndividualSerializer(read_only=True, many=False)
    membership_type = CouncilMembershipTypeSerializer(read_only=True, many=False)
    class Meta:
        model = CouncilMember
        fields = ['member', 'membership_type']


class CouncilSerializer(serializers.ModelSerializer):
    members = IndividualSerializer(many=True, read_only=True)
    chairman = IndividualSerializer(read_only=True, many=False)
    class Meta:
        model = Council
        fields = ['name_en', 'name_ch', 'start_year', 'members', 'chairman']

