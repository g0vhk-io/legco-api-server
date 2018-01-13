import datetime
from haystack import indexes
from .models import Reply


class ReplyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    bureau = indexes.CharField(model_attr='bureau')
    year = indexes.IntegerField(model_attr='year')
    member = indexes.CharField(model_attr='member')
    reply_serial_no = indexes.CharField(model_attr='reply_serial_no')

    def get_model(self):
        return Reply

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
