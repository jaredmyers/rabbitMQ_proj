import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read,user-top-read"
TRACK_LIST_LIMIT=10

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
results = sp.current_user_top_tracks(limit=TRACK_LIST_LIMIT,offset=0,time_range="short_term")

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
    print(item)
    if(idx<TRACK_LIST_LIMIT):
        f.write(((str(idx))+","+str(item['id'])+","+item["name"]+","+albumDisplay+","+artistsDisplay+","+releaseDisplay+"\n"))
f.close()
