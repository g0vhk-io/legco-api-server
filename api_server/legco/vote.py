from legco.models import Meeting, Vote, Motion, Individual, IndividualVote, VoteSummary
from lxml import etree
from datetime import *
import requests
from dateutil.parser import *
import hashlib


def parse_date(s):
    for fmt in ["%d/%m/%Y","%d-%m-%Y"]:
        try:
            return datetime.strptime(s, fmt).date()
        except:
            pass
    raise Exception("failed to parse %s." % (s))


def parse_time(s):
    return datetime.strptime(s or "00:00:00", "%H:%M:%S").time()


def upsert_votes_into_db(url):
    if url is None:
        return []

    r = requests.get(url)
    s = r.content
    print(s[0:300])
    doc = etree.XML(s)
    individuals = Individual.objects.all()

    results = []

    for meeting_node in doc.xpath('//meeting'):
        md5 = hashlib.new('md5')
        md5.update(url.encode('utf-8'))
        key = str(md5.hexdigest())
        meeting = Meeting.objects.filter(key=key).first()
        if meeting is not None:
             votes = []
             for v in Vote.objects.filter(meeting=meeting):
                summaries = VoteSummary.objects.filter(vote=v)
                individual_votes = IndividualVote.objects.filter(vote=v)
                votes.append({'vote': v, 'summaries': summaries, 'individual_votes': individual_votes})
             results.append({'meeting': meeting, 'votes': votes, 'is_created': False})
             continue
        meeting = Meeting()
        meeting.date = parse_date(meeting_node.attrib['start-date'])
        meeting.meeting_type = meeting_node.attrib['type']
        meeting.source_url = url
        meeting.key = key
        meeting.save()
        votes = []
        for vote_node in meeting_node.xpath('./vote'):
            motion = Motion()
            motion.name_en = vote_node.xpath('motion-en')[0].text or ""
            motion.name_ch = vote_node.xpath('motion-ch')[0].text
            if len(vote_node.xpath('mover-en')) > 0:
                motion.mover_en = vote_node.xpath('mover-en')[0].text
                motion.mover_ch = vote_node.xpath('mover-ch')[0].text
                motion.mover_type = vote_node.xpath('mover-type')[0].text
            else:
                motion.mover_en = ""
                motion.mover_ch = ""
                motion.mover_type = ""
            motion.save()
            vote = Vote()
            vote.meeting = meeting
            vote.date = parse_date(vote_node.xpath('vote-date')[0].text)
            vote.time = parse_time(vote_node.xpath('vote-time')[0].text)
            vote.vote_number = int(vote_node.attrib['number'])
            vote.separate = vote_node.xpath('vote-separate-mechanism')[0].text == "Yes"
            vote.motion = motion
            vote.save()
            possible_summary_tags = ['overall','functional-constituency','geographical-constituency']
            summary_types = ['OVER', 'FUNC', 'GEOG']
            summaries = []
            for summary_node in vote_node.xpath('vote-summary')[0].xpath('*'):
                summary = VoteSummary()
                summary.vote = vote
                summary.summary_type = summary_types[possible_summary_tags.index(summary_node.tag)]
                summary.present_count = int(summary_node.xpath('present-count')[0].text or 0)
                summary.vote_count = int(summary_node.xpath('vote-count')[0].text or 0)
                summary.yes_count =  int(summary_node.xpath('yes-count')[0].text or 0)
                summary.no_count = int(summary_node.xpath('no-count')[0].text or 0)
                summary.abstain_count = int(summary_node.xpath('abstain-count')[0].text or 0)
                summary.result = summary_node.xpath('result')[0].text
                summary.save()
                summaries.append(summary)
            individual_votes = []
            for individual_vote_node in vote_node.xpath('./individual-votes/member'):
                name_ch = individual_vote_node.attrib['name-ch']
                name_en = individual_vote_node.attrib['name-en']
                target_individual = None
                for individual in individuals:
                    if individual.name_ch == name_ch or individual.name_en == name_en:
                        target_individual = individual
                        break
                if target_individual is None:
                    raise Exception("Individual not found " + name_ch)
                individual_vote = IndividualVote()
                individual_vote.result = individual_vote_node.xpath('vote')[0].text.upper()
                individual_vote.individual = target_individual
                individual_vote.vote = vote
                individual_vote.save()
                individual_votes.append(individual_vote)
            votes.append({'vote': vote, 'summaries': summaries, 'individual_votes': individual_votes })
        #Saving Records
        meeting.save()
        results.append({'meeting': meeting, 'votes':votes , 'is_created': True})
    return results
