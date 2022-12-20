from flask_mysqldb import MySQL
import datetime
from passlib.hash import sha256_crypt
import string
import random


class UserUtils:
    def __init__(self, app):
        self.first_name = None
        self.last_name = None
        self.gender = None
        self.email = None
        self.password = None
        self.user_usage = None
        self.phone_number = None
        self.date_of_birth = None
        self.joined_on = datetime.datetime.now()
        self.app = app
        self.app.config['MYSQL_HOST'] = 'localhost'
        self.app.config['MYSQL_USER'] = 'root'
        self.app.config['MYSQL_PASSWORD'] = ''
        self.app.config['MYSQL_DB'] = 'pp_mail'
        self.app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        self.user_id = None
        self.mysql = MySQL(app)

    def set_user_id(self, user_id):
        self.user_id = user_id

    def check_user_exists(self):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where email = %s", (self.email,))
        data = cursor.fetchall()
        cursor.close()
        result = {'user': data}
        if data == ():
            result['user_exists'] = False
            return result
        result['user_exists'] = True
        return result

    def login_user(self, email, password):
        self.email = email
        user = self.check_user_exists()
        user_details = {}
        for details in user['user']:
            user_details = details
        result = {'valid': False}
        if user_details.get('user_id') is not None:
            result['user_id'] = user_details.get('user_id')
            if sha256_crypt.verify(password, user_details.get('password')):
                cursor = self.mysql.connection.cursor()
                cursor.execute(
                    "UPDATE users SET active = true WHERE email=%s", (self.email,))
                self.mysql.connection.commit()
                cursor.close()
                result['valid'] = True
        return result

    def get_user_details(self, user_id):
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "SELECT first_name, last_name, gender, email, user_usage, phone_number, user_id, active, joined_on, profile_picture from users WHERE user_id=%s", (user_id,))
        data = cursor.fetchall()
        cursor.close()
        user_details = {}
        for user in data:
            user_details = user
        return user_details

    def logout_user(self, user_id):
        cursor = self.mysql.connection.cursor()
        cursor.execute("UPDATE users SET active=0 WHERE user_id=%s", (user_id,))
        self.mysql.connection.commit()
        cursor.close()
        return True

    def register_user(self, first_name, last_name, gender, date_of_birth, email, password, user_usage, phone_number):
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.email = email
        self.password = sha256_crypt.encrypt(password)
        self.phone_number = phone_number
        self.user_usage = user_usage
        self.user_id = "".join([random.choice(string.ascii_letters + string.digits) for n in range(30)])
        if not self.check_user_exists()['user_exists']:
            cursor = self.mysql.connection.cursor()
            cursor.execute("INSERT INTO users(user_id,first_name,last_name,gender,date_of_birth,email,password,phone_number,user_usage,joined_on) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (self.user_id, self.first_name, self.last_name, self.gender, self.date_of_birth, self.email,
                            self.password, self.phone_number, self.user_usage,
                            self.joined_on))
            self.mysql.connection.commit()
            cursor.close()
            return True
        return False
