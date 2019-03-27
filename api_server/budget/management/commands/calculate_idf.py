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
import math

class Command(BaseCommand):
    help ='Backfill budget keywords'

    def handle(self, *args, **options):
        replies = list(Reply.objects.all())
        ke = KeywordExtractor()
        k = 0
        all_terms = set()
        document_terms = []
        output = []
        l = len(replies)
        for reply in replies:
            k += 1
            terms = ke.get_terms(reply.question + "\n" + reply.answer)
            document_terms.append(terms)
            for term in terms:
                all_terms.add(term)
            if k % 500 == 0:
                print('%d out of %d' % (k, l))
        for term in all_terms:
            f = 0
            for d in document_terms:
                if term in d:
                    f += 1
            idf = math.log(k / f)
            output.append((term, idf))
        sorted_output = sorted(output, key=lambda tup: -tup[1])
        lines = [",".join([a[0], str(a[1])]) + "\n" for a in sorted_output]
        f = open("idf.txt", "w")
        f.writelines(lines)
        f.close()




