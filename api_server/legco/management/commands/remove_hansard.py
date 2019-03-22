# -*- coding: utf-8 -*-
from django.db import transaction
from django.db import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from legco.models import Keyword
from legco.models import Meeting, Vote, Motion, Individual, IndividualVote, VoteSummary, Party, MeetingHansard, MeetingSpeech, MeetingPersonel
from dateutil.parser import *
import os
import json
import requests
import multiprocessing
from lxml import etree
from io import StringIO
import functools
import hashlib
import re
import sys
import json
from datetime import date, datetime
from collections import Counter
from textrank4zh import TextRank4Keyword, TextRank4Sentence


class Command(BaseCommand):
    help = 'Remove hansard from database'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str)

    def delete_existing_hansard(self, url):
        try:
            hansard = MeetingHansard.objects.get(source_url=url)
            queries = [hansard.members_present,
                       hansard.speeches,
                       hansard.members_absent,
                       hansard.public_officers,
                       hansard.clerks,
                       hansard.keywords]
            for q in queries:
                for o in q.all():
                    o.delete()
                q.clear()
            hansard.delete()
        except ObjectDoesNotExist:
            pass

    @transaction.atomic
    def handle(self, *args, **options):
        url = options['url']
        self.delete_existing_hansard(url)
