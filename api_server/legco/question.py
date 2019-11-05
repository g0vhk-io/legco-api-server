from datetime import datetime
import hashlib
from legco.models import Question, Individual, EventLog


def upsert_question_json_into_db(payload):
    all_individuals = Individual.objects.all()
    link = payload['link']
    existing_question = Question.objects.filter(link=link).first()
    if existing_question:
        print('Found.')
        return existing_question, False
    md5 = hashlib.md5()
    md5.update(link.encode('utf-8'))
    key = str(md5.hexdigest())
    individual_name = payload['individual']
    individual_name = individual_name.replace(u"郭偉强" ,u"郭偉強")
    individual = None
    for i in all_individuals:
        if individual_name.find(i.name_ch + u"議員") != -1:
            individual = i
            break
    if individual is None:
        return None, False
    date = datetime.strptime(payload['date'], '%Y-%m-%d')
    question_type = payload['question_type']
    question_text = payload['question']
    answer_text = payload['answer']
    title_ch = payload['title_ch']
    question = Question()
    question.individual = individual
    question.key = key
    question.date = date
    question.question_type = question_type
    question.link = link
    question.question = question_text
    question.answer = answer_text
    question.question_type = question_type
    question.title_ch = question.title_ch
    question.save()
    event = EventLog()
    event.message = 'New question is added (%s) by %s.' % (question.link, individual_name)
    event.model_key = question.pk
    event.model_class_name = 'question'
    event.save()
    return question, True
