import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    #port='3306', # test this 
    user="testUser",
    password="12345",
    database="testdb"
    )

query = "select * from site_login;"

cursor = conn.cursor()
cursor.execute(query)

result = cursor.fetchall()

for row in result:
    print(row)

conn.close()
