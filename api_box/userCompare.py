import sys,os,re,json
import spotipy
import pika

def main():
    #TODO Get Object from database?

    #Pull from user 1
    f = open('sampleDBpull4.json')
    dataA = json.load(f)
    f.close()

    #Pull from user 2
    f = open('sampleDBpull3.json')
    dataB = json.load(f)
    f.close()

    output=[]
    #print(dataB.keys())
    output.append(compareTracks(dataA,dataB))
    output.append(compareTracks(dataA,dataB,isTopTracks=False))
    output.append(compareGenres(dataA,dataB))
    output.append(compareArtistsFollowed(dataA,dataB))
    output.append(compareAlbums(dataA,dataB))
    #print(compareAlbums(dataA,dataB))
    #output.append()
    #compareFreqListenedToArtists(dataA,dataB)
    #print(dataA.keys())
    #print(output)
    return(output)

    

def compareGenres(JSONdata1,JSONdata2):
    #print(JSONdata1["genres"])
    #graspingForStraws=False
    genreMatches=[]
    for genre in JSONdata1["genres"]:
        #print(genre)
        if genre in JSONdata2["genres"]:
            genreMatches.append(genre)

    if(len(genreMatches))<7:
        if "rock" not in genreMatches:
            genreMatches.append("rock")
        return(genreMatches)
    else:
        for genre in genreMatches:
            badGenres=["alternative rock","rock","pop","electronic"]
            if len(genreMatches)>=7:
                for badGenre in badGenres:
                    if badGenre==genre:
                        genreMatches.remove(genre)
    #print(genreMatches)
    return(genreMatches)

def compareTracks(JSONdata1,JSONdata2,isTopTracks=True):
    #Returns 3 Lists in a larger list object
    #Index 0 = a list of track objects (dictionaries) of tracks that were a 1 to 1 match between top 50 songs
    #Index 1 = a list of 
    #print((JSONdata1["tracks"][0])['artist'])
    tracks1=JSONdata1["tracks"]
    tracks2=JSONdata2["tracks"]
    if isTopTracks == False:
        tracks1=JSONdata1["libraryTracks"]
        tracks2=JSONdata2["libraryTracks"]

    trackMatches1to1=[]
    trackArtistMatchesChecklist=[]
    trackArtistMatchesReturnList=[]
    trackAlbumMatchesChecklist=[]
    trackAlbumMatchesReturnList=[]
    #print(tracks1[0])

    def findInReturnList(sampReturnList,checkObj):
        if(len(sampReturnList)!=0):
            for itemObj in sampReturnList:
                if itemObj[0]==checkObj:
                    itemObj[1]=itemObj[1]+1

    for track1 in tracks1:
        track1Name=track1["name"]
        for track2 in tracks2:
            #print( track1["artist"]+" versus "+track2["artist"])

            if ((track1Name==track2["name"])):
                #print("Track MATCH!"+track1Name)
                trackMatches1to1.append(track1)
            #print(track1['album_name'])
            if track1["album_name"]==track2["album_name"]:
                #print(track1['album_name'])
                if track1["album_name"] not in trackAlbumMatchesChecklist:
                    trackAlbumMatchesChecklist.append(track1["album_name"])
                    trackArtistMatchesReturnList.append([track1["album_name"],1])
                if track1["album_name"] in trackAlbumMatchesChecklist:
                    findInReturnList(trackAlbumMatchesReturnList,track1["album_name"])
            if (track1["artist"]==track2["artist"]):
                #print("WE GOT A BINGO "+track1["artist"])
                if track1["artist"] not in trackArtistMatchesChecklist:
                    trackArtistMatchesChecklist.append(track1["artist"])
                    trackArtistMatchesReturnList.append([track1["artist"],1])
                else:
                    findInReturnList(trackArtistMatchesReturnList,track2["artist"])


    returnList=[trackMatches1to1,trackArtistMatchesReturnList,trackAlbumMatchesReturnList]
    #print(trackAlbumMatchesReturnList)
    #print("\n")
    return(returnList)

def compareArtistsFollowed(JSONdata1,JSONdata2):
    #print(JSONdata1.keys())
    sameArtists=[]
    #print(JSONdata1['followedArtists'])
    for artist1 in JSONdata1["followedArtists"]:
        for artist2 in JSONdata2["followedArtists"]:
            if artist1[0] == artist2[0]:
                sameArtists.append(artist1)
    #print(sameArtists)
    return sameArtists

def compareFreqListenedToArtists(JSONdata1,JSONdata2):
    sameFreqArtists=[]
    #print((JSONdata1["artistFreqByTopTracks"]).keys())
    for artist1 in JSONdata1["artistFreqByTopTracks"]:
        for artist2 in JSONdata2["artistFreqByTopTracks"]:
            if artist1 == artist2:
                #print(artist2)
                pass

def compareAlbums(JSONdata1,JSONdata2):
    #print(JSONdata1['savedAlbums'])
    albumsMatched=[]
    for album1 in JSONdata1["savedAlbums"]:
        for album2 in JSONdata2["savedAlbums"]:
            if album1[1] == album2[1]:
                albumsMatched.append(album1)
    #print((albumsMatched))
    return(albumsMatched)    

if __name__ == "__main__":
    main()
