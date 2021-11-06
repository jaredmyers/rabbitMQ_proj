import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user="testUser",
    password="12345",
    database="testdb"
    )

query = "SELECT account_name, pw FROM site_login WHERE account_name = 'stoopkid';"
#query = "SELECT * FROM site_login"
cursor = conn.cursor()
cursor.execute(query)

result = cursor.fetchall()

for row in result:
    print(row)

conn.close()
