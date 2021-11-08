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

    def pullAllUserInfo(body,simpleOrComplex=True):
        #simpleOrComplex determines the return type of the function. If True (default) it gives basic user stats for the user "my stats" page. If false it gives a DENSE JSON object used for comparing users at the database level.

        # grab access token from rabbit message
        body = body.split(":")
        sessionId = body[1]
        access_token = get_token_from_db(sessionId)

        #import spotipy
        #from spotipy.oauth2 import SpotifyOAuth
        import json
        #import pika
        import re
        
        scope = "user-library-read,user-top-read,user-follow-read" #scope for account access, we only need read access here.
        TRACK_LIST_LIMIT=40
        SPECIFIED_TIME_RANGE="short_term" #This variable will be utilized by the "self analyzing diff" function to track taste changes.
        ARTIST_LIMIT=50
        SPOTIFY_USERNAME="Test"#default should be overwritten automatically by main script
        WRITE_DIRECTORY="./usersData/"#directory path for writing user files
        #TODO Exception Handling and Logging
        
        sp = spotipy.Spotify(access_token)
        #Gets user's username, this is required for filenaming
        currentUserProfileObj = sp.current_user()
        SPOTIFY_USERNAME=currentUserProfileObj['display_name']
        SPOTIFY_USER_ID=currentUserProfileObj["id"] #Used in playlists function
        currentUserFollowers=currentUserProfileObj["followers"] #Not currently used for anything
        
        def getFollowing(username=None):
            #sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
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
            #sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
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
            #sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
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

            recommendedTacksJson=spot.recommendations(seed_artists=artistSeeds[0:4])
            print((recommendedTacksJson["tracks"][0]).keys())
            returnList=[]
            if includePreview==True:
                for recTrack in recommendedTacksJson["tracks"]:
                    returnList.append([recTrack["name"],((recTrack["artists"])[0])['name'],recTrack["id"],recTrack["popularity"],recTrack["preview_url"]])
            else:
                for recTrack in recommendedTacksJson["tracks"]:
                    returnList.append([recTrack["name"],((recTrack["artists"])[0])['name'],recTrack["id"],recTrack["popularity"]])
            #print(returnList)
            return(returnList)

        def getTopGenres(userStatDict,removeDuplicates=True,topLimit=15):
            #removeDuplicates attempts to "clean" the genres you get back of similar/cliche genres
            #topLimit defines the number of genres returned, from most frequent to least. If there are less genres present than the top limit the function returns less than that.
            genreDict=userStatDict["genres"]
            topGenreNum=0
            topGenreList=[]
            print((userStatDict["genres"]))
            for genre in genreDict:
                if genreDict[genre] > topGenreNum:
                    topGenreList.insert(0,genre)
                    topGenreNum=genreDict[genre]
                else:
                    topGenreList.append(genre)
            #print("\n")
            #print(topGenreList)
            
            if(removeDuplicates==True):
                #previousGene=""
                clicheStrings={" rock":0," jazz":0," indie":0," hip-hop":0," pop":0," folk":0," country":0,"american ":0,"modern ":0,"classical ":0,"british ":0,"mexican ":0,"australian ":0,"canadian ":0}
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
        
        #Establish User Stats Object/Dict
        userStats={}
        #Get all the goodies & write to file!
        #getPlaylists(username=SPOTIFY_USERNAME) <- Could be useful but honestly it contains TOO MUCH data for our current purposes
        userStats=getTopTracks(True,username=SPOTIFY_USERNAME)
        userStats["followedArtists"]=getFollowing(username=SPOTIFY_USERNAME)
        userStats["savedAlbums"]=getSavedAlbums(username=SPOTIFY_USERNAME)
        output=json.dumps(userStats)
        if simpleOrComplex !=True:
            return(output)
        else:
            simplifiedReturnObject=[]
            simplifiedReturnObject.append(getTopGenres(userStats))
            simplifiedReturnObject.append(mostListenedToArtists(userStats))
            simplifiedReturnObject.append(userStats['avgYear'])
            simplifiedReturnObject.append(getRecommendationsFromSpotify(sp,simplifiedReturnObject[1],userStats,genreList=getTopGenres(userStats,removeDuplicates=False, topLimit=100)))
            return(simplifiedReturnObject)

 
    ## Main Entry Point ##

    print(f"from db accessor methods: {body}") # print for debug
    body = body.decode('utf-8')

    if "fetch_token" in body:
        return fetch_token(body)
    elif "get_saved_tracks" in body:
        return get_saved_tracks(body)
    elif "get_stats" in body:
        return pullAllUserInfo(body)
