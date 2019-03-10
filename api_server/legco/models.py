from django.db import models
from datetime import datetime

class Keyword(models.Model):
    keyword = models.CharField(max_length=128, unique=True)
    def __unicode__(self):
        return self.keyword

class Party(models.Model):
    name_en = models.CharField(max_length=512)
    name_ch = models.CharField(max_length=512)
    image = models.CharField(max_length=512, blank=True, null=True, default=None)
    keywords = models.CharField(max_length=512, blank=True, null=True, default=None)
    def __unicode__(self):
        return self.name_en + "-" + self.name_ch

class Individual(models.Model):
    name_en = models.CharField(max_length=512)
    name_ch = models.CharField(max_length=512)
    party = models.ForeignKey(Party, null=True, blank=True, on_delete=models.CASCADE)
    image = models.CharField(max_length=512, blank=True, null=True, default=None)
    def __unicode__(self):
        return self.name_en + "-" + self.name_ch

class Motion(models.Model):
    name_en = models.CharField(max_length=512)
    name_ch = models.CharField(max_length=512)
    mover_type = models.CharField(max_length=512)
    mover_ch = models.CharField(max_length=512, default=None, null=True)
    mover_en = models.CharField(max_length=512, default=None, null=True)
    mover_individual = models.ForeignKey(Individual, null=True, blank=True, on_delete=models.DO_NOTHING)
    def __str__(self):
        return self.name_en + "-" + self.name_ch

class ImportantMotion(models.Model):
    motion = models.ForeignKey(Motion, on_delete=models.DO_NOTHING)


class Constituency(models.Model):
    name_en = models.CharField(max_length=512)
    name_ch = models.CharField(max_length=512)
    def __str__(self):
        return self.name_en + "-" + self.name_ch

class Meeting(models.Model):
    date = models.DateField()
    meeting_type = models.CharField(max_length=1024,default=None)
    key = models.CharField(max_length=255, default="no-key", blank=True, null=True, unique=True)
    source_url = models.CharField(max_length=2048, null=True)
    def __str__(self):
        return self.date.strftime('%Y-%m-%d') + "-" + str(self.source_url)

class Vote(models.Model):
    date = models.DateField()
    time = models.TimeField()
    vote_number = models.IntegerField()
    motion = models.ForeignKey(Motion, on_delete=models.DO_NOTHING)
    meeting = models.ForeignKey(Meeting, on_delete=models.DO_NOTHING)
    def __str__(self):
        return self.motion.name_en + " " + self.meeting.date.strftime("%Y-%m-%d")

class VoteSummary(models.Model):
    FUNCTIONAL = 'FUNC'
    OVERALL = 'OVER'
    GEOGRAPHICAL = 'GEOG'
    SUMMARY_CHOICES = ((FUNCTIONAL, 'Functional'),(OVERALL,'Overall'), (GEOGRAPHICAL, 'GEOG'))
    vote = models.ForeignKey(Vote,default=None, on_delete=models.DO_NOTHING)
    summary_type = models.CharField(max_length=64, choices = SUMMARY_CHOICES)
    present_count = models.IntegerField(default=0)
    vote_count = models.IntegerField(default=0)
    yes_count = models.IntegerField(default=0)
    no_count = models.IntegerField(default=0)
    abstain_count = models.IntegerField(default=0)
    result = models.CharField(max_length=512)
    def __str__(self):
        return self.vote.motion.name_en +  " " + self.summary_type + " " + self.result

class IndividualVote(models.Model):
    individual = models.ForeignKey(Individual, on_delete=models.DO_NOTHING)
    YES = 'YES'
    NO = 'NO'
    ABSENT = 'ABSENT'
    ABSTAIN = 'ABSTAIN'
    VOTE_CHOICES = ((YES, 'Yes'), (NO, 'No'),(ABSENT, 'Absent'), (ABSTAIN, 'Abstain'))
    result = models.CharField(max_length=64, choices = VOTE_CHOICES, default=NO)
    vote = models.ForeignKey(Vote, on_delete=models.DO_NOTHING)
    def __str__(self):
        return self.vote.motion.name_en + " " + self.individual.name_en + " " + self.result

class MeetingSpeech(models.Model):
    individual = models.ForeignKey(Individual, null=True, blank=True, on_delete=models.DO_NOTHING)
    others_individual = models.ManyToManyField(Individual, related_name='others')
    title_ch = models.CharField(max_length=100)
    text_ch = models.TextField(max_length=33554432, default="")
    bookmark = models.CharField(max_length=100)
    sequence_number = models.IntegerField(default=0)


class MeetingPersonel(models.Model):
    individual = models.ForeignKey(Individual, null=True, blank=True, on_delete=models.DO_NOTHING)
    title_ch = models.CharField(max_length=100)

class MeetingHansard(models.Model):
    date = models.DateField()
    meeting_type = models.CharField(max_length=128, default="cm")
    key = models.CharField(max_length=128, unique=True)
    source_url = models.CharField(max_length=2048)
    speeches = models.ManyToManyField(MeetingSpeech, related_name='hansard')
    keywords = models.ManyToManyField(Keyword)
    members_present = models.ManyToManyField(MeetingPersonel, related_name='present')
    members_absent = models.ManyToManyField(MeetingPersonel, related_name='absent')
    public_officers = models.ManyToManyField(MeetingPersonel, related_name='officers')
    clerks = models.ManyToManyField(MeetingPersonel, related_name='clerks')

class Question(models.Model):
    individual = models.ForeignKey(Individual, on_delete=models.DO_NOTHING)
    key = models.CharField(max_length=100, primary_key=True)
    date = models.DateField()
    question_type = models.CharField(max_length=255)
    link = models.CharField(max_length=1024, default="")
    question = models.TextField(max_length=33554432, default="")
    answer = models.TextField(max_length=33554432, default="")
    responder = models.CharField(max_length=255)
    question_type = models.CharField(max_length=512)
    title_ch = models.CharField(max_length=512, default="")
    keywords = models.ManyToManyField(Keyword)
    def __str__(self):
        return self.date.strftime("%Y-%m-%d") + self.individual.name_ch + self.title_ch
