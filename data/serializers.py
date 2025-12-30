from rest_framework import serializers
from .models import Song, SongDetails , Composer
from .utils import update_song_spotify_info , update_composer_spotify_info
from datetime import date
import textwrap


class SongNestedSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    singer = serializers.CharField()
    composer = serializers.CharField()
    spotify_song = serializers.URLField()
    spotify_song_poster = serializers.URLField()


class SongSerializer(serializers.Serializer):
    """
    Serializer for Song model
    Handles Spotify fetch for songs on create/update
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    track_number = serializers.IntegerField(required=False, allow_null=True)
    singer = serializers.CharField(max_length=150, required=False, allow_blank=True, default="No Singer")
    composer = serializers.CharField(max_length=150, required=False, allow_blank=True, default="No Composer")
    spotify_song = serializers.URLField(read_only=True)
    spotify_song_poster = serializers.URLField(read_only=True)
    slug = serializers.CharField(read_only=True)

    def create(self, validated_data):
        # Create Song instance
        song = Song.objects.create(**validated_data)
        # Ensure SongDetails exists
        SongDetails.objects.get_or_create(song=song)
        # Fetch Spotify song info (song URL & poster) on creation
        update_song_spotify_info(song, getattr(song, "details", None))
        return song

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Fetch Spotify song info on update (does not overwrite existing URLs)
        update_song_spotify_info(instance, getattr(instance, "details", None))
        return instance


class SongDetailSerializer(serializers.Serializer):
    # ===== Album fields first =====
    id = serializers.IntegerField(read_only=True)
    genre = serializers.CharField(max_length=70, required=False, allow_blank=True)
    album = serializers.CharField(max_length=400, required=False, allow_blank=True)
    album_composer = serializers.CharField(
        max_length=50, required=False, allow_blank=True, default="No Album Composer"
    )
    release_date = serializers.DateField(required=False, allow_null=True)
    spotify_album = serializers.URLField(read_only=True)
    spotify_album_poster = serializers.URLField(read_only=True)

    # ===== WRITE ONLY =====
    song_id = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(),
        write_only=True,
        source="song"
    )

    # ===== READ ONLY (nested) =====
    song = SongNestedSerializer(read_only=True)

    def create(self, validated_data):
        song = validated_data.pop("song")   # ✅ now exists

        details, created = SongDetails.objects.get_or_create(
            song=song,
            defaults=validated_data
        )

        if not created:
            for attr, value in validated_data.items():
                setattr(details, attr, value)
            details.save()

        update_song_spotify_info(song, details)
        return details

    def update(self, instance, validated_data):
        validated_data.pop("song", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        update_song_spotify_info(instance.song, instance)
        return instance

class ComposerSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)

    genre = serializers.CharField(max_length=150, required=False, allow_blank=True)
    join_date = serializers.DateField(required=False)   # 👈 manual only
    # about = serializers.CharField(required=False, allow_blank=True)
    about = serializers.CharField(required=False, allow_blank=True)
    total_album = serializers.IntegerField(required=False)
    single_tracks = serializers.IntegerField(required=False)

    pic = serializers.URLField(required=False)
    recent_release = serializers.URLField(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data.get('about'):
            clean_text = data['about'].replace("\r", " ").replace("\n", " ").strip()
            data['about'] = textwrap.wrap(clean_text, width=100)

        return data

    def create(self, validated_data):
        validated_data.setdefault("genre", "")
        validated_data.setdefault("about", "")
        validated_data.setdefault("total_album", 0)
        validated_data.setdefault("single_tracks", 0)

        composer = Composer.objects.create(**validated_data)

        update_composer_spotify_info(composer)

        return composer

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        update_composer_spotify_info(instance)

        return instance
