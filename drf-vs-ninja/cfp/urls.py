from django.urls import path

from . import views

app_name = "cfp"

urlpatterns = [
    path("", views.home, name="home"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("thanks/", views.thanks, name="thanks"),
    path("guests/", views.guests, name="guests"),
    path("talks/", views.my_talks, name="my_talks"),
    path("talks/new/", views.TalkCreateView.as_view(), name="talk_new"),
    path("talks/new-fbv/", views.talk_create, name="talk_new_fbv"),
    path("talks/check-title/", views.check_title, name="check_title"),
    path("talks/<int:pk>/", views.talk_detail, name="talk_detail"),
    path("talks/<int:pk>/edit/", views.talk_edit, name="talk_edit"),
    path("tw/crispy/", views.tw_crispy, name="tw_crispy"),
    path("tw/helper/", views.tw_helper, name="tw_helper"),
    path("tw/tweaks/", views.tw_tweaks, name="tw_tweaks"),
]
