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
    path("talks/<int:pk>/edit/", views.TalkUpdateView.as_view(), name="talk_edit"),
    path("talks/<int:pk>/approve/", views.TalkApproveView.as_view(), name="talk_approve"),
    path("review/", views.review_list, name="review_list"),
    path("organizer/", views.OrganizerHomeView.as_view(), name="organizer_home"),
]
