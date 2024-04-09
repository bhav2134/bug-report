from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required,logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from flask_bcrypt import Bcrypt
from wtforms.validators import Email
from datetime import datetime
import plotly.graph_objs as go
from flask_mail import Mail, Message
import os
from sqlalchemy import distinct
import pandas as pd
from collections import Counter

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Bug(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    bug_description = db.Column(db.String(800), nullable=False)
    bug_flair = db.Column(db.String(20), nullable=True)
    bug_status = db.Column(db.String(20), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'bugdatabase@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('mail_password')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail=Mail(app)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    email = StringField(validators=[InputRequired(), Email(), Length(min=4, max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Regsiter")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("username already exists, Please choose a different username")
    
    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError("email already exists, Please choose a different email one or log in")
        
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if not existing_user_username:
            raise ValidationError("username not found")

    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        if user and not bcrypt.check_password_hash(user.password, password.data):
            raise ValidationError("Incorrect password, try again")

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[InputRequired(), Length(min=4, max=20)])
    new_password = PasswordField('New Password', validators=[InputRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField('Confirm New Password', validators=[InputRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    bug_reports = Bug.query.all()
    return render_template('dashboard.html', bug_reports=bug_reports)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form=RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/submit_bug', methods=['GET'])
@login_required
def submit_bug_page():
    return render_template('submit_bug.html')


@app.route('/submit_bug', methods=['POST'])
@login_required
def submit_bug():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        bug_description = request.form['bug_description']
        bug_flair = request.form['bug_flair']

        # Create a new Bug instance and add it to the database
        new_bug = Bug(username=username, email=email, bug_description=bug_description, 
                      bug_flair=bug_flair, bug_status="Open")
        db.session.add(new_bug)
        db.session.commit()

        return redirect(url_for('submit_bug'))


@app.route('/update_bug_status/<int:bug_id>', methods=['POST'])
@login_required
def update_bug_status(bug_id):
    bug = Bug.query.get(bug_id)
    if bug:
        bug_reporter_emails = db.session.query(distinct(Bug.email)).all()
        new_status = request.form.get('bug_status')
        bug.bug_status = new_status
        db.session.commit()
        for email in bug_reporter_emails:
            msg = Message("This is a notification from your bug database app", sender='bugdatabase@gmail.com', recipients=[email[0]])
            msg.body = f"Bug {bug_id} status has been updated to {new_status}"
            mail.send(msg)
    return redirect(url_for('dashboard'))

@app.route('/close_bug/<int:bug_id>', methods=['POST'])
@login_required
def close_bug(bug_id):
    bug = Bug.query.get(bug_id)
    if bug:
        bug_reporter_emails = db.session.query(distinct(Bug.email)).all()
        for email in bug_reporter_emails:
            msg = Message("This is a notification from your bug database app", sender='bugdatabase@gmail.com', recipients=[email[0]])    
            msg.body = f"Bug {bug_id} status has been closed"
            mail.send(msg)
        db.session.delete(bug)
        db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/bug_graphs')
def bug_graphs():
    bug_reports = Bug.query.all()
    bug_flairs = [bug.bug_flair for bug in bug_reports]
    flair_counts = Counter(bug_flairs)
    labels = list(flair_counts.keys())
    values = list(flair_counts.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    graph_html = fig.to_html(full_html=False)

    return render_template('bug_graphs.html', graph_html=graph_html)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user
        if bcrypt.check_password_hash(user.password, form.old_password.data):
            new_password_hashed = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            user.password = new_password_hashed
            db.session.commit()
            flash('Your password has been updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid old password. Please try again.', 'danger')
    return render_template('change_password.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
