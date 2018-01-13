import datetime
from haystack import indexes
from .models import Party


class PartyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    name_en = indexes.CharField(model_attr='name_en')
    name_ch = indexes.CharField(model_attr='name_ch')

    def get_model(self):
       return Party

    def index_queryset(self, using=None):
       return self.get_model().objects.filter() 
