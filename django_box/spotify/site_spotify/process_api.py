import base64, requests, sys
from urllib.parse import urlencode
from site_spotify.send_to_db import send_to_db
from site_spotify.send_to_api import send_to_api
import site_spotify.credentials as cred
import spotipy

'''
interface between webfront and MQ
for anything regarding the API
interfaces with the API driver which established MQ connection

'''

def fetch_token2(auth_code):

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
    
def store_token_api(token, sessionId):
    message = 'store_token:' + sessionId + ':' + token
    response = send_to_db(message,'check_session')
    print("from store_token_api: ")
    print(response)

    return response

def fetch_token(auth_code):
    message = 'fetch_token:' + auth_code
    response = send_to_api(message, 'api_info')
    print("from process_api_fetchToken: ")
    print(response)
    return response

def get_saved_tracks(sessionId):
    message = "get_saved_tracks:"+ sessionId
    response = send_to_api(message, 'api_info')
    print("-------FROM GET_SAVED_TRACKS:")
    print(response)
    print("-------------")

    if not response:
        return []

    saved_tracks = response.split(";")
    del saved_tracks[-1]
    
    return saved_tracks

def get_stats_page(sessionId):
    message = "get_stats:" + sessionId
    response = send_to_api(message, 'api_info')

    if not response:
        return ''

    print("-------FROM GET_STATS_PAGE:")
    response = response.split("+")

    most_listened_genres = response[0]
    most_listened_genres = most_listened_genres.split(":")
    del most_listened_genres[-1]


    most_freq_artists = response[1]
    most_freq_artists = most_freq_artists.split(";")
    del most_freq_artists[-1]
    mfa = []
    for i in most_freq_artists:
        mfa.append(i.split(":"))

    avg_release_year = response[2]
    
    recommended_tracks = response[3]
    recommended_tracks = recommended_tracks.split(";")
    del recommended_tracks[-1]
    rt = []
    for i in recommended_tracks:
        rt.append(i.split(":"))

    rt.sort(key=lambda x:x[2], reverse=True)


    print(most_listened_genres)
    print("----")
    print(mfa)
    print("----")
    print(avg_release_year)
    print("----")
    print(rt)
    print("-------------")

    # take first 5 of each
    return [most_listened_genres[:4], mfa[:4], avg_release_year, rt[:4]]


