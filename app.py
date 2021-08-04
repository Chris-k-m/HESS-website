import re
import os
import MySQLdb
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required
import mysql
from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import stripe
import requests
from werkzeug.utils import secure_filename

stripe.api_key = ['secret_key']

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'
mysql = MySQL()

login_manager = LoginManager(app)
login_manager.login_view = "/charges"
"""
LoginManager comes with
is_authenticated
is_active
is_anonymous
get_id()
"""


@login_manager.user_loader
def load_user(subscriber_Id):
    return User.query.get(int(subscriber_Id))


# Enter your database connection details below
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'hess'
app.config['MYSQL_CURSOR_CLASS'] = 'DictCursor'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/hess'
app.config['SQLALCHEMY TRACK MODIFICATIONS'] = False

mysql.init_app(app)
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    subscriber = db.Column(db.Boolean)


# courses_paid = db.relationship('Courses', backref='author', lazy='dynamic')

courses_paid = db.relationship(
    'Course',
    foreign_keys='Courses.paid_by_id',
    backref='subscriber',
    lazy=True
)


def __repr__(self):
    return self.name


class Subscriber_details(db.Model):
    subscriber_Id = db.Column(db.Integer, primary_key=True, )
    change_email = db.Column(db.String(100), index=True, nullable=True)
    change_name = db.Column(db.String(100), index=True, nullable=True)


