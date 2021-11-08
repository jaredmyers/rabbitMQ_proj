import sys,os,re,json
import spotipy
import pika

def main():
    #TODO Get Object from database?

    #Pull from user 1
    f = open('sampleDBpull.json')
    dataA = json.load(f)
    f.close()

    #Pull from user 2
    f = open('sampleDBpull2.json')
    dataB = json.load(f)
    f.close()

    compareTopTracks(dataA,dataB)

    #print(dataA.keys())

def compareGenres(JSONdata1,JSONdata2):
    pass

def compareTopTracks(JSONdata1,JSONdata2):
    tracks1=JSONdata1["tracks"]
    tracks2=JSONdata2["tracks"]
    trackMatches1to1=[]
    trackArtistMatches=[]
    #print(tracks1[0])
    for track1 in tracks1:
        track1Name=track1["name"]
        for track2 in tracks2:
            if track1Name==track2["name"]:
                #print("Track MATCH!"+track1Name)
                trackMatches1to1.append([track1Name,track2["id"]])
            else:
                

    pass

def compareArtists(JSONdata1,JSONdata2):
    pass

def compareAlbums(JSONdata1,JSONdata2):
    pass
    
if __name__ == "__main__":
    main()
