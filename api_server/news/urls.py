from .views import *
from django.conf.urls import url


urlpatterns = [
    url(r'^$', NewsView.as_view(), name='news'),
    url(r'^feed/$', NewsFeed(), name='rss')
]
