import mysql.connector
from testClass import RunSubscriber
from testClass import RunPublisher
import credentials as cred
from logPublisher import sendLog
import uuid

exchange = 'db_exchange'
queue = 'db1'


def db_access(given_creds):

    try:

        conn = mysql.connector.connect(
            host=cred.db_host,
            user=cred.db_user,
            password=cred.db_pw,
            database=cred.db_database
        )
            

        given_creds = given_creds.decode("utf-8")
        given_creds = given_creds.split(":")
        username = given_creds[0]
        password = given_creds[1]

        query = f"SELECT uname, pw FROM users WHERE uname = '{username}';"

        # console log for debug
        print(query) 

        cursor = conn.cursor()
            
        cursor.execute(query)
        query_result = cursor.fetchall()
        
            
        if query_result == []:
            print('Not Found')
            result_was_returned = 0
        else:
            result_was_returned = 1
            
        if result_was_returned:
            query_answer = []
            for row in query_result:
                for data in row:
                    query_answer.append(data)
                    
            print(query_answer)

            if query_answer == given_creds:
                cred_match = 1
            else:
                cred_match = 0
        else:
            cred_match = 0
        
        if cred_match:
            query = f"SELECT id FROM users WHERE uname = '{username}';"
            cursor = conn.cursor()
            cursor.execute(query)
            query_result = cursor.fetchall()
            userId = query_result[0][0]

            sessionId = uuid.uuid1()
            sessionId = str(sessionId)

            query = f"INSERT into sessions (userId, sessionId) values ('{userId}', '{sessionId}');"
            cursor= conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            
            cred_match = sessionId


        cred_match = str.encode(str(cred_match))
        pub_conn = RunPublisher(cred.user, cred.pw, cred.ip_address)
        pub_conn.db_publish(exchange, 'db2', cred_match)

    except Exception as e:
        print(e)
        sendLog(str(e))
  
sub_conn = RunSubscriber(cred.user, cred.pw, cred.ip_address)
sub_conn.db_subscribe_persist(exchange, queue, db_access)

