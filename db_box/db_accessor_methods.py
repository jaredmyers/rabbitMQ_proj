import mysql.connector
import credentials as cred
import bcrypt, uuid, datetime, random, json


def accessor_methods(body,queue):

    conn = mysql.connector.connect(
    host=cred.db_host,
    user=cred.db_user,
    password=cred.db_pw,
    database=cred.db_database
    )
    

    def check_session(body):
        '''checks to see if session exists and is still valid'''
        sessionId = body
        token_expiry = 0.50

        # grab the given session time
        query = "SELECT sessionId, sTime FROM sessions WHERE sessionId = %s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        
        # return false if session doesn't exist,
        # check sessions time, delete if expired
        if not query_result:
            return ''
        else:
            token_issue_date = query_result[0][1]
            current_time = datetime.datetime.now()
            diff = current_time - token_issue_date
            diff_hours = diff.total_seconds()/3600

            if diff_hours > token_expiry:
                delete_session(f'delete:{sessionId}')
                return ''

            return query_result[0][0]

    def delete_session(body):
        '''deletes a session'''
        body = body.split(':')
        body = body[1]
        sessionId = body

        query = "DELETE FROM sessions WHERE sessionId = %s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        conn.commit()
        
        return '1'

    def generate_sessionId(username):
        '''internal method - generates a sessionId'''
        #grab current usernames userID
        query = "SELECT userID FROM users WHERE uname = %s;"
        val = (username,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        userID = query_result[0][0]

        sessionId = uuid.uuid4().hex

        # if user has a session, delete it
        query = "DELETE FROM sessions WHERE userID=%s;"
        val = (userID,)
        cursor.execute(query, val)
        conn.commit()
        
        #insert newly generated sessionId in sessions
        query = "INSERT into sessions (userID, sessionId) values (%s, %s);"
        val = (userID, sessionId)
        cursor.execute(query, val)
        conn.commit()
        
        return sessionId
    
    def register_user(body):
        body = body.split(':')
        username = body[1]
        hashed_pw = body[2]

        # checks if username already exists
        query = "SELECT userID FROM users WHERE uname = %s;"
        val = (username,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # create if username doesn't exist
        if not query_result:
            query = "insert into users (uname, pw) values (%s, %s);"
            val = (username, hashed_pw)
            cursor.execute(query, val)
            conn.commit()
            
            return generate_sessionId(username)
        else:
            return ''

    def login(body):
        given_creds = body.split(":")
        username = given_creds[1]
        password = given_creds[2]
        
        #grabs users username and hashed password
        query = "SELECT uname, pw FROM users WHERE uname = %s;"
        val = (username,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        
        #return false if user doesn't exist
        if not query_result:
            return ''
        
        uname = query_result[0][0]
        hashed = query_result[0][1]

        # check is given pw matched hashed pw
        cred_match = bcrypt.checkpw(password.encode(),hashed.encode())
        print("credmatch from accessor methods: ", cred_match) # log

        if cred_match:
            return generate_sessionId(username)

            query = "SELECT userID FROM users WHERE uname = %s;"
            val = (username,)
            cursor.execute(query, val)
            query_result = cursor.fetchall()
            userID = query_result[0][0]

            sessionId = uuid.uuid4().hex

            query = "DELETE FROM sessions WHERE userID=%s;"
            val = (userID,)
            cursor.execute(query, val)
            conn.commit()
        
            query = "INSERT into sessions (userID, sessionId) values (%s, %s);"
            val = (userID, sessionId)
            cursor.execute(query, val)
            conn.commit()

            print("sessionId from accessor methods: " + sessionId)
            
            return sessionId
        
        
        return ''

    def get_threads():
        '''get all forum threads for forum page'''
        # grab all relevant forum thread info
        query = "select users.uname, threads.threadID, threads.title, threads.content, threads.ts from users,threads where users.userID=threads.userID order by ts desc;"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()

        # json strings delimited by semicolon
        json_string = ''
        for i in query_result:
            json_string += '{"author":"'+i[0]+'",'
            json_string += '"threadID":"'+str(i[1])+'",'
            json_string += '"title":"'+i[2]+'",'
            json_string += '"content":"'+i[3]+'",'
            json_string += '"date":"'+i[4].strftime('%Y-%m-%d')+'"}'
            json_string += ';'

        return json_string

    def get_reply_page(body):
        '''gets replies for a given forum thread for reply page'''
        body = body.split(":")
        threadID = body[1]

        # grab all relevant forum thread information
        query = "select users.uname, threads.threadID, threads.title, threads.content, threads.ts from users,threads where users.userID=threads.userID and threads.threadID=%s;"
        val = (threadID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # forum thread information, json strings delim by semicolon
        thread_json_string = ''
        for i in query_result:
            thread_json_string += '{"author":"'+i[0]+'",'
            thread_json_string += '"threadID":"'+str(i[1])+'",'
            thread_json_string += '"title":"'+i[2]+'",'
            thread_json_string += '"content":"'+i[3]+'",'
            thread_json_string += '"date":"'+i[4].strftime('%Y-%m-%d')+'"}'
            thread_json_string += '+'

        # grab all relevant reply data for the given forum thread
        query = "select users.uname, replies.content, replies.replyts from users,replies where users.userID=replies.userID and replies.threadID=%s order by replies.replyts desc;"
        val = (threadID,)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # reply information, json strings delim by semicolons
        replies_json_string = ''
        for i in query_result:
            replies_json_string += '{"author":"'+i[0]+'",'
            replies_json_string += '"content":"'+i[1]+'",'
            replies_json_string += '"date":"'+i[2].strftime('%Y-%m-%d')+'"}'
            replies_json_string += ';'

        return (thread_json_string + replies_json_string)

    def make_new_thread(body):
        '''creates new forum thread on forum page'''
        body = body.split(':')
        sessionId = body[1]
        threadname = body[2]
        threadcontent = body[3]

        # grab posting users userID
        query = "select userID from sessions where sessionId=%s;"
        val =(sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        
        # returns false if session valid
        if not query_result:
            return ''

        userID = query_result[0][0]
        
        #inserts new forum post into threads table
        query = "insert into threads (userID, title, content) values (%s,%s,%s);"
        val = (userID, threadname, threadcontent)
        cursor.execute(query, val)
        conn.commit()

        return '1'

    def make_new_reply(body):
        '''creates new reply on reply page'''
        body = body.split(':')
        sessionId = body[1]
        threadID = body[2]
        replycontent = body[3]

        # grab posting users userID
        query = "select userID from sessions where sessionId=%s;"
        val =(sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # return false if session not valid
        if not query_result:
            return ''
        userID = query_result[0][0]

        # inserts new reply into replies table
        query = "insert into replies (threadID, userID, content) values (%s,%s,%s);"
        val = (threadID,userID, replycontent)
        cursor.execute(query, val)
        conn.commit()

        return '1'

    def store_token(body):
        '''stores the spotify api token, token life is 1 hour'''
        body = body.split(":")
        sessionId = body[1]
        api_token = body[2]

        # grab users userID
        query = "select userID from sessions where sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # return false is session not valid
        if not query_result:
            return ''

        userID = query_result[0][0]

        # insert api token into apitokens table
        query = "insert into apitokens (apitoken, userID) values (%s, %s);"
        val = (api_token, userID)
        cursor.execute(query, val)
        conn.commit()

        return '1'

    def delete_token(body):
        ''' internal method - deletes api token'''
        body = body.split(":")
        sessionId = body[1]

        # deletes api token based on session identity 
        query = "delete apitokens from apitokens inner join sessions on sessions.userID=apitokens.userID where sessions.sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        conn.commit()

    def get_token(body):
        '''grabs api token from storage to make a users api calls'''
        body = body.split(":")
        sessionId = body[1]
        api_expiry = 0.9 

        # grabs users api token and issue date
        query = "select apitokens.apitoken, apitokens.tTime from apitokens,sessions where sessions.sessionId = %s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # returns false if users api token doesn't exist
        # removes token if it has expired
        if not query_result:
            return ''
        else:
            api_issue_date = query_result[0][1]
            current_time = datetime.datetime.now()
            diff = current_time - api_issue_date
            diff_hours = diff.total_seconds()/3600

            if diff_hours > api_expiry:
                delete_token(f'delete_token:{sessionId}')
                return ''

        access_token = query_result[0][0]

        return access_token

    def check_friend(body):
        ''' internal method'''
        pass
    
    def add_friend(body):
        '''adds friend to users friend list'''
        body = body.split(":")
        sessionId = body[1]
        username = body[2]

        ## this whole function deserves a more elegant SQL solution. I gotta move on. ##

        ## grab current users userID
        query = "select userID from sessions where sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        userID1 = cursor.fetchall()[0][0]

        ## grab potential friends userID
        query = "select userID from users where uname=%s;"
        val = (username,)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        #returns false if potential friend doesn't exist
        if not query_result:
            return ''
        
        userID2 = query_result[0][0]

        # return false if user tries to friend self
        if userID1 == userID2:
            return ''

        # check if they are already friends
        query = "select * from friends where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
        val = (userID1,userID2,userID2,userID1)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # returns false if already friends
        if query_result:
            return ''

        ## add friend relationship to friends table
        query = "insert into friends (userID1, userID2) values (%s, %s);"
        val = (userID1, userID2)
        cursor.execute(query, val)
        conn.commit()

        return '1'

    def get_friends(body):
        '''fetches users friends for their friend list'''
        body = body.split(":")
        sessionId = body[1]

        ## this whole function deserves a more elegant SQL solution. I gotta move on. ##

        # get current users userID
        query = "select userID from sessions where sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        userID = cursor.fetchall()[0][0]

        # grabbing all the users friend relationships
        query = "select * from friends where userID1=%s or userID2 =%s;"
        val = (userID,userID)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # return false if user has no friends
        if not query_result:
            return ''

        # parsing out just the users friends as userIDs
        userID_list = []
        for i in query_result:
            for p in i:
                if p != userID:
                    userID_list.append(p) # these are userID ints from db
        
        # selecting all the users (again, no time to fancy-fi this)
        query = "select * from users;"
        cursor.execute(query)
        query_result = cursor.fetchall()

        # grabbing all the users names of all the users friends
        friend_names = ''
        for i in query_result:
            if i[0] in userID_list:
                friend_names += i[1] + ":" # these are uname strings from db

        return friend_names

    def create_chat(body):
        '''generates the chatroom table for the specific chat'''
        body = body.split(":")
        print(body)
        sessionId = body[1]
        chat_recipient = body[2]

        # grab chat creators username and userID
        query = "select users.uname, users.userID from users inner join sessions on sessions.userID=users.userID where sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        uname1 = query_result[0][0]
        userID1 = query_result[0][1]

        # grab chat recipient userID
        query = "select userID from users where uname=%s;"
        val = (chat_recipient,)
        cursor.execute(query, val)
        userID2 = cursor.fetchall()[0][0]
        
        #check if chatroom already exists
        query = "select roomID from friends where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
        val = (userID1,userID2,userID2,userID1)
        cursor.execute(query, val)
        query_result = cursor.fetchall()
        
        # create chatroom if one doesn't exist, update chatroom name into friends table
        #f string vars all internal values (not user input)
        if not query_result[0][0]:
            roomID = f"{uname1}_{chat_recipient}"
            query = f"create table if not exists {roomID} (messageID INT AUTO_INCREMENT PRIMARY KEY, uname VARCHAR(255), message TEXT);"
            val = (roomID,)
            cursor.execute(query)
            conn.commit()

            query = "update friends set roomID=%s where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
            val = (roomID, userID1,userID2,userID2,userID1)
            cursor.execute(query, val)
            conn.commit()

            return roomID
        
        # returns chatroom name if it existed
        return query_result[0][0]
    
    def get_username(body):
        '''grabs users username'''
        body = body.split(":")
        sessionId = body[1]

        # grabs username based on session 
        query = "select users.uname from users inner join sessions on sessions.userID=users.userID where sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        username = cursor.fetchall()[0][0]

        return username

    def new_chat_message(body):
        '''creates a new chat message for chatroom id'''
        body = body.split(":")
        username = body[1] 
        chat_message = body[2]
        room_id = body[3]

        # inserts new chat message into chatroom
        query = f"insert into {room_id} (uname, message) values (%s, %s);"
        val = (username, chat_message)
        cursor = conn.cursor()
        cursor.execute(query, val)
        conn.commit()

        return '1'

    def get_chat_messages(body):
        '''gets all chat messages for chatroom id to populate chatbox'''
        body = body.split(":")
        room_id = body[1]

        # select message history for limiting
        query = f"select messageID from {room_id};"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()

        # limit message history to latest 20
        if len(query_result) > 20:
            query = f"delete from {room_id} order by messageID ASC LIMIT 1;"
            cursor.execute(query)
            conn.commit()

        # get all remaining messages
        query = f"select uname, message from {room_id}"
        cursor.execute(query)
        query_result = cursor.fetchall()

        # sent back formated as a string to be decompressed into a lists
        # using ; delim for lists, : delim elements
        chat_records = ''
        for i in query_result:
            chat_records += i[0] + ":" + i[1] + ";"

        return chat_records

    def store_stats(body):
        body = body.split("?&#))")
        sessionId = body[1]
        json = body[2]

        # grab users userID
        query = "select userID from sessions where sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        userID = cursor.fetchall()[0][0]

        # inserts new json into stats
        query = "insert into stats (userID, stat) values (%s, %s);"
        val = (userID, json)
        cursor = conn.cursor()
        cursor.execute(query, val)
        conn.commit()

        return '1'

    def check_stats(body):
        body = body.split(':')
        sessionId = body[1]

        print("from check stat")
        print(body)
        print(sessionId)

        # grab users userID
        query = "select userID from sessions where sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        userID = cursor.fetchall()[0][0]

        # check json
        query = "select userID from stats where userID=%s;"
        val = (userID,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        if not query_result:
            return ''
        else:
            return '1'

    def get_compare_data(sessionId):

        current_user = get_username("get_username:" + sessionId)

        query = "select users.uname, stats.stat from users,stats where users.userID=stats.userID;"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()

        product = [current_user, query_result]
        print(product)

        ## format [current user name, [(username, json), (username, json)..]]
        return product
    
    def convert_getUsersForListComparison(recommended):
        # incoming format [['kingelmer', ['wizzywiz', 5]]]
        # converting to string -- edit now just json.dumps

        if not recommended:
            recommended = ["none"]

        print("from convert script: ")
        print(recommended)

        return json.dumps(recommended)
        '''
        recommended_friends = ''
        for i in recommended:
            recommended_friends += i[0] + ":" + str(i[1][1]) + ";"

        print("returning recommended_friends")
        print(recommended_friends)
        return recommended_friends
        '''



    def getUsersForListComparison(body):
        body = body.split(':')
        sessionId = body[1]
        #typeOfRequest= body[2]
        #Type of request is either "get_list_info" or "get_detailed info"
        # List info is used when displaying the list of users. Get detailed info is when getting a specific user
        
        def sortDetails(sampleList):
            for i in range(len(sampleList)):
            # We want the last pair of adjacent elements to be (n-2, n-1)
                for j in range(len(sampleList) - 1):
                    if sampleList[j][1][1] > sampleList[j+1][1][1]:
                        # Swap
                        sampleList[j], sampleList[j+1] = sampleList[j+1], sampleList[j]
            return(sampleList)  
        
        tableData=[]
        tableData=get_compare_data(sessionId)
        currentUsername=tableData[0]
        currentJSON=""
        comparisonListDetails=[]
        sortDict={}
        print("TEST_1: Current Username is: "+currentUsername)
        
        
        #if len(tableData) <= 1:
            #raise Exception("Not enough user information in database to make comparison list!\n")
                #return(false)
        #debugVar=1
        
        for userObject in tableData[1]: #in the spirit of as little queries as possible hahahaha
            #print("Cycle "+(str(debugVar))+" of "+(str(len(tableData[1]))))
            if userObject[0]==currentUsername:
                currentJSON=userObject[1]
        
        for userObject in tableData[1]:
            if userObject[0]==currentUsername:
                pass
            else:
                listingDetails=compare_users(currentJSON,userObject[1],IS_SIMPLE=True)
                comparisonListDetails.append([userObject[0],listingDetails])
                sortDict[userObject[0]]=listingDetails[1]
        sortedSortDict=sorted(sortDict.items(), key=lambda x: x[1], reverse=True)

        
        #return(sortedReturnList)
        # this returns a converted version of the return which is a string
        print(sortDetails(comparisonListDetails))
        return convert_getUsersForListComparison(sortDetails(comparisonListDetails))
        #return convert_getUsersForListComparison(sortedReturnList)

    def convert_compareUsersDetailed(body):
        '''converts compareUsersDetailed into string for transport''' 

        return json.dumps(body)

        index0 = body[0]
        mutual_tracks = ''
        try: 
            for i in index0[0]:
                mutual_tracks += i['name'] + ':' + i['artist'] + ';'
            mutual_tracks += '+'
        except:
            mutual_tracks = ';+'
        
        mutual_artists = ''
        try:
            for i in index0[1]:
                mutual_artists += i[0] + ';'
            mutual_artists += '+'
        except:
            mutual_artists += ';+'

        index2 = body[2]
        mutual_genres = ''
        try:
            for i in index2:
                mutual_genres += i + ':'
            mutual_genres += ';+'
        except:
            mutual_genres = ';+'

        index4 = body[4]
        saved_albums = ''
        try:
            for i in index4: 
                saved_albums += i[2][0]['name'] + ':' + i[0] + ';'
            saved_albums += '+'
        except:
            saved_albums += ';+'

        song_preview = body[5]

        package = mutual_tracks + mutual_artists + mutual_genres + saved_albums + song_preview


        return package

    def compareUsersDetailed(body):
        body = body.split(":")
        sessionId=body[1]
        specifiedUserUsername=body[2]
        
        bigCompareData=get_compare_data(sessionId)
        currentUserUsername=bigCompareData[0]


        currentUserJSON=""
        specifiedUserJSON=""

        for userDataObj in bigCompareData[1]:
            if userDataObj[0]==specifiedUserUsername:
                specifiedUserJSON=userDataObj[1]
            if userDataObj[0]==currentUserUsername:
                currentUserJSON=userDataObj[1]
        
        print(compare_users(currentUserJSON,specifiedUserJSON,IS_SIMPLE=False))        
        return convert_compareUsersDetailed(compare_users(currentUserJSON,specifiedUserJSON,IS_SIMPLE=False))
            #return(compare_users(currentUserJSON,specifiedUserJSON,IS_SIMPLE=False))
            

    def compare_users(userJSON1,userJSON2,IS_SIMPLE=False):

        #import json
        def getUserBsTopTrack(JSONdata2):
            partA='<iframe src="https://open.spotify.com/embed/track/'
            partB='"width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
            return(partA+(JSONdata2["tracks"][0])["id"]+partB)

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
                    #print(track1.keys())
                    if ((track1Name==track2["name"])):
                        #print("Track MATCH!"+track1Name)
                        trackMatches1to1.append(track1)
                    #print(track1['album_name'])
                    if track1["album_name"]==track2["album_name"]:
                        #print(track1['album_name'])
                        if track1["album_name"] not in trackAlbumMatchesChecklist:
                            trackAlbumMatchesChecklist.append(track1["album_name"])
                            trackAlbumMatchesReturnList.append([track1["album_name"],1])
                        if track1["album_name"] in trackAlbumMatchesChecklist:
                            findInReturnList(trackAlbumMatchesReturnList,track1["album_name"])
                    if ("artist" in track1.keys()) and ("artist" in track2.keys()):
                        if (track1["artist"]==track2["artist"]):
                            #print("WE GOT A BINGO "+track1["artist"])
                            if track1["artist"] not in trackArtistMatchesChecklist:
                                trackArtistMatchesChecklist.append(track1["artist"])
                                trackArtistMatchesReturnList.append([track1["artist"],1])
                            else:
                                findInReturnList(trackArtistMatchesReturnList,track2["artist"])
                    else:
                        #print("No artist associated with: "+track1["name"])
                        pass

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

        if(str(type(userJSON1))!="<class 'dict'>"):
            print("did not crash")
            dataA = json.loads(userJSON1)
            #f.close()
        else:
            dataA = userJSON1

        if(str(type(userJSON2))!="<class 'dict'>"):
            dataB = json.loads(userJSON2)
        else:
            dataB=userJSON2
            
        print("DataA Input:")
        print(dataA)
        
        print("DataB Input:")
        print(dataB)

        output=[]

        output.append(compareTracks(dataA,dataB))
        output.append(compareTracks(dataA,dataB,isTopTracks=False))
        output.append(compareGenres(dataA,dataB))
        output.append(compareArtistsFollowed(dataA,dataB))
        output.append(compareAlbums(dataA,dataB))
        output.append(getUserBsTopTrack(dataB))
        #output.append([dataA["avgYear"],dataB["avgYear"]],(dataA["avgYear"]-dataB["avgYear"]))
        
        print(output)
        print("\n")

        if IS_SIMPLE==False:
            return(output)
        else:
            return([dataB["username"],len(str(output))])
        

    def remove_friend(body):
        body = body.split(":")
        sessionId = body[1]
        username = body[2]

        ## grab current users userID
        query = "select userID from sessions where sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        userID1 = cursor.fetchall()[0][0]

        ## grab potential friends userID
        query = "select userID from users where uname=%s;"
        val = (username,)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        #returns false if potential friend doesn't exist
        if not query_result:
            return ''

        userID2 = query_result[0][0]

        # return false if user tries to delete self
        if userID1 == userID2:
            return ''

        # check if they are already friends & get potential roomID
        query = "select * from friends where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
        val = (userID1,userID2,userID2,userID1)
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # returns false if not friends
        if not query_result:
            return ''
        
        # delete chat table if exists
        if query_result[0][2]:
            roomID = query_result[0][2]

            # delete corresponding chat table
            query = f"drop table {roomID}"
            cursor.execute(query)
            conn.commit()
        
        ## remove friend relationship to friends table
        query = "delete from friends where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
        val = (userID1, userID2, userID2, userID1)
        cursor.execute(query, val)
        conn.commit()

        return '1'


## Main entry point

    '''
    Main Entry point to database accessor methods
    called by the rabbitMQ subscriber callback
    acts as gigantic switch board
    
    '''
    print(f"from db accessor methods: {body}")
    body = body.decode('utf-8')

    if "delete" in body:
        return delete_session(body)
    elif "register" in body:
        return register_user(body)
    elif "login" in body:
        return login(body)
    elif "get_threads" in body:
        return get_threads()
    elif "get_reply_page" in body:
        return get_reply_page(body)
    elif "new_thread" in body:
        return make_new_thread(body)
    elif "new_reply" in body:
        return make_new_reply(body)
    elif "store_token" in body:
        return store_token(body)
    elif "get_token" in (body):
        return get_token(body)
    elif "add_friend" in body:
        return add_friend(body)
    elif "get_friends" in body:
        return get_friends(body)
    elif "create_chat" in body:
        return create_chat(body)
    elif "get_username" in body:
        return get_username(body)
    elif "new_chat_message" in body:
        return new_chat_message(body)
    elif "get_messages" in body:
        return get_chat_messages(body)
    elif "store_stats" in body:
        return store_stats(body)
    elif "check_stats" in body:
        return check_stats(body)
    elif "compare_users" in body:
        return compareUsersDetailed(body)
    elif "get_recommendations" in body:
        return getUsersForListComparison(body)
    elif "remove_friend" in body:
        return remove_friend(body)
    elif "get_details_page" in body:
        return compareUsersDetailed(body)
    else:
        return check_session(body)

