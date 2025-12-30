from django.conf import settings
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


# -----------------------------
# Spotify client via settings
# -----------------------------
client_credentials_manager = SpotifyClientCredentials(
    client_id=settings.SPOTIFY_CLIENT_ID,
    client_secret=settings.SPOTIFY_CLIENT_SECRET,
)
sp = Spotify(auth_manager=client_credentials_manager)


def fetch_spotify_assets(
    song_name=None,
    singer=None,
    composer=None,
    album_name=None,
    album_composer=None,
):
    """
    Fetch Spotify song + album data.
    Spotify ONLY provides data, overwrite logic handled elsewhere.
    """

    data = {}

    # =============================
    # SONG FETCH
    # =============================
    if song_name and (
        (singer and singer != "No Singer")
        or (composer and composer != "No Composer")
    ):
        query_parts = [song_name]

        if singer and singer != "No Singer":
            query_parts.append(singer)

        if composer and composer != "No Composer":
            query_parts.append(composer)

        query = " ".join(query_parts)

        try:
            res = sp.search(q=query, type="track", limit=1)
            tracks = res.get("tracks", {}).get("items", [])

            if tracks:
                track = tracks[0]
                album = track.get("album", {})

                data["spotify_song"] = track.get(
                    "external_urls", {}
                ).get("spotify")

                images = album.get("images", [])
                if images:
                    data["spotify_song_poster"] = images[0].get("url")

                # ---- Genre (best effort) ----
                artists = track.get("artists", [])
                if artists:
                    artist_id = artists[0]["id"]
                    artist_data = sp.artist(artist_id)
                    genres = artist_data.get("genres", [])
                    if genres:
                        data["genre"] = genres[0]

        except Exception as e:
            print(f"[Spotify Song Error] {e}")

    # =============================
    # ALBUM FETCH
    # =============================
    if album_name or (
        album_composer and album_composer != "No Album Composer"
    ):
        query_parts = []

        if album_name:
            query_parts.append(album_name)

        if album_composer and album_composer != "No Album Composer":
            query_parts.append(album_composer)

        query = " ".join(query_parts)

        try:
            res = sp.search(q=query, type="album", limit=1)
            albums = res.get("albums", {}).get("items", [])

            if albums:
                album = albums[0]

                data["spotify_album"] = album.get(
                    "external_urls", {}
                ).get("spotify")

                images = album.get("images", [])
                if images:
                    data["spotify_album_poster"] = images[0].get("url")

                if album.get("release_date"):
                    data["release_date"] = album["release_date"]

                artists = album.get("artists", [])
                if artists:
                    data["album_composer"] = artists[0].get("name")

        except Exception as e:
            print(f"[Spotify Album Error] {e}")

    return data


def update_song_spotify_info(song_instance, details_instance=None):
    """
    Update Song & SongDetails with Spotify data
    - NEVER overwrites manually filled fields
    - SAFE for PATCH / PUT / BULK updates
    """

    assets = fetch_spotify_assets(
        song_name=song_instance.name,
        singer=song_instance.singer,
        composer=song_instance.composer,
        album_name=details_instance.album if details_instance else None,
        album_composer=details_instance.album_composer if details_instance else None,
    )

    # =============================
    # SONG UPDATE (SAFE)
    # =============================
    song_updated = False

    if not song_instance.spotify_song and assets.get("spotify_song"):
        song_instance.spotify_song = assets["spotify_song"]
        song_updated = True

    if not song_instance.spotify_song_poster and assets.get(
        "spotify_song_poster"
    ):
        song_instance.spotify_song_poster = assets["spotify_song_poster"]
        song_updated = True

    if hasattr(song_instance, "details") and assets.get("genre"):
        if not song_instance.details.genre:
            song_instance.details.genre = assets["genre"]
            song_instance.details.save(update_fields=["genre"])

    if song_updated:
        song_instance.save(
            update_fields=["spotify_song", "spotify_song_poster"]
        )

    # =============================
    # ALBUM UPDATE (SAFE)
    # =============================
    if details_instance:
        detail_fields = []

        if not details_instance.spotify_album and assets.get("spotify_album"):
            details_instance.spotify_album = assets["spotify_album"]
            detail_fields.append("spotify_album")

        if not details_instance.spotify_album_poster and assets.get(
            "spotify_album_poster"
        ):
            details_instance.spotify_album_poster = assets[
                "spotify_album_poster"
            ]
            detail_fields.append("spotify_album_poster")

        if not details_instance.release_date and assets.get("release_date"):
            details_instance.release_date = assets["release_date"]
            detail_fields.append("release_date")

        if (
            details_instance.album_composer in ("", "No Album Composer")
            and assets.get("album_composer")
        ):
            details_instance.album_composer = assets["album_composer"]
            detail_fields.append("album_composer")

        if detail_fields:
            details_instance.save(update_fields=detail_fields)

    return song_instance, details_instance

def update_composer_spotify_info(composer_instance):
    if not composer_instance.name:
        return composer_instance

    try:
        # =============================
        # SEARCH ARTIST
        # =============================
        res = sp.search(
            q=composer_instance.name,
            type="artist",
            limit=1
        )
        artists = res.get("artists", {}).get("items", [])
        if not artists:
            return composer_instance

        artist = artists[0]
        artist_id = artist.get("id")
        update_fields = []

        # =============================
        # PROFILE PIC
        # =============================
        images = artist.get("images", [])
        if images and not composer_instance.pic:
            composer_instance.pic = images[0].get("url")
            update_fields.append("pic")

        # =============================
        # GENRE
        # =============================
        genres = artist.get("genres", [])
        if genres and not composer_instance.genre:
            composer_instance.genre = genres[0]
            update_fields.append("genre")

        # =============================
        # TOTAL ALBUMS (ALL PAGES)
        # =============================
        if not composer_instance.total_album:
            albums = []
            offset = 0
            while True:
                albums_res = sp.artist_albums(
                    artist_id,
                    album_type="album",
                    limit=50,
                    offset=offset
                )
                page_albums = albums_res.get("items", [])
                if not page_albums:
                    break
                albums.extend(page_albums)
                if len(page_albums) < 50:
                    break
                offset += 50

            if albums:
                composer_instance.total_album = len(albums)
                update_fields.append("total_album")

                # =============================
                # RECENT RELEASE URL
                # =============================
                recent_album = albums[0]
                recent_url = recent_album.get("external_urls", {}).get("spotify")
                if recent_url and not composer_instance.recent_release:
                    composer_instance.recent_release = recent_url
                    update_fields.append("recent_release")

        # =============================
        # SAVE ONLY WHAT CHANGED
        # =============================
        if update_fields:
            composer_instance.save(update_fields=update_fields)

    except Exception as e:
        print(f"[Spotify Composer Error] {e}")

    return composer_instance
