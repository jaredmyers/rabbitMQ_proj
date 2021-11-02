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
        
        return '1'

    def generate_sessionId(username):
        
        query = f"SELECT id FROM users WHERE uname = '{username}';"
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()
        userId = query_result[0][0]

        sessionId = uuid.uuid4().hex
        
        query = f"INSERT into sessions (userId, sessionId) values ('{userId}', '{sessionId}');"
        cursor= conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
            
        return sessionId
    
    def register_user(body):
        body = body.split(':')
        username = body[1]
        hashed_pw = body[2]

        query = f"SELECT id FROM users WHERE uname = '{username}';"
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
            query = f"SELECT id FROM users WHERE uname = '{username}';"
            cursor.execute(query)
            query_result = cursor.fetchall()
            userId = query_result[0][0]

            sessionId = uuid.uuid4().hex
        
            query = f"INSERT into sessions (userId, sessionId) values ('{userId}', '{sessionId}');"
            cursor.execute(query)
            conn.commit()
            conn.close()

            print("sessionId from accessor methods: " + sessionId)
            
            return sessionId
        
        return ''

    def get_threads():
        cursor = conn.cursor()
        query = f"SELECT id FROM users WHERE uname = '{username}';"
        cursor.execute(query)
        query_result = cursor.fetchall()
        
        if isinstance(qr[0][3], datetime.datetime):
            pass
        
        thread_info = []
        for i in query_result:
            for p in i:
                thread_info.append()



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
    else:
        return check_session(body)

    '''
    if queue == 'check_session':
        return check_session(body)
    if queue == 'delete_session':
        return delete_session(body)
    '''
