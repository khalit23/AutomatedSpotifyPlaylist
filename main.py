import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup

CLIENT_ID = "84af18209ee44600a53d632836a2929b"
CLIENT_SECRET = "8e4242e8ba4046a0b06badba0f30bd01"

user_input = input("What year would you like to go back to? Type the date in this format YYYY-MM-DD: ")

URL = f"https://www.billboard.com/charts/hot-100/{user_input}/"


def get_songs():
    response = requests.get(url=URL)

    soup = BeautifulSoup(response.text, "html.parser")

    first_song = soup.find(name="h3", id="").getText()

    rest_of_songs = soup.find_all(name="h3",
                                  class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only")

    song_titles_unclean = []

    song_titles_unclean.append(first_song)

    for song in rest_of_songs:
        title = song.getText()
        song_titles_unclean.append(title)

    song_titles_cleaning = [song.replace('\n', "") for song in song_titles_unclean]

    song_titles = [song.replace("\t", "") for song in song_titles_cleaning]

    return song_titles


def authenticate_spotify():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri="http://example.com",
                                                   scope="user-library-read"))

    return sp


year = user_input.split("-")[0]
queried_songs = get_songs()
sp = authenticate_spotify()
user_id = authenticate_spotify().current_user()["id"]

song_uris = []

for song in queried_songs:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

spot = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)

playlist = spot.user_playlist_create(user=user_id, name=f"Billboard top 100 songs from {user_input}", public=False)

spot.playlist_add_items(playlist_id=playlist["id"], items=song_uris)