from .views import *
from .vote_views import MeetingVoteUpsertView
from django.conf.urls import url

urlpatterns = [
  url(r'^vote/(?P<key>[0-9]+)/$', VoteDetailView.as_view(), name='vote'),
  url(r'^votes/(?P<date>[0-9]+\-[0-9]+\-[0-9]+)/$', VoteSearchView.as_view(), name='votes'),
  url(r'^votes/(?P<year>[0-9]+)/$', VoteSearchView.as_view(), name='votes_per_year'),
  url(r'^votes/latest/(?P<key>[0-9]+)/$', LatestVotesView.as_view(), name='latest_votes'),
  url(r'^speech_search/(?P<keyword>.+)/$', MeetingSpeechSearchView.as_view(), name='speech_by_keyword'),
  url(r'^hansard/(?P<key>[0-9]+)/$', MeetingHansardView.as_view(), name='hansard_detail'),
  url(r'^hansard/$', MeetingHansardView.as_view(), name='hansard_detail'),
  url(r'^upsert_hansard/$', MeetingHansardUpsertView.as_view(), name='hansard_detail_upsert'),
  url(r'^hansards/$', MeetingHansardsView.as_view(), name='hansards'),
  url(r'^hansards/(?P<year>[0-9]+)/$', MeetingHansardsView.as_view(), name='hansards_in_a_year'),
  url(r'^present_count/(?P<key>[0-9]+)$', PresentCountView.as_view(), name='present'),
  url(r'^present_count/$', PresentCountView.as_view(), name='present'),
  url(r'^vote_count/(?P<key>[0-9]+)$', VoteCountView.as_view(), name='vote_count'),
  url(r'^absent_rank/$', AbsentView.as_view(), name='absent'),
  url(r'^speak_rank/$', SpeakView.as_view(), name='speak'),
  url(r'^important_motion/$', ImportantMotionView.as_view(), name='important_motion'),
  url(r'^question_search/(?P<keyword>.+)/$', QuestionSearchView.as_view(), name='question_by_keyword'),
  url(r'^question/(?P<key>.+)/$', QuestionView.as_view(), name='question'),
  url(r'^upsert_vote/$', MeetingVoteUpsertView.as_view(), name='vote_upsert'),
]
