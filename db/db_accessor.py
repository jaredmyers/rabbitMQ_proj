import mysql.connector
from testClass import RunSubscriber
from testClass import RunPublisher
import credentials as cred

exchange = 'db_exchange'
queue = 'db1'

def db_access(q):

    conn = mysql.connector.connect(
        host=cred.db_host,
        user=cred.db_user,
        password=cred.db_pw,
        database=cred.db_database
    )

    query = q.decode("utf-8")
    
    # console log for debug
    print(query) 

    cursor = conn.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except Exception:
        result = 'fetch error'
    
    if result == []:
        result = 'Not Found'
    
    conn.close()

    print(result)

    if result != 'fetch error' and result != 'Not Found':
        new_result = ''
        for row in result:
            for data in row:
                new_result += (" " + data)
    
        result = new_result
        result = str.encode(result)

    pub_conn = RunPublisher(cred.user, cred.pw, cred.ip_address)
    pub_conn.db_publish(exchange, 'db2', result)
  
sub_conn = RunSubscriber(cred.user, cred.pw, cred.ip_address)
sub_conn.db_subscribe_persist(exchange, queue, db_access)

