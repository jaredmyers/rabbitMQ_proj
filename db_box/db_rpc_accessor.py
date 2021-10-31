import mysql.connector
import credentials as cred


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
        sessionId = body

        query = f"DELETE FROM sessions WHERE sessionId = '{sessionId}';"
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        
        return '1'


## Main entry point

    print(f"from db accessor methods: {body}")
    body = body.decode('utf-8')

    if "delete" in body:
        body = body.split(':')
        body = body[1]
        return delete_session(body)
    else:
        return check_session(body)

    '''
    if queue == 'check_session':
        return check_session(body)
    if queue == 'delete_session':
        return delete_session(body)
    '''
