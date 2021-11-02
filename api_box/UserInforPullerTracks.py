import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

scope = "user-library-read,user-top-read,user-follow-read"
TRACK_LIST_LIMIT=10
SPECIFIED_TIME_RANGE="short_term" #This variable will be utilized by the "self analyzing diff" function to track taste changes.
ARTIST_LIMIT=50

def main():
    #getPlaylists()
    #getTopTracks()
    getFollowing()

def getPlaylists():
    #Potential idea: compare all playlists between all users and see what matches the most.
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    #playlists = sp.user_playlists(username)
    playlists = sp.current_user_playlists()
    print(playlists["items"])

def getFollowing():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    followingArtists = sp.current_user_followed_artists(limit=ARTIST_LIMIT)
    #followingUsers = (sp.current_user_following_users())
    artistList=followingArtists['artists']['items']
    for artist in artistList:
        print(artist['name'])

def getTopTracks():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    results = sp.current_user_top_tracks(limit=TRACK_LIST_LIMIT,offset=0,time_range=SPECIFIED_TIME_RANGE)

    f = open("userfile2.csv", "w")

    for idx, item in enumerate(results['items']):
        #print(item.keys())
        #  track = item['tr']
        #print((item["album"]).keys())

        artistsDisplay="" 
        if(len(item["artists"])>1):
            #
            intx=0
            for artist in item["artists"]:
                if(artist == item["artists"][(len(item["artists"])-1)]):
                    artistsDisplay=artistsDisplay+" & "+str(artist["name"])
                else:
                    artistsDisplay=artistsDisplay+" , "+str(artist["name"])
            intx=intx+1
        else:
            #print(item["artists"][0]["name"])
            artistsDisplay=(item["artists"][0]["name"])
            #print(artistsDisplay)

        albumDisplay=item["album"]["name"]
        releaseDisplay=item["album"]["release_date"]
        #print(item)
        if(idx<TRACK_LIST_LIMIT):
            f.write(((str(idx))+","+str(item['id'])+","+item["name"]+","+albumDisplay+","+artistsDisplay+","+releaseDisplay+"\n"))
    f.close()

if __name__ == "__main__":
    main()
