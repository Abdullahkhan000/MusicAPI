from django.urls import path
from . import views
urlpatterns = [
    path("spotify_song/",views.SongView.as_view()),
    path("spotify_song/<int:pk>/", views.SongView.as_view()),

    path("spotify_album/",views.SongDetailView.as_view()),
    path("spotify_album/<int:pk>/", views.SongDetailView.as_view()),

    path("composer/",views.ComposerView.as_view()),
    path("composer/<int:pk>/", views.ComposerView.as_view()),

    path("composer-ui/", views.composer_list_ui, name="composer-list-ui"),
    path("composer-ui/<int:pk>/", views.composer_detail_ui, name="composer-detail-ui"),

]