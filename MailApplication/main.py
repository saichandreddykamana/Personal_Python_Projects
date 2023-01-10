import datetime
import math
import re

from flask import Flask, render_template, request, flash, url_for, redirect, session

from UserUtils import UserUtils
from MailUtils import MailUtils

app = Flask(__name__)
app.secret_key = "mail_application"
user = UserUtils(app=app)
mail = MailUtils(user=user)
error = None
confirmation = None


@app.route("/")
def home():
    if session.get('user_id') is None:
        return render_template('home.html', user={})
    return redirect(url_for('dashboard'))


@app.route("/contact")
def contact():
    if session.get('user_id') is None:
        return render_template('contact.html', user={})
    return redirect(url_for('dashboard'))


@app.route("/dashboard", defaults={'page': 1, 'rows': 10})
@app.route("/dashboard/inbox/<int:page>/<int:rows>")
def dashboard(page, rows):
    start = rows * (page - 1)
    user_id = session.get('user_id')
    details = user.get_user_details(user_id=user_id)
    page_count = math.ceil(details['inbox_count']/rows) + 1
    prev_page = page
    if page != 1 and page != 0:
        prev_page = page - 1
    next_page = page + 1
    if next_page > page_count - 1:
        next_page = page_count - 1
    user_mails = user.get_user_mails(user_id=user_id, start=start, per_page=rows)
    if details.get('active'):
        return render_template('dashboard.html', user_id=user_id, user=details, confirmation=confirmation,
                               user_mails=user_mails, page_count=page_count, page=page, prev_page=prev_page, next_page=next_page)
    return redirect(url_for('home'))


@app.route("/send_mail", methods=['POST'])
def send_mail():
    sender_email = user.get_user_email()
    if request.method == 'POST':
        receiver_mail = request.form["receiver_mail"]
        mail_subject = request.form["mail_subject"]
        mail_content = request.form["mail_content"]
        response = mail.send_mail(receiver_mail=receiver_mail,
                                  mail_content=mail_content,
                                  mail_subject=mail_subject,
                                  sender_mail=sender_email,
                                  sender_id=session.get('user_id'))
        if response:
            global confirmation
            confirmation = True
            flash("Message sent successfully")
            return 200


@app.route("/login", methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['login-email']
        password = request.form['login-password']
        global confirmation
        user_details = user.login_user(email=email, password=password)
        confirmation = user_details.get('valid')
        if confirmation:
            session['user_id'] = user_details.get('user_id')
            return redirect(url_for('dashboard'))
        flash("Please check email and password.")
    return render_template('home.html', confirmation=False)


@app.route("/logout")
def logout():
    user_id = session.get('user_id')
    global confirmation
    confirmation = user.logout_user(user_id=user_id)
    if confirmation:
        session['user_id'] = None
        return redirect(url_for('home'))


@app.route("/change_password", methods=['POST'])
def change_password():
    user_id = session.get('user_id')
    if request.method == 'POST':
        new_password = request.form["authenticate-password"]
        user.set_user_id(user_id=user_id)
        result = user.change_user_password(password=new_password)
        global confirmation
        if result == 'Password changed Successfully.':
            confirmation = True
            flash(result)
            return redirect(url_for('dashboard'))


@app.route("/get_full_mail", methods=['POST'])
def get_full_mail():
    if request.method == 'POST':
        mail_id = request.form['mail_id']
        mail.set_mail_id(mail_id=mail_id)
        mail_details = mail.get_full_mail()
        return mail_details


@app.route("/register", methods=['POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['register-email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gender = request.form['gender']
        dob = request.form['birthday']
        date = datetime.datetime.strptime(dob, '%Y-%m-%d')
        year = date.year
        phone_number = request.form['phone-number']
        usage = request.form['usage']
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if all(x.isalpha() or x.isspace() for x in first_name) and all(x.isalpha() or x.isspace() for x in last_name) \
                and year <= 2015 and all(x.isdigit() for x in phone_number) and all(x.isalpha() for x in gender) \
                and re.fullmatch(regex, email) and password == confirm_password and (usage == '0' or usage == '1') \
                and len(password) >= 10:
            global confirmation, error
            confirmation = user.register_user(first_name=first_name, last_name=last_name, gender=gender, email=email,
                                              password=password, date_of_birth=dob, phone_number=phone_number,
                                              user_usage=usage)
            if confirmation:
                error = "Account Created Successfully. Please login into the account."
            else:
                error = " Please check the email or password. Or user exists."
        else:
            confirmation = False
            error = "Please enter valid data in inputs."
    flash(error)
    return render_template('home.html', confirmation=confirmation)


if __name__ == "__main__":
    app.run(debug=True)
