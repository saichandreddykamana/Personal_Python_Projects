from flask import session
from flask_mysqldb import MySQL


class Trigger:
    def __init__(self):
        self.user_id = session.get('user_id')
        self.mysql = MySQL()

    def update_user_inbox_count(self):
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) as 'COUNT' FROM mails_info INNER JOIN pp_mails ON pp_mails.mail_info_id = mails_info.mail_info_id WHERE pp_mails.receiver_id = %s",
            (self.user_id,))
        data = cursor.fetchall()
        cursor.close()
        print("trigger data : ", data)
