import mysql.connector
import credentials as cred
import bcrypt, uuid, datetime, random


def accessor_methods(body,queue):

    conn = mysql.connector.connect(
    host=cred.db_host,
    user=cred.db_user,
    password=cred.db_pw,
    database=cred.db_database
    )
    cursor = conn.cursor()

    def check_session(body):
        sessionId = body
        token_expiry = 0.50

        query = f"SELECT sessionId, sTime FROM sessions WHERE sessionId = '{sessionId}';"
        cursor = conn.cursor() 
        cursor.execute(query)
        query_result = cursor.fetchall()
        


        #if not query_result:
        #    return ''
        #else:
        #    return str(query_result[0][0])

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
        body = body.split(':')
        body = body[1]
        sessionId = body

        query = f"DELETE FROM sessions WHERE sessionId = '{sessionId}';"
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        
        
        return '1'

    def generate_sessionId(username):
        ''' internal method'''
        query = f"SELECT userID FROM users WHERE uname = '{username}';"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()
        userID = query_result[0][0]

        sessionId = uuid.uuid4().hex
        
        query = f"INSERT into sessions (userID, sessionId) values ('{userID}', '{sessionId}');"
        cursor= conn.cursor()
        cursor.execute(query)
        conn.commit()
        
            
        return sessionId
    
    def register_user(body):
        body = body.split(':')
        username = body[1]
        hashed_pw = body[2]

        query = f"SELECT userID FROM users WHERE uname = '{username}';"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()

        # if username doesn't exist
        if not query_result:
            query = f"insert into users (uname, pw) values ('{username}', '{hashed_pw}');"
            cursor.execute(query)
            conn.commit()
            
            
            return generate_sessionId(username)
        else:
            return ''

    def login(body):

        given_creds = body.split(":")
        username = given_creds[1]
        password = given_creds[2]

        query = f"SELECT uname, pw FROM users WHERE uname = '{username}';"

        # console log for debug
        print(query) 
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()
        
        if not query_result:
            return ''
        
        uname = query_result[0][0]
        hashed = query_result[0][1]

        cred_match = bcrypt.checkpw(password.encode(),hashed.encode())
        print("credmatch from accessor methods: ", cred_match)

        if cred_match:
            query = f"SELECT userID FROM users WHERE uname = '{username}';"
            cursor.execute(query)
            query_result = cursor.fetchall()
            userID = query_result[0][0]

            sessionId = uuid.uuid4().hex

            query = f"DELETE FROM sessions WHERE userID='{userID}';"
            cursor.execute(query)
            conn.commit()
        
            query = f"INSERT into sessions (userID, sessionId) values ('{userID}', '{sessionId}');"
            cursor.execute(query)
            conn.commit()

            print("sessionId from accessor methods: " + sessionId)
            
            return sessionId
        
        conn.close()
        return ''

    def get_threads():
        cursor = conn.cursor()
        query = f"select users.uname, threads.threadID, threads.title, threads.content, threads.ts from users,threads where users.userID=threads.userID order by ts desc;"
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
        body = body.split(":")
        threadID = body[1]

        cursor = conn.cursor()
        query = f"select users.uname, threads.threadID, threads.title, threads.content, threads.ts from users,threads where users.userID=threads.userID and threads.threadID='{threadID}';"
        cursor.execute(query)
        query_result = cursor.fetchall()

        thread_json_string = ''
        for i in query_result:
            thread_json_string += '{"author":"'+i[0]+'",'
            thread_json_string += '"threadID":"'+str(i[1])+'",'
            thread_json_string += '"title":"'+i[2]+'",'
            thread_json_string += '"content":"'+i[3]+'",'
            thread_json_string += '"date":"'+i[4].strftime('%Y-%m-%d')+'"}'
            thread_json_string += '+'

        query = f"select users.uname, replies.content, replies.replyts from users,replies where users.userID=replies.userID and replies.threadID='{threadID}' order by replies.replyts desc;"
        cursor.execute(query)
        query_result = cursor.fetchall()

        replies_json_string = ''
        for i in query_result:
            replies_json_string += '{"author":"'+i[0]+'",'
            replies_json_string += '"content":"'+i[1]+'",'
            replies_json_string += '"date":"'+i[2].strftime('%Y-%m-%d')+'"}'
            replies_json_string += ';'

        return (thread_json_string + replies_json_string)

    def make_new_thread(body):
        body = body.split(':')
        sessionId = body[1]
        threadname = body[2]
        threadcontent = body[3]

        query = f"select userID from sessions where sessionId='{sessionId}';"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()
        
        if not query_result:
            return ''
        userID = query_result[0][0]
        
        query = f"insert into threads (userID, title, content) values ('{userID}','{threadname}','{threadcontent}');"
        cursor.execute(query)
        conn.commit()

        return '1'

    def make_new_reply(body):
        body = body.split(':')
        sessionId = body[1]
        threadID = body[2]
        replycontent = body[3]

        query = f"select userID from sessions where sessionId='{sessionId}';"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()

        if not query_result:
            return ''
        userID = query_result[0][0]

        query = "insert into replies (threadID, userID, content) values (%s,%s,%s);"
        val = (threadID,userID, replycontent)
        cursor.execute(query, val)
        conn.commit()

        return '1'

    def store_token(body):
        body = body.split(":")
        sessionId = body[1]
        api_token = body[2]

        query = f"select userID from sessions where sessionId='{sessionId}';"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()

        if not query_result:
            return ''

        userID = query_result[0][0]

        query = "insert into apitokens (apitoken, userID) values (%s, %s);"
        val = (api_token, userID)
        cursor.execute(query, val)
        conn.commit()

        return '1'

    def delete_token(body):
        ''' internal method'''
        body = body.split(":")
        sessionId = body[1]

        query = "delete apitokens from apitokens inner join sessions on sessions.userID=apitokens.userID where sessions.sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        conn.commit()

    def get_token(body):
        body = body.split(":")
        sessionId = body[1]
        api_expiry = 0.9

        query = f"select apitokens.apitoken, apitokens.tTime from apitokens,sessions where sessions.sessionId = %s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

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
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        #returns false if potential friend doesn't exist
        if not query_result:
            return ''
        
        userID2 = query_result[0][0]

        # check if they are already friends
        query = "select * from friends where userID1=%s and userID2=%s or userID1=%s and userID2=%s;"
        val = (userID1,userID2,userID2,userID1)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        # returns false if already friends
        if query_result:
            return ''

        ## add friend
        query = "insert into friends (userID1, userID2) values (%s, %s);"
        val = (userID1, userID2)
        cursor = conn.cursor()
        cursor.execute(query, val)
        conn.commit()

        return '1'

    def get_friends(body):
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
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

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
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()

        # grabbing all the users names of all the users friends
        friend_names = ''
        for i in query_result:
            if i[0] in userID_list:
                friend_names += i[1] + ":" # these are uname strings from db

        return friend_names

    def create_chat(body):
        body = body.split(":")
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
        if not query_result[0][0]:
            roomID = f"{uname1}_{chat_recipient}"
            query = f"create table if not exists {roomID} (uname VARCHAR(255), message TEXT);"
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
        body = body.split(":")
        sessionId = body[1]

        query = "select users.uname from users inner join sessions on sessions.userID=users.userID where sessionId=%s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        username = cursor.fetchall()[0][0]

        return username

    def new_chat_message(body):
        body = body.split(":")
        username = body[1] 
        chat_message = body[2]
        room_id = body[3]

        query = f"insert into {room_id} (uname, message) values (%s, %s);"
        val = (username, chat_message)
        cursor.execute(query, val)
        conn.commit()

        return '1'

    def get_chat_messages(body):
        body = body.split(":")
        room_id = body[1]

        query = f"select * from {room_id}"
        cursor.execute(query)
        query_result = cursor.fetchall()

        chat_records = ''
        for i in query_result:
            chat_records += i[0] + ":" + i[1] + ";"


        '''
        p = 0
        chat_records = {"messages":[]}
        for i in query_result:
            chat_records["messages"].append({"chat_num":str(p), "username":i[0], "message":i[1]})
            p += 1
        
        p = 0
        storage = '{'
        for i in query_result:
            storage += '"chat_num":"'+'"'+str(p)+'"'+'"'+i[0]+'":"'+i[1]+'",'
            p+=1
        storage += '}'

        chat_records = storage.replace(',}','}')
        '''
        return chat_records

        




## Main entry point

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
    else:
        return check_session(body)

    '''
    if queue == 'check_session':
        return check_session(body)
    if queue == 'delete_session':
        return delete_session(body)
    '''
