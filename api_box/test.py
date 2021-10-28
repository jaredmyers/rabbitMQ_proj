## testing api connection and functions

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth 
import spotipy.util as util

scope = 'user-library-read'
scope2 = 'user-read-currently-playing'

def get_service():
    try:
        token = util.prompt_for_user_token(user, scope2, client_id=client_id, client_secret=client_sk, redirect_uri=redirect_uri)
        service = spotipy.Spotify(auth=token)
        return service
    except:
        print('Error')

#oauth_object = spotipy.SpotifyOAuth(client_id=client_id, client_secret=client_sk, redirect_uri=redirect_uri, scope=scope)

#token_dict = oauth_object.get_access_token()
#token = token_dict['access_token']

#print(token)

#sp = spotipy.Spotify(auth=token)


#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_sk, redirect_uri=redirect_uri, scope=scope))

sp = get_service()
results = sp.current_user_saved_tracks()

for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " - ", track['name'])

#sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_sk))

#results = sp.search(q='weezer', limit=20)

#for idx, track in enumerate(results['tracks']['items']):
#    print(idx, track['name'])

#username = 'jaredrunner?si=d73e5d75deab4c07'

#try:
#    token = util.prompt_for_user_token(username)
#except:
#    print('error')

#sp = spotipy.Spotify(auth=token)


