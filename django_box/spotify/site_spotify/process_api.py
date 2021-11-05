import base64, requests, sys
from urllib.parse import urlencode
from site_spotify.send_to_db import send_to_db
import site_spotify.credentials as cred
import spotipy

def fetch_token(auth_code):

    CLIENT_ID = cred.client_id
    CLIENT_SECRET = cred.client_sk
    redirect_uri = 'http://10.202.5.100/site_spotify/home'
    url_endpoint = 'https://accounts.spotify.com/api/token'

    client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    client_creds_b64 = client_creds_b64.decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {client_creds_b64}"
        }

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri
        }

    r = requests.post(url_endpoint, headers=headers, data=data)
    if r.status_code not in range(200,299):
        raise Exception("Could not authenticate")
    data = r.json()
    access_token = data['access_token']

    return access_token

def store_token_api(token, sessionId):
    message = 'store_token:' + sessionId + ':' + token
    response = send_to_db(message,'check_session')
    print("from store_token_api: ")
    print(response)

    return response

def api_test2(access_token):

    sp = spotipy.Spotify(access_token)

    if sp == None:
        sys.exit("error, service none")

    results = sp.current_user_saved_tracks()
 
    saved_tracks = []
    for idx, item in enumerate(results['items']):
        track = item['track']
        saved_tracks.append((idx, track['artists'][0]['name'], " - ", track['name']))

    return saved_tracks
    
    



