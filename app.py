from pyexpat import model
import joblib
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import os
from datetime import datetime
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
import pymysql
pymysql.install_as_MySQLdb()
import numpy as np

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
import os
from datetime import datetime

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = "bap026a029a301n539v"
basedir = os.path.abspath(os.path.dirname(__file__))

# SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

model = joblib.load('model.joblib') 
db = SQLAlchemy(app)

# Initialize the LoginManager
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    db_path = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)  # Add balance field
    data = db.relationship('Data', backref='user', lazy=True)

    def __init__(self, email, username, password, db_path, balance=0.0):
        self.email = email
        self.username = username
        self.password = password
        self.db_path = db_path
        self.balance = balance

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    pay_mode = db.Column(db.String(50), nullable=False)
    tran_type = db.Column(db.String(10), nullable=False)
    new_balance = db.Column(db.Float, nullable=False)
    fraud = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_time = db.Column(db.DateTime, default=datetime.now, nullable=False)  # Add transaction time

    def __init__(self, description, amount, date, category, pay_mode, tran_type, new_balance, fraud, user_id):
        self.description = description
        self.amount = amount
        self.date = date
        self.category = category
        self.pay_mode = pay_mode
        self.tran_type = tran_type
        self.new_balance = new_balance
        self.fraud = fraud
        self.user_id = user_id

def create_tables():
    with app.app_context():
        try:
            db.create_all()
            print("Tables created successfully!")
        except Exception as e:
            print(f"Error: {e}")

def get_balance():
    # Get the current logged-in user's balance
    user = User.query.filter_by(id=current_user.id).first()  # Get current logged-in user
    return user.balance  # Assuming 'balance' is the field storing the user's balance

def switch_db(db_path):
    # This will update the database URI dynamically
    new_uri = f'sqlite:///{db_path}'  # Update this if using other DB types
    if app.config['SQLALCHEMY_DATABASE_URI'] != new_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = new_uri
        db.engine.dispose()  # Dispose of the current engine
        db.session.configure(bind=db.create_engine(new_uri))  # Reconfigure session to use new engine

@app.route('/')
def home():
    return render_template("home.html", user=current_user)



@app.route('/insert', methods=['POST'])
@login_required
def insert():
    switch_db(current_user.db_path)

    if request.method == 'POST':
        # Fetch input data from the form
        description = request.form['description']
        amount = float(request.form['amount'])  # Ensure amount is treated as a float
        date_str = request.form['date']
        category = request.form['category']
        pay_mode = request.form['pay_mode']
        new_balance = float(request.form['new_balance'])  # Assuming this is the new balance entered by the user
        userID = current_user.id

        try:
            # Calculate available balance for the user
            total_income = db.session.query(func.sum(Data.amount)).filter_by(tran_type='income', user_id=userID).scalar() or 0
            total_expense = db.session.query(func.sum(Data.amount)).filter_by(tran_type='expense', user_id=userID).scalar() or 0
            available_balance = total_income - total_expense

            # Check if available balance is sufficient
            if available_balance < amount:
                flash("Insufficient balance to record this expense.", "danger")
                return redirect(url_for('Index'))

            # Convert date from string to date object
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Get current time for the transaction
            transaction_time = datetime.now()

            # Convert amount and new_balance to floats for calculations
            amount = float(amount)
            new_balance = float(new_balance)
            # Calculate the user's balance
            total_income = db.session.query(func.sum(Data.amount)).filter_by(tran_type='income', user_id=userID).scalar() or 0
            total_expense = db.session.query(func.sum(Data.amount)).filter_by(tran_type='expense', user_id=userID).scalar() or 0
            old_balance = total_income - total_expense

            # Fraud detection logic
            fraud_detected = False
            if new_balance > old_balance:
                fraud_detected = True
            if old_balance < amount:
                fraud_detected = True
            if new_balance != old_balance - amount:
                fraud_detected = True
                
            if fraud_detected:
                flash("Expense recorded but flagged as fraud.", "warning")
            else:
                flash("Expense recorded successfully.", "success")

            # Record the expense
            new_data = Data(
                description=description,
                amount=amount,
                date=date_obj,
                category=category,
                pay_mode=pay_mode,
                new_balance=new_balance,
                tran_type='expense',
                user_id=userID,
                fraud=fraud_detected
            )
         
            db.session.add(new_data)
            db.session.commit()

            flash("Expense recorded successfully.", "success")
            return redirect(url_for('Index'))

        except Exception as e:
            return f'An error occurred: {str(e)}'

