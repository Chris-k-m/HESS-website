import mysql

db = mysql.connector.connect(host="localhost",
                             user="root",
                             password="root",
                             database="hess"
                             )
cursor = db.cursor()

# cursor.execute("DROP TABLE document")
# cursor.execute("DROP TABLE courses")
# cursor.execute("DROP TABLE subscribers")
# cursor.execute("DROP TABLE publication")

# cursor.execute("CREATE TABLE admin( admin_Id INT(20) AUTO_INCREMENT PRIMARY KEY, firstname CHAR(50), lastname CHAR(50), email VARCHAR(50))")


# cursor.execute("CREATE TABLE document( document_Id INT(20) AUTO_INCREMENT PRIMARY KEY, course_content varchar(10000))")
# cursor.execute("CREATE TABLE courses( course_Id INT(20) AUTO_INCREMENT PRIMARY KEY, course_title varchar(200), course_description varchar(500), course_price VARCHAR(50))")
# cursor.execute("CREATE TABLE subscribers( subscriber_Id INT(20) AUTO_INCREMENT PRIMARY KEY, name char(45), Email varchar(45))")
# cursor.execute("CREATE TABLE password( password_Id INT(20) AUTO_INCREMENT PRIMARY KEY, password varchar(200))")
# cursor.execute("CREATE TABLE publications( publication_Id INT(20) AUTO_INCREMENT PRIMARY KEY, title varchar(200), description varchar(500), content varchar(3000), created datetime(6))")
# cursor.execute("CREATE TABLE gallery( image_Id INT(20) AUTO_INCREMENT PRIMARY KEY, image_title varchar(200), image_description varchar(500),created datetime(6))", image LONGBLOB)
# cursor.execute("CREATE TABLE events( event_Id INT(20) AUTO_INCREMENT PRIMARY KEY, event_title varchar(200), event_description varchar(500), event_price VARCHAR(50))")

# cursor.execute('ALTER TABLE admin ADD ( publication_Id INT(20), FOREIGN KEY (publication_Id) REFERENCES publications (publication_Id),course_Id INT(20), FOREIGN KEY (course_Id) REFERENCES courses (course_Id),subscriber_Id INT(20), FOREIGN KEY (subscriber_Id) REFERENCES subscribers (subscriber_Id),document_Id INT(20), FOREIGN KEY (document_Id) REFERENCES document (document_Id))')
# cursor.execute('ALTER TABLE subscribers ADD ( document_Id INT(20), FOREIGN KEY (document_Id) REFERENCES document (document_Id))')
# cursor.execute('ALTER TABLE password ADD ( admin_Id INT(20), FOREIGN KEY (admin_Id) REFERENCES admin (admin_Id))')
# cursor.execute('ALTER TABLE admin ADD ( image_Id INT(20), FOREIGN KEY (image_Id) REFERENCES gallery (image_Id))')
# cursor.execute('ALTER TABLE gallery ADD ( filename varchar(220))')
# cursor.execute('ALTER TABLE admin ADD ( event_Id INT(20), FOREIGN KEY (event_Id) REFERENCES events (event_Id))')
# cursor.execute('ALTER TABLE admin ADD ( document_Id INT(20), FOREIGN KEY (document_Id) REFERENCES document (document_Id))')
# cursor.execute('ALTER TABLE document ADD (course_Id INT(20), FOREIGN KEY (course_Id) REFERENCES courses (course_Id))')
# cursor.execute('ALTER TABLE courses ADD ( course_content varchar(10000))')
cursor.execute('ALTER TABLE events ADD ( created datetime(6))')




