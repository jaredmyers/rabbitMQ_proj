import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import pika
import re

scope = "user-library-read,user-top-read,user-follow-read" #scope for account access, we only need read access here.
TRACK_LIST_LIMIT=40
SPECIFIED_TIME_RANGE="long_term" #This variable will be utilized by the "self analyzing diff" function to track taste changes.
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
    #Establish User Stats Object/Dict
    userStats={}
    #Get all the goodies & write to file!
    #getPlaylists(username=SPOTIFY_USERNAME) <- Could be useful but honestly it contains TOO MUCH data for our current purposes
    userStats=getTopTracks(True,username=SPOTIFY_USERNAME)
    userStats["followedArtists"]=getFollowing(username=SPOTIFY_USERNAME)
    userStats["savedAlbums"]=getSavedAlbums(username=SPOTIFY_USERNAME)
    output=json.dumps(userStats)
    #return(output)

    simplifiedReturnObject=[]
    simplifiedReturnObject.append(getTopGenres(userStats))
    simplifiedReturnObject.append(mostListenedToArtists(userStats))
    simplifiedReturnObject.append(userStats['avgYear'])
    simplifiedReturnObject.append(getRecommendationsFromSpotify(sp,simplifiedReturnObject[1],userStats,genreList=getTopGenres(userStats,removeDuplicates=False, topLimit=100)))
    #print(simplifiedReturnObject[3])
    print(output)

def printUserStats(inputObj):
    pass
    #TODO make a good visual with this data

def getRecommendationsFromSpotify(spot,artistList,userInfo,genreList=None,includePreview=False):
    matchingGenreSeeds=[]
    if genreList != None:
        recSeeds=spot.recommendation_genre_seeds()
        badWords=["post","pre","modern","classic"]
        for genreSeed in recSeeds['genres']:
            for genre in genreList:
                #Big O notation = infinity and beyond
                for word in genre.split():
                    if word in genreSeed:
                        if genreSeed not in matchingGenreSeeds:
                            if word not in badWords:
                                matchingGenreSeeds.append(genreSeed)
    artistSeeds=[]
    for artistObj in artistList:
        artistSeeds.append(artistObj[2])
    #TODO make an input variable that lets you decide what factors you want to weigh for recommendation presentation
    trackSeeds=[]
    for track in userInfo['tracks']:
        trackSeeds.append(track["id"])
    #TODO call for recommended tracks several times with different input parameters, aggregate the results and display the "least popular" tracks to do a "hidden gems" recomender
    recommendedTacksJson=spot.recommendations(seed_artists=artistSeeds[0:4])
    #recommendedTacksJson=spot.recommendations(seed_genres=genreList[0:4]) not good results
    #print((recommendedTacksJson["tracks"][0]).keys())
    returnList=[]
    if includePreview==True:
        for recTrack in recommendedTacksJson["tracks"]:
            returnList.append([recTrack["name"],((recTrack["artists"])[0])['name'],recTrack["id"],recTrack["popularity"],recTrack["preview_url"]])
    else:
        for recTrack in recommendedTacksJson["tracks"]:
            returnList.append([recTrack["name"],((recTrack["artists"])[0])['name'],recTrack["id"],recTrack["popularity"]])
    #print(returnList)
    return(returnList)

def mostListenedToArtists(userStatDict):
    #print(userStatDict['artistFreqByTopTracks'])
    returnFreqList=[]
    
    #print((userStatDict['artistFreqByTopTracks']).items())
    ezSortDict={}
    for artistObj in (userStatDict['artistFreqByTopTracks']).items():
        ezSortDict[artistObj[0]]=(artistObj[1][0])
    #print(ezSortDict)
    
    sortedDict=(dict(sorted(ezSortDict.items(), key=lambda item: item[1])))
    returnList=[]
    for lightWeightArtistObj in sortedDict:
        newTempList=((userStatDict['artistFreqByTopTracks'])[lightWeightArtistObj])
        newTempList.insert(0,lightWeightArtistObj)
        returnList.append(newTempList)
    returnList.reverse()
    #print(returnList) WOOOO!
    return(returnList)
    

def getTopGenres(userStatDict,removeDuplicates=True,topLimit=15):
    #print(userStatDict.keys())
    genreDict=userStatDict["genres"]
    topGenreNum=0
    topGenreList=[]
    #print((userStatDict["genres"]))
    for genre in genreDict:
        if genreDict[genre] > topGenreNum:
            topGenreList.insert(0,genre)
            topGenreNum=genreDict[genre]
        else:
            topGenreList.append(genre)
        
        for displayGenre in topGenreList:
            if genreDict[genre]>genreDict[displayGenre]:
                if topGenreList.index(genre)!=0:
                    topGenreList.insert((topGenreList.index(displayGenre)-1),genre)
                    break
            

    #print("\n")
    #print(topGenreList)
    
    if(removeDuplicates==True):
        previousGene=""
        clicheStrings={" rock":0," jazz":0," indie":0," pop":0," folk":0," country":0,"american ":0,"modern ":0,"classical ":0,"british ":0,"mexican ":0,"australian ":0,"canadian ":0}
        for genre in topGenreList:
            if genre=="rock":
                topGenreList.remove(genre)
            if genre=="pop":
                topGenreList.remove(genre)
            if genre=="electronic":
                topGenreList.remove(genre)
            if genre=='alternative rock': 
                topGenreList.remove(genre)
            if genre=="pop rock":
                topGenreList.remove(genre)
            if genre=="rap":
                topGenreList.remove(genre)
            for cliche in clicheStrings:
                if genre in topGenreList:
                    if clicheStrings[cliche]>5:
                        #print(genre)
                        topGenreList.remove(genre)
                        clicheStrings[cliche]=0
                    if cliche in genre:
                        clicheStrings[cliche]+=1
        if(len(topGenreList)<15):
            return(topGenreList)
        else:
            return(topGenreList[0:topLimit])
    else:
        return(topGenreList[0:topLimit])
    
    


