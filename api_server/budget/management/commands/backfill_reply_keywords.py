# -*- coding: utf-8 -*-
import requests
from lxml.html.clean import clean_html
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from budget.models import Reply, Keyword
from lxml import etree
from datetime import *
from dateutil.parser import *
from lxml.html.clean import Cleaner
from django.db.utils import *
import re
from legco.management.commands.keyword_extractor import KeywordExtractor

class Command(BaseCommand):
    help ='Backfill budget keywords'

    @transaction.atomic
    def handle(self, *args, **options):
        replies = Reply.objects.all()
        ke = KeywordExtractor()
        for reply in replies:
            reply.keywords = []
            keywords = ke.get_keywords(reply.question + "\n" + reply.answer)
            print(",".join(keywords))
            for keyword in keywords:
                m, created = Keyword.objects.get_or_create(keyword = keyword)
                m.keyword = keyword
                reply.keywords.add(m)
                m.save()
            reply.save()




