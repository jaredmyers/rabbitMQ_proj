## testing api connection and functions

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth 
import spotipy.util as util
import sys, json
import site_spotify.credentials as cred

scope = 'user-library-read'
scope2 = 'user-read-currently-playing'

def api_test():
   

    def get_service():
        try:
            token = util.prompt_for_user_token(cred.spot_user, scope, client_id=cred.client_id, client_secret=cred.client_sk, redirect_uri=cred.redirect_uri)
            service = spotipy.Spotify(auth=token)
            print(type(token))
            print(token)
            
            return service
        except Exception as e:
            print(e)
    

#oauth_object = spotipy.SpotifyOAuth(client_id=client_id, client_secret=client_sk, redirect_uri=redirect_uri, scope=scope)

#token_dict = oauth_object.get_access_token()
#token = token_dict['access_token']

#print(token)

#sp = spotipy.Spotify(auth=token)


#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_sk, redirect_uri=redirect_uri, scope=scope))

    sp = get_service()
    if sp == None:
        sys.exit("error, service none")

    results = sp.current_user_saved_tracks()
 
    saved_tracks = []
    for idx, item in enumerate(results['items']):
        track = item['track']
        saved_tracks.append((idx, track['artists'][0]['name'], " - ", track['name']))

    return saved_tracks

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


