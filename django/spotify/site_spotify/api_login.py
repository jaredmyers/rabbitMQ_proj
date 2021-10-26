import base64
import datetime
from urllib.parse import urlencode
import requests
import credentials as cred

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy.util as util

auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=cred.client_id, client_secret=cred.client_sk, username=cred.spot_user, scope='user-library-read', redirect_uri=cred.redirect_uri, )

sp = spotipy.Spotify(auth_manager=auth_manager)

results = sp.current_user_saved_tracks()

saved_tracks = []
for idx, item in enumerate(results['items']):
    track = item['track']
    saved_tracks.append((idx, track['artists'][0]['name'], " - ", track['name']))

for track in saved_tracks:
    print(track)