def getPlaylists(username=None):
    #TODO (If feature is included in production build), Convert naming mechanism to JSON
    #Potential idea: compare all playlists between all users and see what matches the most.
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    #playlists = sp.user_playlists(username)
    playlists = sp.current_user_playlists()
    #print(playlists["items"][0]["tracks"])
    playlistWriteList=[]
    #f = open((WRITE_DIRECTORY+username+"Playlists.csv"), "w")
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
        #f.write(writeString)
    #f.close()


def getFollowing(username=None):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    followingArtists = sp.current_user_followed_artists(limit=ARTIST_LIMIT)
    #followingUsers = (sp.current_user_following_users())
    artistList=followingArtists['artists']['items']
    artistReturnList=[]

    #f = open((WRITE_DIRECTORY+username+"Artists.csv"), "w")
    for artist in artistList:
        artistReturnList.append([artist["id"],artist["name"]])
        #f.write((artist['id']+","+artist['name'])+"\n")
    #f.close()
    #print(artistReturnList)
    return(artistReturnList)

def getSavedAlbums(username=None):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    savedAlbums = sp.current_user_saved_albums(limit=20)
    albumList=savedAlbums['items']
    writeOutAlbumList=[]
    returnList=[]
    #print(albumList[0].keys())
    for albumItem in albumList:
        album=albumItem["album"]
        artistsName=""
        tempArtistList=[]
        for artist in album["artists"]:
            tempArtistList.append({"id":artist["id"],"name":artist["name"]})
        returnList.append([album["name"],album["id"],tempArtistList])

        #Semi-Depricated CSV file naming mechanism\/\/\/\/
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
        writeOutAlbumList.append(str(album["id"]+","+album["name"]+","+artistsName))
        #print(album.keys())
    #f = open((WRITE_DIRECTORY+username+"Albums.csv"), "w")
    #for albumInfo in writeOutAlbumList:
        #print(albumInfo)
        #f.write(albumInfo+"\n")
    #f.close()
    return(returnList)

def getTopTracks(doStats,username=None):
    #doStats is a boolean that determines wheather we want to compute a "Genre Analysis" File for the user.
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    results = sp.current_user_top_tracks(limit=TRACK_LIST_LIMIT,offset=0,time_range=SPECIFIED_TIME_RANGE)

    #f = open((WRITE_DIRECTORY+username+"TopTracks.csv"), "w")

    genreStatDict={}
    artistFreqDict={}
    releaseYearStatList=[]
    AvgReleaseYearStat=0
    trackObjList=[]

    for idx, item in enumerate(results['items']):

        artistsDisplay="" 

        if (item["artists"][0])["name"] in artistFreqDict:    
            artistFreqDict[(item["artists"][0])["name"]][0]=(artistFreqDict[(item["artists"][0])["name"]][0]+1)
            #print(artistFreqDict[(item["artists"][0])["name"]][0])
        else:
            artistFreqDict[(item["artists"][0])["name"]]=[1,(item["artists"][0])["id"]]

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
                #print(genre)
                if genre in genreStatDict:
                    genreStatDict[genre]=genreStatDict[genre]+1
                else:
                    genreStatDict[genre]=1

            trackDictObj={}
            trackDictObj["id"]=item["id"]
            trackDictObj["name"]=item["name"]
            trackDictObj["album_name"]=albumDisplay
            trackDictObj["artist"]=item["artists"][0]["name"]
            trackDictObj["popularity"]=item["popularity"]
            releaseYrMatch=re.search(r"\d\d\d\d",item["album"]["release_date"])
            #print("JSON INPUT: "+(item["album"]["release_date"]))
            if(releaseYrMatch!=None):
                #print("Match String: "+releaseYrMatch.group())
                releaseYearStatList.append(int(releaseYrMatch.group()))
            #print(item["album"]["release_year"])
            else:
                pass
            trackObjList.append(trackDictObj)

            #f.write(((str(idx))+","+str(item['id'])+","+item["name"]+","+albumDisplay+","+artistsDisplay+","+releaseDisplay+"\n"))

    #f.close()

    for year in releaseYearStatList:
        AvgReleaseYearStat+=year
    AvgReleaseYearStat=int(AvgReleaseYearStat/(len(releaseYearStatList)))
    #print("Year List: "+str(releaseYearStatList))
    #print("Genre Dict: "+str(genreStatDict)+"\n")
    #print("Avg Year: "+str(AvgReleaseYearStat)+"\n")
    #print("ArtistFreqDict: "+str(artistFreqDict)+"\n")
    returnDict={"genres":genreStatDict,"tracks":trackObjList,"avgYear":AvgReleaseYearStat,"artistFreqByTopTracks":artistFreqDict}
    return(returnDict)

if __name__ == "__main__":
    main()
