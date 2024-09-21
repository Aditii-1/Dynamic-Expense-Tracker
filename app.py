from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import os
from datetime import datetime
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# App configurations
app.secret_key = "bap026a029a301n539v"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Login manager setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User model
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    db_path = db.Column(db.String(200), nullable=False)
    data = db.relationship('Data', backref='user', lazy=True)

    def __init__(self, email, username, password, db_path):
        self.email = email
        self.username = username
        self.password = password
        self.db_path = db_path


# Data model
class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    pay_mode = db.Column(db.String(50), nullable=False)
    tran_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, description, amount, date, category, pay_mode, tran_type, user_id):
        self.description = description
        self.amount = amount
        self.date = date
        self.category = category
        self.pay_mode = pay_mode
        self.tran_type = tran_type
        self.user_id = user_id


# Function to switch databases based on the user's db_path
def switch_db(db_path):
    new_uri = f'sqlite:///{db_path}'
    if app.config['SQLALCHEMY_DATABASE_URI'] != new_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = new_uri
        db.engine.dispose()
        db.session.configure(bind=create_engine(new_uri))


# Function to create all tables
def create_tables():
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Error creating tables: {e}")


# Route to home page
@app.route('/')
def home():
    return render_template("home.html", user=current_user)


# Login route
@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email_var = request.form.get("email")
        pas1 = request.form.get("password1")
        user = User.query.filter_by(email=email_var).first()
        if user:
            if check_password_hash(user.password, pas1):
                flash("Logged in successfully.", category='success')
                login_user(user, remember=True)
                switch_db(user.db_path)
                return redirect(url_for('Index'))
            else:
                flash("Incorrect password, try again.", category='error')
        else:
            flash("Email does not exist.", category='error')

    return render_template("login.html", user=current_user)


# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# Signup route
@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email_var = request.form.get("email")
        fname = request.form.get("firstName")
        pas1 = request.form.get("password1")
        pas2 = request.form.get("password2")

        user = User.query.filter_by(email=email_var).first()
        if user:
            flash("Email already exists.", category='error')
        elif len(email_var) < 4:
            flash("Email must be greater than 4 characters", category="error")
        elif len(fname) < 2:
            flash("First Name must be greater than 2 characters", category="error")
        elif pas1 != pas2:
            flash("Passwords don't match", category="error")
        elif len(pas1) < 7:
            flash("Password must be at least 7 characters", category="error")
        else:
            db_path = os.path.join(basedir, f'{email_var}.sqlite3')
            new_user = User(email=email_var, username=fname, password=generate_password_hash(pas1), db_path=db_path)
            db.session.add(new_user)
            db.session.commit()
            flash("Account Created!", category="success")
            init_user_db(db_path)
            return redirect(url_for("login"))

    return render_template("signup.html", user=current_user)


# Initialize new user's database
def init_user_db(db_path):
    engine = create_engine(f'sqlite:///{db_path}')
    with engine.connect() as connection:
        Data.metadata.create_all(connection)


# Insert new expense
@app.route('/insert', methods=['POST'])
@login_required
def insert():
    switch_db(current_user.db_path)
    if request.method == 'POST':
        description = request.form['description']
        amount = request.form['amount']
        date_str = request.form['date']
        category = request.form['category']
        pay_mode = request.form['pay_mode']
        userID = current_user.id

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            new_data = Data(description=description, amount=amount, date=date_obj, category=category, pay_mode=pay_mode, tran_type='expense', user_id=userID)
            db.session.add(new_data)
            db.session.commit()
            flash("Data inserted successfully")
            return redirect(url_for('Index'))
        except Exception as e:
            return f'An error occurred: {str(e)}'


# Insert new income
@app.route('/insert_income', methods=['POST'])
@login_required
def insert_income():
    switch_db(current_user.db_path)
    if request.method == 'POST':
        description = request.form['description']
        amount = request.form['amount']
        date_str = request.form['date']
        category = request.form['category']
        pay_mode = request.form['pay_mode']
        userID = current_user.id

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            new_data = Data(description=description, amount=amount, date=date_obj, category=category, pay_mode=pay_mode, tran_type='income', user_id=userID)
            db.session.add(new_data)
            db.session.commit()
            flash("Income data inserted successfully")
            return redirect(url_for('Index'))
        except Exception as e:
            return f'An error occurred: {str(e)}'


# Index page for expenses
@app.route('/Index')
@login_required
def Index():
    switch_db(current_user.db_path)
    expenses_data = Data.query.filter_by(tran_type='expense', user_id=current_user.id).all()
    return render_template("index.html", expenses=expenses_data, user=current_user)


# Income page
@app.route('/income')
@login_required
def income():
    switch_db(current_user.db_path)
    income_data = Data.query.filter_by(tran_type='income', user_id=current_user.id).all()
    return render_template("income.html", incomes=income_data, user=current_user)


# Transaction summary
@app.route('/transactions')
@login_required
def transactions():
    switch_db(current_user.db_path)
    total_income = db.session.query(func.sum(Data.amount)).filter_by(tran_type='income', user_id=current_user.id).scalar() or 0
    total_expense = db.session.query(func.sum(Data.amount)).filter_by(tran_type='expense', user_id=current_user.id).scalar() or 0
    balance = total_income - total_expense
    transactions = Data.query.filter_by(user_id=current_user.id).all()
    return render_template("transactions.html", balance=balance, income_amount=total_income, expense_amount=total_expense, transactions=transactions, user=current_user)


# Update expense
@app.route('/update/<int:expense_id>', methods=['POST'])
@login_required
def update(expense_id):
    switch_db(current_user.db_path)
    my_data = Data.query.get(expense_id)
    if my_data:
        my_data.description = request.form['description']
        my_data.amount = float(request.form['amount'])
        my_data.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        my_data.category = request.form['category']
        my_data.pay_mode = request.form['pay_mode']
        my_data.tran_type = 'expense'
        db.session.commit()
        flash("Expense updated successfully")
    else:
        flash("Error in updating")
    return redirect(url_for('Index'))


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
