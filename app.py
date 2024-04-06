from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required,logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from wtforms.validators import Email
from datetime import datetime
import plotly.graph_objs as go

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
        new_status = request.form.get('bug_status')
        bug.bug_status = new_status
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/close_bug/<int:bug_id>', methods=['POST'])
@login_required
def close_bug(bug_id):
    bug = Bug.query.get(bug_id)
    if bug:
        db.session.delete(bug)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/bug_graphs')
def bug_graphs():
    # Query database to get counts of bugs based on flair
    flair_counts = db.session.query(Bug.bug_flair, db.func.count()).group_by(Bug.bug_flair).all()

    # Extract flair names and counts for plotting
    flair_names = [flair[0] for flair in flair_counts]
    flair_values = [flair[1] for flair in flair_counts]

    # Create a bar chart
    data = [go.Bar(x=flair_names, y=flair_values)]

    # Configure layout
    layout = go.Layout(title='Bug Flair Distribution', xaxis=dict(title='Flair'), yaxis=dict(title='Count'))

    # Create a figure
    fig = go.Figure(data=data, layout=layout)

    # Convert the figure to HTML
    graph_html = fig.to_html(full_html=False)

    return render_template('bug_graphs.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)
