# -*- coding: utf-8 -*-
import requests
from lxml.html.clean import clean_html
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from legco.models import Question, Keyword
from lxml import etree
from datetime import *
from dateutil.parser import *
from lxml.html.clean import Cleaner
from django.db.utils import *
import re
from .keyword_extractor import KeywordExtractor

class Command(BaseCommand):
    help ='Backfill question keywords'

    @transaction.atomic
    def handle(self, *args, **options):
        questions = Question.objects.all()
        ke = KeywordExtractor()
        for question in questions:
            question.keywords = []
            keywords = ke.get_keywords(question.question)
            print(",".join(keywords))
            for keyword in keywords:
                m, created = Keyword.objects.get_or_create(keyword = keyword)
                m.keyword = keyword
                question.keywords.add(m)
                m.save()
            question.save()




