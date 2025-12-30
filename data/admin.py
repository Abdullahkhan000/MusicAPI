from django.contrib import admin
from .models import Song , SongDetails , Composer

admin.site.register(Song)
admin.site.register(SongDetails)
admin.site.register(Composer)