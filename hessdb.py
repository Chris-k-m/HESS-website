import mysql

db = mysql.connector.connect(host="localhost",
                             user="root",
                             password="root",
                             database="hess"
                             )
cursor = db.cursor()

admin = "SELECT * FROM admin"
cursor.execute(admin)

print(admin)