@app.route('/update/<int:expense_id>', methods=['POST'])
@login_required
def update(expense_id):
    switch_db(current_user.db_path)

    my_data = Data.query.get(expense_id)
    if my_data:
        try:
            # Fetch updated data from the form (excluding amount and new_balance)
            updated_description = request.form['description']
            updated_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            updated_category = request.form['category']
            updated_pay_mode = request.form['pay_mode']

            # Get current time for the transaction update
            transaction_time = datetime.now()

            # Calculate the available balance before updating
            userID = current_user.id
            total_income = db.session.query(func.sum(Data.amount)).filter_by(tran_type='income', user_id=userID).scalar() or 0
            total_expense = db.session.query(func.sum(Data.amount)).filter_by(tran_type='expense', user_id=userID).scalar() or 0
            old_balance = total_income - total_expense   # Add back the current record's amount to old balance

            # Do not update fraud logic or balance as amount and new_balance are not edited
            my_data.description = updated_description
            my_data.date = updated_date
            my_data.category = updated_category
            my_data.pay_mode = updated_pay_mode

            db.session.commit()
            flash("Expense updated successfully.", "success")
        except Exception as e:
            flash(f"An error occurred while updating: {str(e)}", "danger")
    else:
        flash("Expense not found.", "danger")

    return redirect(url_for('Index'))


@app.route('/insert_income', methods=['POST'])
@login_required
def insert_income():
    switch_db(current_user.db_path)
    
    if request.method == 'POST':
        # Fetch input data from the form
        description = request.form['description']
        amount = request.form['amount']
        date_str = request.form['date']
        category = request.form['category']
        pay_mode = request.form['pay_mode']
        new_balance = request.form['new_balance']
        userID = current_user.id

        try:
            transaction_time = datetime.now()
            # Convert the date to a datetime object
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Convert amount and new_balance to floats for calculations
            amount = float(amount)
            new_balance = float(new_balance)

            # Fetch the total income and expense for the user to calculate the old balance
            total_income = db.session.query(func.sum(Data.amount)).filter_by(tran_type='income', user_id=userID).scalar() or 0
            total_expense = db.session.query(func.sum(Data.amount)).filter_by(tran_type='expense', user_id=userID).scalar() or 0
            old_balance = total_income - total_expense

            # Logic to detect fraud (Inconsistent balance update for CASH-IN transactions)
            if new_balance != old_balance + amount:
                fraud_detected = True
            else:
                fraud_detected = False

            # Insert the new income data into the database
            new_data = Data(
                description=description,
                amount=amount,
                date=date_obj,
                category=category,
                pay_mode=pay_mode,
                new_balance=new_balance,
                tran_type='income',
                user_id=userID,
                fraud=fraud_detected  # Store the fraud status in the database
            )
            
            if fraud_detected:
                flash("Expense recorded but flagged as fraud.", "warning")
            else:
                flash("Expense recorded successfully.", "success")


            db.session.add(new_data)
            db.session.commit()

            flash("Income data inserted successfully", "success")
            return redirect(url_for('income'))

        except Exception as e:
            # Handle any errors that occur
            return f'An error occurred: {str(e)}'
    return redirect(url_for('income'))

