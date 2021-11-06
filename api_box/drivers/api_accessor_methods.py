import sys, base64, requests
import spotipy
import credentials as cred
from send_to_db import send_to_db

'''
The body of the incoming message will contain a command and a sessionId (or any other info)
in the format of "command:sessionId" The command will route
the message to an accessor method, which will parse the message and 
execute the command, returning the results

'''

def accessor_methods(body, queue):
    '''
    driver for all accessor methods
    takes in string body in format "command:sessionId"
    takes in string queue, currently not in use.
    '''

    def fetch_token(body):
        '''takes in string in format "command:auth_code", returns api token string '''

        body = body.split(":")
        auth_code = body[1]

        CLIENT_ID = cred.client_id
        CLIENT_SECRET = cred.client_sk
        redirect_uri = cred.redirect_uri
        url_endpoint = cred.url_endpoint

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

    def get_token_from_db(sessionId):
        '''takes in string sessionId, return string access_token from db'''

        message = f"get_token:{sessionId}"
        access_token = send_to_db(message, 'check_session')

        return access_token

    def get_saved_tracks(body):
        '''takes in string in format "command:sessionId", returns saved tracks string'''
        body = body.split(":")
        sessionId = body[1]
        access_token = get_token_from_db(sessionId)

        if not access_token:
            return ''
        
        sp = spotipy.Spotify(access_token)

        if sp == None:
            print("error, service none")
            return ''

        results = sp.current_user_saved_tracks()
    
        saved_tracks = ''
        for idx, item in enumerate(results['items']):
            track = item['track']
            saved_tracks += track['artists'][0]['name'] + " - " + track['name'] + ';'

        return saved_tracks


    def another_api_call(body):
        pass

 
    ## Main Entry Point ##

    print(f"from db accessor methods: {body}") # print for debug
    body = body.decode('utf-8')

    if "fetch_token" in body:
        return fetch_token(body)
    elif "get_saved_tracks" in body:
        return get_saved_tracks(body)
