from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "cfp"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("ping/", views.PingView.as_view(), name="ping"),
    path("subscribe/", views.SubscribeView.as_view(), name="subscribe"),
    path("subscribe-fbv/", views.subscribe_fbv, name="subscribe_fbv"),
    path("thanks/", views.ThanksView.as_view(), name="thanks"),
    path("talks/", views.TalkListView.as_view(), name="talk_list"),
    path("talks-fbv/", views.my_talks_fbv, name="talk_list_fbv"),
    path("talks/new/", views.TalkCreateView.as_view(), name="talk_new"),
    path("talks/new-traced/", views.TracedTalkCreateView.as_view(), name="talk_new_traced"),
    path("talks/check-title/", views.CheckTitleView.as_view(), name="check_title"),
    path("talks/<int:pk>/", views.TalkDetailView.as_view(), name="talk_detail"),
    path("talks/<int:pk>/edit/", views.TalkUpdateView.as_view(), name="talk_edit"),
    path("talks/<int:pk>/delete/", views.TalkDeleteView.as_view(), name="talk_delete"),
    path("proposals/", RedirectView.as_view(pattern_name="cfp:talk_list"), name="old_talks"),
    path("submit/", RedirectView.as_view(pattern_name="cfp:talk_new", preserve_request=True), name="old_submit"),
]
