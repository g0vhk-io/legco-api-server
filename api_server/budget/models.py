from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

class Keyword(models.Model):
    keyword = models.CharField(max_length=200, primary_key=True)

class Reply(models.Model):
    year = models.IntegerField()
    bureau = models.CharField(max_length=56)
    head = models.CharField(max_length=256)
    head_number = models.IntegerField()
    sub_head = models.CharField(max_length=256)
    sub_head_number = models.IntegerField(null=True)
    controlling_officer_title = models.CharField(max_length=256)
    controlling_officer_name = models.CharField(max_length=256)
    programme = models.CharField(max_length=256)
    reply_serial_no = models.CharField(max_length=256)
    member = models.CharField(max_length=256)
    director = models.CharField(max_length=256)
    member_question_no = models.IntegerField()
    key = models.CharField(max_length=128, primary_key=True)
    question = models.TextField()
    answer =  models.TextField()
    keywords = models.ManyToManyField(Keyword)
    def __unicode__(self):
        return self.bureau + "-" + str(self.pk)
