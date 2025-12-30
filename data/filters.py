import django_filters
from .models import Song , SongDetails , Composer

class SongFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name",lookup_expr="icontains")
    track_id = django_filters.NumberFilter(field_name="track_number", lookup_expr="exact")
    singer = django_filters.CharFilter(field_name="singer" ,lookup_expr="icontains")
    composer = django_filters.CharFilter(field_name="composer", lookup_expr="icontains")

    class Meta:
        model = Song
        fields = [
            "name",
            "track_id",
            "singer",
            "composer"
        ]

class SongDetailFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name="genre",lookup_expr="icontains")
    album = django_filters.CharFilter(field_name="album",lookup_expr="icontains")
    album_composer = django_filters.CharFilter(field_name="album_composer",lookup_expr="icontains")
    released_after = django_filters.DateFilter(
        field_name="release_date", lookup_expr="gte"
    )
    released_before = django_filters.DateFilter(
        field_name="release_date", lookup_expr="lte"
    )

    class Meta:
        model = SongDetails
        fields = [
            "genre",
            "album",
            "album_composer",
            "released_after",
            "released_before"
        ]

class ComposerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains"
    )

    genre = django_filters.CharFilter(
        field_name="genre", lookup_expr="icontains"
    )

    joined_after = django_filters.DateFilter(
        field_name="join_date", lookup_expr="gte"
    )
    joined_before = django_filters.DateFilter(
        field_name="join_date", lookup_expr="lte"
    )

    min_albums = django_filters.NumberFilter(
        field_name="total_album", lookup_expr="gte"
    )
    max_albums = django_filters.NumberFilter(
        field_name="total_album", lookup_expr="lte"
    )

    class Meta:
        model = Composer
        fields = ["name","genre","joined_after","joined_before","min_albums","max_albums"]