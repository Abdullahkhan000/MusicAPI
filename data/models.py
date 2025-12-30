from os import name

from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])


class Song(BaseModel):
    name = models.CharField(max_length=100, help_text="Enter the name of the song")
    slug = models.SlugField(max_length=300, unique=True, blank=True, db_index=True)
    track_number = models.PositiveIntegerField(
        null=True, blank=True, help_text="Track number of the song (Spotify original)")
    singer = models.CharField(max_length=150, help_text="Singer(s) of the song", blank=True, default="No Singer")
    composer = models.CharField(max_length=150, help_text="Composer(s) of the song", blank=True, default="No Composer")

    spotify_song = models.URLField(null=True, blank=True)
    spotify_song_poster = models.URLField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Song.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Song Name {self.name}"

class SongDetails(BaseModel):
    song = models.OneToOneField(
        Song,
        on_delete=models.CASCADE,
        related_name="details"
    )

    genre = models.CharField(
        max_length=70,
        blank=True,
        help_text="Genre of the song or album"
    )

    album = models.CharField(
        max_length=400,
        blank=True,
        help_text="Album name"
    )

    album_composer = models.CharField(
        max_length=50,
        blank=True,
        help_text="Album's Composer Name",
        default="No Album Composer"
    )

    spotify_album = models.URLField(
        null=True,
        blank=True,
        help_text="Spotify album URL"
    )

    spotify_album_poster = models.URLField(
        null=True,
        blank=True,
        help_text="Spotify album cover image"
    )

    release_date = models.DateField(
        null=True,
        blank=True,
        help_text="Official release date"
    )

    class Meta:
        verbose_name_plural = "Song Details"

    @property
    def spotify_song_url(self):
        return self.song.spotify_song

    def __str__(self):
        return f"Details for {self.song.name} + Album {self.album}"

class Composer(BaseModel):
    name = models.CharField(
        max_length=200,
        help_text="Enter the name of the composer"
    )
    genre = models.CharField(
        max_length=150,
        help_text="Enter the composer's genre"
    )
    join_date = models.DateField(null=True, blank=True)
    about = models.TextField(
        help_text="Enter the bio of the composer"
    )
    recent_release = models.URLField(
        null=True,
        blank=True,
        help_text="Spotify URL of the most recent release"
    )
    pic = models.URLField(
        null=True,
        blank=True,
        help_text="URL of the composer's picture"
    )
    total_album = models.PositiveIntegerField(
        help_text="Total number of albums by the composer"
    )
    single_tracks = models.PositiveIntegerField(
        help_text="Total number of tracks by the composer"
    )

    def __str__(self):
        return f"{self.name} ({self.join_date})"