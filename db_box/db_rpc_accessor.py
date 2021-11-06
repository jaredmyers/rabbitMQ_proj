import mysql.connector
import credentials as cred
import bcrypt, uuid, datetime


def accessor_methods(body,queue):

    conn = mysql.connector.connect(
    host=cred.db_host,
    user=cred.db_user,
    password=cred.db_pw,
    database=cred.db_database
    )

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

    def get_token(body):
        body = body.split(":")
        sessionId = body[1]

        query = f"select apitokens.apitoken from apitokens,sessions where sessions.sessionId = %s;"
        val = (sessionId,)
        cursor = conn.cursor()
        cursor.execute(query, val)
        query_result = cursor.fetchall()

        if not query_result:
            return ''

        access_token = query_result[0][0]

        return access_token



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
    else:
        return check_session(body)

    '''
    if queue == 'check_session':
        return check_session(body)
    if queue == 'delete_session':
        return delete_session(body)
    '''
