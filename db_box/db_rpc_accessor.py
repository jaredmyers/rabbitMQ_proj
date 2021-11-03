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

        query = f"SELECT sessionId FROM sessions WHERE sessionId = '{sessionId}';"
        cursor = conn.cursor() 
        cursor.execute(query)
        query_result = cursor.fetchall()
        conn.close()

        if query_result == []:
            return str(0)
        else:
            return str(query_result[0][0])

    def delete_session(body):
        body = body.split(':')
        body = body[1]
        sessionId = body

        query = f"DELETE FROM sessions WHERE sessionId = '{sessionId}';"
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        
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
        conn.close()
            
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
            conn.close()
            
            return generate_sessionId(username)
        else:
            conn.close()
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
            conn.close()
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
        
            query = f"INSERT into sessions (userID, sessionId) values ('{userID}', '{sessionId}');"
            cursor.execute(query)
            conn.commit()
            conn.close()

            print("sessionId from accessor methods: " + sessionId)
            
            return sessionId
        
        conn.close()
        return ''

    def get_threads():
        cursor = conn.cursor()
        query = f"select users.uname, threads.threadID, threads.title, threads.content, threads.ts from users,threads where users.userID=threads.userID order by ts desc;"
        cursor.execute(query)
        query_result = cursor.fetchall()
        conn.close()

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

        query = f"select users.uname, replies.content, replies.replyts from users,replies where users.userID=replies.userID and replies.threadID='{threadID}';"
        cursor.execute(query)
        query_result = cursor.fetchall()

        replies_json_string = ''
        for i in query_result:
            replies_json_string += '{"author":"'+i[0]+'",'
            replies_json_string += '"content":"'+i[1]+'",'
            replies_json_string += '"date":"'+i[2].strftime('%Y-%m-%d')+'"}'
            replies_json_string += ';'

        conn.close()
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
        conn.close()

        return '1'

        '''
        with sesssion id, get userID..  the add to thread table values(userID, title, content)

        return bool for success or fail
        
        
        '''

    def make_new_reply(body):
        pass

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
    else:
        return check_session(body)

    '''
    if queue == 'check_session':
        return check_session(body)
    if queue == 'delete_session':
        return delete_session(body)
    '''
