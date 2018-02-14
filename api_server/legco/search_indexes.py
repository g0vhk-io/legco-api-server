import datetime
from haystack import indexes
from .models import Party, MeetingSpeech


class PartyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    name_en = indexes.CharField(model_attr='name_en')
    name_ch = indexes.CharField(model_attr='name_ch')

    def get_model(self):
       return Party

    def index_queryset(self, using=None):
       return self.get_model().objects.filter() 

class SpeechIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name_ch = indexes.CharField(model_attr='title_ch')
    year = indexes.IntegerField(model_attr='hansard__date__year')

    def get_model(self):
        return MeetingSpeech

    def index_queryset(self, using=None):
        return self.get_model().objects.filter().prefetch_related('hansard')