class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_title = db.Column(db.String(100), index=True, nullable=True)
    course_description = db.Column(db.String(100), index=True, nullable=True)
    course_price = db.Column(db.String(100), index=True, nullable=True)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'passwords' in request.form:
        # Create variables for easy access
        session['email'] = request.form['email']
        session['password'] = request.form['passwords']
        # check if data is in db
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM password WHERE passwords =MD5(%s) ', (session['password'],))
        cursor.execute('SELECT * FROM admin WHERE email = %s ', (session['email'],))
        # Fetch one record and return result
        admin = cursor.fetchone()
        # if account exists
        if admin:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['admin_Id'] = admin['admin_Id']
            session['firstname'] = admin['firstname']
            session['lastname'] = admin['lastname']
            session['publication_Id'] = admin['publication_Id']
            session['course_Id'] = admin['course_Id']
            session['subscriber_Id'] = admin['subscriber_Id']
            session['image_Id'] = admin['image_Id']
            return render_template('index.html')

        else:
            # employee doesnt exist or username/password incorrect
            msg = 'Incorrect email/password!'
            # Show the login form with message (if any)
            return render_template('login.html', msg=msg)
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Output message if something goes wrong...
    msg = ''
    # validate the received values
    if request.method == 'POST' and "firstname" in request.form and "lastname" in request.form and "password" in request.form and "password2" in request.form and "email" in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        password2 = request.form['password2']
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE firstname = %s', (firstname,))
        admin = cursor.fetchone()
        # If account exists show error and validation checks
        if admin:
            'admin already exists!'
            return render_template('signup.html')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return render_template("signup.html", msg="email has a match")
        elif not re.match(r'[A-Za-z0-9]+', firstname):
            return render_template("signup.html", msg="only use letters and No's")
        if password != password2:
            return render_template("signup.html", msg="password don't match")
        elif not firstname or not password or not email:
            msg = 'Please refill out the form!'
            return render_template("adminhome.html", msg=msg)

        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Account doesnt exists and the form data is valid, now insert new account into admin table
            cursor.execute('INSERT INTO admin VALUES (NULL, %s, %s, %s, NULL, NULL, NULL, NULL, NULL)',
                           (firstname, lastname, email))
            cursor.execute('INSERT INTO password VALUES( NULL, MD5(%s),NULL)', (password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
        return render_template('login.html', msg='You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        # Show registration form with message (if any)
    return render_template('signup.html', msg=msg)


def subscribe_user(email, user_group_email, api_key):
    resp = requests.post(f"https://api.mailgun.net/v3/lists/{user_group_email}/members",
                         auth=("api", api_key),
                         data={"subscribed": True,
                               "address": email}
                         )
    return resp


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form['email']

        subscribe_user(email=email,
                       user_group_email="chrispaskamau@sandboxf973537988bc40e9adccd3d44a679152.mailgun.org",
                       api_key="pubkey-d8ba0af9433525830393d27ffd5a6f32")
        msg = "successfully subscribed"
        return render_template("index.html", msg=msg)
    return render_template("subscribe.html")


@app.route('/charges', methods=['GET', 'POST'])
def charges():
    # Output message if something goes wrong...
    msg = ''
    # validate the received values
    if request.method == 'POST' and "sname" in request.form and "semail" in request.form:
        name = request.form['sname']
        email = request.form['semail']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM subscribers WHERE Email = %s', (email,))
        subscriber = cursor.fetchone()
        # If account exists show error and validation checks
        if subscriber:
            msg = 'subscriber already exists!'
            return render_template('charges.html', msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return render_template("charges.html", msg="email has a match")
        elif not re.match(r'[A-Za-z0-9]+', name):
            return render_template("charges.html", msg="only use letters and No's")
        elif not name or not email:
            msg = 'Please refill out the form!'
            return render_template("charges.html", msg=msg)

        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Account doesnt exists and the form data is valid, now insert new account into subscriber table
            cursor.execute('INSERT INTO subscribers VALUES (NULL, %s, %s,NULL)',
                           (name, email))
            mysql.connection.commit()
            msg = 'You have successfully subscribed, you may now view your course!'
        return render_template('courses.html', msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        # Show registration form with message (if any)
    return render_template('charges.html', msg=msg)


@app.route('/subscriber_details', methods=['GET', 'POST'])
@login_required
def edit_profile():
    return render_template("subscriber_details.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/workshop')
def workshop():
    return render_template("workshop.html")


@app.route('/gallery')
def gallery():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * FROM gallery")
    images = cursor.fetchall()  # data from database
    return render_template("gallery.html", images=images)


IMAGE_UPLOADS = 'static/images/uploads'
app.config['IMAGE_UPLOADS'] = IMAGE_UPLOADS
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ['PNG', 'JPG', 'JPEG', 'GIF']


def allowed_images(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


@app.route("/uploadimage", methods=["GET", "POST"])
def uploadimage():
    if request.method == "POST" and "image_Id" in request.form and "image_title" in request.form and "image_description" in request.form and "created" in request.form and request.files:
        image_Id = request.form['image_Id']
        image_title = request.form['image_title']
        image_description = request.form['image_description']
        created = request.form['created']

        image = request.files["image"]

        if image.filename != "":
            if not allowed_images(image.filename):
                print("that image extension is not allowed")
                return redirect(request.url)

            else:
                filename = secure_filename(image.filename)
                newimage= image(name=image.filename, data=image.read())

                image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                # Account doesnt exists and the form data is valid, now insert new account into admin table
                cursor.execute('INSERT INTO gallery VALUES (%s, %s, %s, %s, %s)',
                               (image_Id, image_title, image_description, created, newimage))
            print('image saved')
            return render_template("gallery.html")

        print("Image must have a name")
        return redirect(requests.url)

    return render_template("uploadimage.html")


@app.route('/events')
def events():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * FROM events")
    events = cursor.fetchall()  # data from database
    return render_template("events.html", events=events)


@app.route('/addevent', methods=['GET', 'POST'])
def addevent():
    # Output message if something goes wrong...
    msg = ''
    # validate the received values
    if request.method == 'POST' and "event_Id" in request.form and "event_title" in request.form and "event_description" in request.form and "event_price" in request.form and "created" in request.form:
        event_Id = request.form['event_Id']
        event_title = request.form['event_title']
        event_description = request.form['event_description']
        event_price = request.form['event_price']
        created = request.form['created']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM events WHERE event_Id = %s', (event_Id,))
        event = cursor.fetchone()
        if event:
            msg = 'event exists'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # event doesnt exists and the form data is valid, now insert new event into event table
            cursor.execute('INSERT INTO events VALUES (%s, %s, %s, %s, %s)',
                           (event_Id, event_title, event_description, event_price, created))
            mysql.connection.commit()
            msg = 'You have successfully added event!'
        return render_template('events.html', events=events, msg=msg)
    return render_template("addevent.html")


@app.route('/publications')
def publications():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * FROM publications")
    publication = cursor.fetchall()  # data from database
    return render_template("publications.html", publication=publication)


@app.route('/updatepublication', methods=('GET', 'POST'))
def updatepublication():
    if request.method == 'POST' and "publication_Id" in request.form and "title" in request.form and "description" in request.form and "created" in request.form and "content" in request.form:
        new_publication_Id = request.form['publication_Id']
        new_title = request.form['title']
        new_description = request.form['description']
        new_content = request.form['content']
        new_created = request.form['created']
        # connect to mysql database
        if 'loggedin' in session:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT publication_Id FROM admin WHERE admin_Id= %s', (session['admin_Id'],))
            publication_Id = cursor.fetchone()
            print(publication_Id)
            print(new_publication_Id)
            if publication_Id != new_publication_Id:
                cursor.execute('UPDATE publications SET title = %s, description = %s, content = %s, created = %s '
                               'WHERE publication_Id = %s',
                               (new_title, new_description, new_content, new_created, (session['publication_Id'],)))
                mysql.connection.commit()
                msg = 'You have successfully updated !'
                return render_template("publications.html", publications=publications, msg=msg)
            else:
                msg = 'use the correct ID'
            return render_template("updatepublication.html", msg=msg)
    else:
        msg = 'input data!'
        return render_template("updatepublication.html", msg=msg)

    # validate if user has input data
    # if request.method == 'POST' and "publication_Id" in request.form and "title" in request.form and "description" in request.form and "created" in request.form and "content" in request.form:
    #     new_publication_Id = request.form['publication_Id']
    #     new_title = request.form['title']
    #     new_description = request.form['description']
    #     new_content = request.form['content']
    #     new_created = request.form['created']
    #
    #
    #     # connect to mysql database
    #     if 'loggedin' in session:
    #         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #         cursor.execute('SELECT publication_Id FROM admin WHERE admin_Id= %s', (session['admin_Id'],))
    #         publication_Id = cursor.fetchone()
    #         print(publication_Id)
    #         print(new_publication_Id)
    #
    #         if publication_Id == new_publication_Id:
    #             msg = 'use the correct ID'
    #             return render_template("updatepublication.html", msg=msg)
    #         else:
    #             cursor.execute('UPDATE publications SET title = %s, description = %s, content = %s, created = %s '
    #                            'WHERE publication_Id = %s',
    #                            (new_title, new_description, new_content, new_created, (session['publication_Id'],)))
    #             mysql.connection.commit()
    #             msg = 'You have successfully updated !'
    #             return render_template("publications.html", publications=publications, msg=msg)
    # else:
    #     return render_template("updatepublication.html")
    #


@app.route('/deletepublications')
def deletepublication():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM publication WHERE publication_Id = ?', (session['publication_Id'],))
    mysql.connection.commit()
    return render_template("publications.html")


@app.route('/addpublications', methods=('GET', 'POST'))
def addpublications():
    # Output message if something goes wrong...
    msg = ''
    # validate the received values
    if request.method == 'POST' and "publication_Id" in request.form and "title" in request.form and "description" in request.form and "created" in request.form and "content" in request.form:
        publication_Id = request.form['publication_Id']
        title = request.form['title']
        description = request.form['description']
        created = request.form['created']
        content = request.form['content']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM publications WHERE publication_Id = %s', (publication_Id,))
        event = cursor.fetchone()
        if event:
            msg = 'publication exists'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # event doesnt exists and the form data is valid, now insert new event into event table
            cursor.execute('INSERT INTO publications VALUES (%s, %s, %s, %s, %s)',
                           (publication_Id, title, description, content, created))
            mysql.connection.commit()
            msg = 'You have successfully added publication!'
        return render_template('publications.html', publications=publications, msg=msg)
    return render_template("addpublications.html")


@app.route('/courses')
def courses():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * FROM courses")
    courses = cursor.fetchall()  # data from database
    return render_template("courses.html", courses=courses)


@app.route('/deletecourse')
def deletecourse():
    return render_template("courses.html")


@app.route('/updatecourse')
def updatecourse():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT course_Id FROM admin WHERE admin_Id = %s', (session['admin_Id'],))
        cursor.execute('SELECT document_Id FROM admin WHERE admin_Id = %s', (session['admin_Id'],))
        course = cursor.fetchone()
        documents = cursor.fetchone()
        if course and documents and request.form == 'POST' and 'new_ctitle' in request.form and 'new_cdescription' in request.form and 'new_cprice' in request.form and 'new_ccontent' in request.form:
            new_ctitle = request.form['new_ctitle']
            new_cdescription = request.form['new_cdescription']
            new_cprice = request.form['new_cprice']
            new_ccontent = request.form['new_content']
            cursor.execute('UPDATE courses SET course_title = %s, course_description = %s WHERE course_Id = %s',
                           (new_ctitle, new_cdescription, new_cprice, (session['course_Id'],)))
            cursor.execute('UPDATE document SET course_content = %s = %s WHERE course_Id = %s',
                           (new_ccontent, (session['course_Id'],)))
            mysql.connection.commit()
            msg = 'You have successfully updated now add content !'
    return render_template("updatecourse.html")


@app.route('/addcourse', methods=('GET', 'POST'))
def addcourse():
    # Output message if something goes wrong...
    msg = ''
    # validate the received values
    if request.method == 'POST' and "course_Id" in request.form and "course_title" in request.form and "course_description" in request.form and "course_price" in request.form and "course_content" in request.form:
        course_Id = request.form['course_Id']
        course_title = request.form['course_title']
        course_description = request.form['course_description']
        course_price = request.form['course_price']
        course_content = request.form['course_content']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM courses WHERE course_Id = %s', (course_Id,))
        course = cursor.fetchone()
        if course:
            msg = 'course exists'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # course doesnt exists and the form data is valid, now insert new course into course table
            cursor.execute('INSERT INTO courses VALUES (%s, %s, %s, %s, %s)',
                           (course_Id, course_title, course_description, course_price, course_content))
            mysql.connection.commit()
            msg = 'You have successfully added publication!'
        return render_template('courses.html', courses=courses, msg=msg)
    return render_template("addcourse.html")


@app.route('/logout')
def logout():
    # check if user is logged in:
    if 'loggedin' in session:
        # Remove session data, this will log the user out
        session.pop('loggedin', None)
        session.pop('admin_Id', None)
        session.pop('firstname', None)
        session.clear()
        # Redirect to login page
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return "page not found", 404


@app.errorhandler(500)
def internal_error(e):
    return "internal error", 500


if __name__ == "__main__":
    app.run(debug=True)
