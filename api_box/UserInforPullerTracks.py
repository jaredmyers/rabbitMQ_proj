import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import pika
import re

scope = "user-library-read,user-top-read,user-follow-read" #scope for account access, we only need read access here.
TRACK_LIST_LIMIT=40
SPECIFIED_TIME_RANGE="short_term" #This variable will be utilized by the "self analyzing diff" function to track taste changes.
ARTIST_LIMIT=50
SPOTIFY_USERNAME="Test"#default should be overwritten automatically by main script
SPOTIFY_USER_ID=""#see main script

WRITE_DIRECTORY="./usersData/"#directory path for writing user files
#TODO Exception Handling and Logging   

def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    #Gets user's username, this is required for filenaming
    currentUserProfileObj = sp.current_user()
    SPOTIFY_USERNAME=currentUserProfileObj['display_name']
    SPOTIFY_USER_ID=currentUserProfileObj["id"] #Used in playlists function
    currentUserFollowers=currentUserProfileObj["followers"] #Not currently used for anything

    #Get all the goodies & write to file!
    getPlaylists(username=SPOTIFY_USERNAME)
    getTopTracks(True,username=SPOTIFY_USERNAME)
    getFollowing(username=SPOTIFY_USERNAME)
    getSavedAlbums(username=SPOTIFY_USERNAME)

def getPlaylists(username=None):
    
    #Potential idea: compare all playlists between all users and see what matches the most.
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    #playlists = sp.user_playlists(username)
    playlists = sp.current_user_playlists()
    #print(playlists["items"][0]["tracks"])
    playlistWriteList=[]
    f = open((WRITE_DIRECTORY+username+"Playlists.csv"), "w")
    for playlist in playlists["items"]:
        #print(playlist["name"])
        playlistTracksObj=sp.user_playlist_tracks(SPOTIFY_USER_ID, playlist_id=playlist["id"])
        #print(playlistTracksObj["items"])
        writeString=playlist["id"]+","+playlist["name"]+","+"["
        for trackObj in (playlistTracksObj["items"]):
            #print(trackObj["track"]["name"])
            writeString=writeString+"["+(trackObj["track"]["id"])+","+(trackObj["track"]["name"])
            writeString=writeString+","+"["
            for artist in trackObj["track"]["artists"]:
                writeString=writeString+"["+artist["id"]+","+artist["name"]+"]"
                if artist != (trackObj["track"]["artists"])[(len(trackObj["track"]["artists"])-1)]:
                    writeString=writeString+","
            writeString=writeString+"]]"
            if trackObj != (playlistTracksObj["items"])[(len(playlistTracksObj["items"])-1)]:
                writeString=writeString+","
        writeString=writeString+"]\n"
        f.write(writeString)
    f.close()


def getFollowing(username=None):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    followingArtists = sp.current_user_followed_artists(limit=ARTIST_LIMIT)
    #followingUsers = (sp.current_user_following_users())
    artistList=followingArtists['artists']['items']
    f = open((WRITE_DIRECTORY+username+"Artists.csv"), "w")
    for artist in artistList:
        f.write((artist['id']+","+artist['name'])+"\n")
    f.close()

def getSavedAlbums(username=None):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    savedAlbums = sp.current_user_saved_albums(limit=20)
    #print(savedAlbums.keys())
    albumList=savedAlbums['items']
    writeOutAlbumList=[]
    #print(albumList[0].keys())
    for albumItem in albumList:
        album=albumItem["album"]
        artistsName=""
        for artistObj in album["artists"]:
            if artistsName=="":
                #artistsName="["
                pass
            else:
                artistsName=artistsName+","
            if(len(album["artists"])==1):
                artistsName="["+(album["artists"][0])["id"]+","+(album["artists"][0])["name"]+"]"
            else:
                artistsName=artistsName+"["+artistObj["id"]+","+ artistObj["name"]+"]" 
        #print(artistsName)
        #print(album["id"]+","+album["name"]+","+artistsName)
        writeOutAlbumList.append(str(album["id"]+","+album["name"]+","+artistsName))
        #print(album.keys())
    f = open((WRITE_DIRECTORY+username+"Albums.csv"), "w")
    for albumInfo in writeOutAlbumList:
        #print(albumInfo)
        f.write(albumInfo+"\n")
    f.close()

def getTopTracks(doStats,username=None):
    #doStats is a boolean that determines wheather we want to compute a "Genre Analysis" File for the user.
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    results = sp.current_user_top_tracks(limit=TRACK_LIST_LIMIT,offset=0,time_range=SPECIFIED_TIME_RANGE)

    f = open((WRITE_DIRECTORY+username+"TopTracks.csv"), "w")

    genreStatDict={}
    artistFreqDict={}
    releaseYearStatList=[]
    AvgReleaseYearStat=0

    for idx, item in enumerate(results['items']):

        artistsDisplay="" 
        if(len(item["artists"])>1):
            intx=0
            for artist in item["artists"]:
                if(artist == item["artists"][(len(item["artists"])-1)]):
                    artistsDisplay=artistsDisplay+" & "+str(artist["name"])
                else:
                    artistsDisplay=artistsDisplay+" , "+str(artist["name"])
            intx=intx+1
        else:
            artistsDisplay=(item["artists"][0]["name"])
        albumDisplay=item["album"]["name"]
        releaseDisplay=item["album"]["release_date"]
        #print(item)
        if(idx<TRACK_LIST_LIMIT):
            #TODO Store Preview URL
            #TODO Store Track Popularity
            #TODO CREATE A DICTIONARY OF GENRES CALLING AN AUDIO ANALYSIS FOR EACH TRACK IN LIST
            artist = sp.artist(item["artists"][0]["external_urls"]["spotify"])
            trackGenreList=("artist genres:", artist["genres"])[1]
            #print(trackGenreList)
            for genre in trackGenreList:
                print(genre)
                if genre in genreStatDict:
                    genreStatDict[genre]=genreStatDict[genre]+1
                else:
                    genreStatDict[genre]=1

            trackDictObj={}
            trackDictObj["id"]=item["id"]
            trackDictObj["name"]=item["name"]
            trackDictObj["album_name"]=albumDisplay
            releaseYrMatch=re.search(r"\d\d\d\d$",item["album"]["release_date"])
            if(releaseYrMatch!=None):
                print(releaseYrMatch.string)
                releaseYearStatList.append(int(releaseYrMatch.string))
            #print(item["album"]["release_year"])
            else:
                pass

            f.write(((str(idx))+","+str(item['id'])+","+item["name"]+","+albumDisplay+","+artistsDisplay+","+releaseDisplay+"\n"))

    f.close()

    for year in releaseYearStatList:
        AvgReleaseYearStat+=year
    AvgReleaseYearStat=(AvgReleaseYearStat/(len(releaseYearStatList)))
    print("yearList= "+str(releaseYearStatList))
    print("Genre Dict: "+str(genreStatDict)+"\n")
    print("Avg Year: "+str(AvgReleaseYearStat)+"\n")

if __name__ == "__main__":
    main()
