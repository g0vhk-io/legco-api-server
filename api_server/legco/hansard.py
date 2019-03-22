from django.db import transaction
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


def process_members(members, all_individuals):
    all_personels = []
    for line in members:
        title = re.sub(r'[a-zA-Z\-]', '', line.split(",")[0]).strip()
        title = title.replace(u"郭偉强" ,u"郭偉強")
        if title.startswith(u"#"):
            continue
        personel = MeetingPersonel()
        personel.title_ch = title
        for i in all_individuals:
            if title.find(i.name_ch + u"議員") != -1:
                personel.individual = i
                break
        personel.save()
        all_personels.append(personel)
    return all_personels


def process_speeches(speeches, all_individuals):
    output = []
    for data in speeches:
        speech = MeetingSpeech()
        bookmark = data["bookmark"]
        content = data["content"]
        speech.individual = None
        if bookmark.startswith("SP"):
            speech.title_ch = data["title"]
            speech.title_ch = speech.title_ch.replace(u"郭偉强" ,u"郭偉強")
            dot_pos = speech.title_ch.find('.')
            if dot_pos != -1:
                speech.title_ch = speech.title_ch[dot_pos + 1:]
            for individual in all_individuals:
                if speech.title_ch.startswith(individual.name_ch):
                    speech.individual = individual
        speech.text_ch = content
        speech.bookmark = bookmark
        speech.sequence_number = data["sequence"]
        speech.save()
        output.append(speech)
    return output


def upsert_hansard_json_into_db(payload):
    hansard_url = payload["url"]
    existing_hansard = MeetingHansard.objects.filter(source_url=hansard_url).first()
    if existing_hansard:
        print('Found.')
        return existing_hansard, False

    all_individuals = Individual.objects.all()
    hansard_date = datetime.strptime(payload["date"], '%Y-%m-%d')
    hansard = MeetingHansard()
    md5 = hashlib.md5()
    md5.update(hansard_url.encode('utf-8'))
    hansard.key = str(md5.hexdigest())
    hansard.source_url = hansard_url
    hansard.date = hansard_date
    hansard.save()
    members_present = process_members(payload["membersPresent"], all_individuals)
    members_absent = process_members(payload["membersAbsent"], all_individuals)
    public_officers = process_members(payload["publicOfficersAttending"], all_individuals)
    clerks = process_members(payload["clerksInAttendance"], all_individuals)
    speeches = process_speeches(payload["speeches"], all_individuals)
    for m in members_present:
        hansard.members_present.add(m)
    for m in members_absent:
        hansard.members_absent.add(m)
    for p in public_officers:
        hansard.public_officers.add(p)
    for c in clerks:
        hansard.clerks.add(c)

    all_s = ""
    for s in speeches:
        all_s += s.text_ch + "\n"
        hansard.speeches.add(s)
    #print("Calculating keyword")
    #tr4w = TextRank4Keyword(allow_speech_tags=["nr", "ns", "nz", "nt"])
    #tr4w.analyze(text=all_s, lower=True, window=3)
    #for item in tr4w.get_keywords(20, word_min_len=3):
    #    keyword = item.word
    #    m, created = Keyword.objects.get_or_create(keyword = keyword)
    #    m.keyword = keyword
    #    print(keyword)
    #    hansard.keywords.add(m)
    #print("New hansard ID=%d" % hansard.id)
    hansard.save()
    return hansard, True