@app.route('/update_income/<int:income_id>', methods=['POST'])
@login_required
def update_income(income_id):
    switch_db(current_user.db_path)
    
    my_data1 = Data.query.get(income_id)
    if my_data1:
        try:
            # Update the fields with the new values from the form
            updated_description1 = request.form['description']
            updated_date1 = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            updated_category1 = request.form['category']
            updated_pay_mode1 = request.form['pay_mode']

            transaction_time = datetime.now()
            
            userID = current_user.id
            total_income = db.session.query(func.sum(Data.amount)).filter_by(tran_type='income', user_id=userID).scalar() or 0
            total_expense = db.session.query(func.sum(Data.amount)).filter_by(tran_type='expense', user_id=userID).scalar() or 0
            old_balance = total_income - total_expense   # Add back the current record's amount to old balance

            # Update the fields in the record
            my_data1.description = updated_description1
            my_data1.date = updated_date1
            my_data1.category = updated_category1
            my_data1.pay_mode = updated_pay_mode1
           
            db.session.commit()
            flash("Income data updated successfully", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
    else:
        flash("Income data not found", "danger")
    
    return redirect(url_for('income'))


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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

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


@app.route('/delete/<int:id>/', methods=['GET', 'POST'])
@login_required
def delete(id):
    switch_db(current_user.db_path)
    my_data = Data.query.get(id)
    if my_data:
        db.session.delete(my_data)
        db.session.commit()
        flash("Expense data deleted successfully", "danger")
    else:
        flash("Data not found!")
    return redirect(url_for('Index'))

@app.route('/delete_income/<int:id>/', methods=['GET', 'POST'])
@login_required
def delete_income(id):
    switch_db(current_user.db_path)
    my_data = Data.query.get(id)
    if my_data:
        db.session.delete(my_data)
        db.session.commit()
        flash("Income data deleted successfully", "danger")
    else:
        flash("Income data not found!")
    return redirect(url_for('income'))

@app.route('/income')
@login_required
def income():
    switch_db(current_user.db_path)
    income_data = Data.query.filter_by(tran_type='income', user_id=current_user.id).all()
    return render_template("income.html", incomes=income_data, user=current_user)

@app.route('/Index')
@login_required
def Index():
    switch_db(current_user.db_path)
    expenses_data = Data.query.filter_by(tran_type='expense', user_id=current_user.id).all()
    return render_template("index.html", expenses=expenses_data, user=current_user)

@app.route('/transactions')
@login_required
def transactions():
    switch_db(current_user.db_path)
    total_income = db.session.query(func.sum(Data.amount)).filter_by(tran_type='income', user_id=current_user.id).scalar() or 0
    total_expense = db.session.query(func.sum(Data.amount)).filter_by(tran_type='expense', user_id=current_user.id).scalar() or 0
    balance = total_income - total_expense
    transactions = Data.query.filter_by(user_id=current_user.id).all()
    return render_template("transactions.html", balance=balance, income_amount=total_income, expense_amount=total_expense, transactions=transactions, user=current_user)

@app.route('/fraud')
@login_required
def fraud():
    switch_db(current_user.db_path)
    return render_template("fraud.html",user=current_user)


@app.route('/prediction', methods=['POST'])
def prediction():
    try:
        # Fetch input data from the form
        trans_type = request.form.get('type')
        amount = request.form.get('amount')
        oldbalanceOrg = request.form.get('oldbalanceOrg')
        newbalanceOrig = request.form.get('newbalanceOrig')

        # Input validation
        if not (trans_type and amount and oldbalanceOrg and newbalanceOrig):
            return render_template('fraud.html', 
                                   prediction_text="Error: All fields are required.",
                                   trans_type=trans_type, amount=amount,
                                   oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

        # Convert and validate transaction type
        try:
            trans_type = int(trans_type)
            if trans_type not in [1, 2, 3, 4, 5]:
                return render_template('fraud.html', 
                                       prediction_text="Error: Incorrect transaction type. Please enter a type between 1 and 5.",
                                       trans_type=trans_type, amount=amount,
                                       oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)
        except ValueError:
            return render_template('fraud.html', 
                                   prediction_text="Error: Transaction type must be an integer.",
                                   trans_type=trans_type, amount=amount,
                                   oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

        # Convert and validate numeric inputs
        try:
            amount = float(amount)
            oldbalanceOrg = float(oldbalanceOrg)
            newbalanceOrig = float(newbalanceOrig)
        except ValueError:
            return render_template('fraud.html', 
                                   prediction_text="Error: Amount, Old Balance, and New Balance must be numeric.",
                                   trans_type=trans_type, amount=amount,
                                   oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

        # Add logical checks for fraud detection
        if oldbalanceOrg < 0 or newbalanceOrig < 0:
            return render_template('fraud.html', 
                                   prediction_text="Fraud detected: Balances cannot be negative.", 
                                   fraud_detected=True,
                                   trans_type=trans_type, amount=amount,
                                   oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

        if amount < 0:
            return render_template('fraud.html', 
                                   prediction_text="Fraud detected: Amount cannot be negative.", 
                                   fraud_detected=True,
                                   trans_type=trans_type, amount=amount,
                                   oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

        # Business logic checks
        if trans_type in [2, 5]:  # CASH-OUT or TRANSFER
            if newbalanceOrig > oldbalanceOrg:
                return render_template('fraud.html', 
                                       prediction_text="Fraud detected: New balance cannot exceed old balance for CASH-OUT or TRANSFER transactions.", 
                                       fraud_detected=True,
                                       trans_type=trans_type, amount=amount,
                                       oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)
            if oldbalanceOrg < amount:
                return render_template('fraud.html', 
                                       prediction_text="Fraud detected: Insufficient balance for TRANSFER or CASH-OUT transactions.", 
                                       fraud_detected=True,
                                       trans_type=trans_type, amount=amount,
                                       oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)
                
            if newbalanceOrig != oldbalanceOrg + amount:
                return render_template('fraud.html', 
                                       prediction_text="Fraud detected: Inconsistent balance update.", 
                                       fraud_detected=True,
                                       trans_type=trans_type, amount=amount,
                                       oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)
        
        if trans_type == 1:  # CASH-IN
            if newbalanceOrig != oldbalanceOrg + amount:
                return render_template('fraud.html', 
                                       prediction_text="Fraud detected: Inconsistent balance update for CASH-IN.", 
                                       fraud_detected=True,
                                       trans_type=trans_type, amount=amount,
                                       oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

        if trans_type in [3, 4]:  # DEBIT or PAYMENT
            if amount > oldbalanceOrg:
                return render_template('fraud.html', 
                                       prediction_text="Fraud detected: Amount exceeds available balance for DEBIT or PAYMENT transactions.", 
                                       fraud_detected=True,
                                       trans_type=trans_type, amount=amount,
                                       oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)
                
            if newbalanceOrig != oldbalanceOrg + amount:
                return render_template('fraud.html', 
                                       prediction_text="Fraud detected: Inconsistent balance update.", 
                                       fraud_detected=True,
                                       trans_type=trans_type, amount=amount,
                                       oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

        # Special conditions for detecting fraud
        if trans_type == 5 and amount > 1000000:
            return render_template('fraud.html', 
                                   prediction_text="Fraud detected: TRANSFER of large amount flagged.", 
                                   fraud_detected=True,
                                   trans_type=trans_type, amount=amount,
                                   oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

        if trans_type == 2 and oldbalanceOrg == 0 and newbalanceOrig == 0 and amount > 0:
            return render_template('fraud.html', 
                                   prediction_text="Fraud detected: CASH-OUT transaction with zero balances flagged.", 
                                   fraud_detected=True,
                                   trans_type=trans_type, amount=amount,
                                   oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

        if amount > 1000000:
            return render_template('fraud.html', 
                                   prediction_text="Fraud detected: High transaction amount flagged.", 
                                   fraud_detected=True,
                                   trans_type=trans_type, amount=amount,
                                   oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

        
        arr = np.array([[trans_type, amount, oldbalanceOrg, newbalanceOrig]])

        # Make prediction using the ML model
        pred = model.predict(arr)
        
        # Map prediction result to meaningful output
        result = "Fraud detected" if pred[0] == 1 else "Not Fraud"

        # Return prediction result
        return render_template('fraud.html', 
                               prediction_text=f"{result}", 
                               fraud_detected=(pred[0] == 1),
                               trans_type=trans_type, amount=amount,
                               oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

    except Exception as e:
        # Handle unexpected errors
        return render_template('fraud.html', 
                               prediction_text=f"An unexpected error occurred: {e}", 
                               trans_type=trans_type, amount=amount,
                               oldbalanceOrg=oldbalanceOrg, newbalanceOrig=newbalanceOrig)

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
