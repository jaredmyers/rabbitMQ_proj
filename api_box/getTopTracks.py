from decouple import config
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth 
import spotipy.util as util

SPOTIPY_CLIENT_ID = config('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = config('SPOTIPY_CLIENT_SECRET')
redirect_uri="http://localhost"

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
sp = spotipy.Spotify()

user = sp.user('wizzywizzard')

scope = 'user-library-read'
scope2 = 'user-top-read'

def get_service():
    try:
        token = util.prompt_for_user_token(user, scope2, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=redirect_uri)
        service = spotipy.Spotify(auth=token)
        return service
    except:
        print('Error getting auth token')



#print(spotify.current_user())