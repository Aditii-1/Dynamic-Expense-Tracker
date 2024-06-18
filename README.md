
# 💰 DYNAMIC EXPENSE TRACKER 💰 
### 💸 Track Your Expenses Seamlessly with Expense Tracker 💸
Expense Tracker is a powerful web application designed to help you manage your finances effortlessly. By providing a user-friendly interface, it enables you to track your income and expenses, view detailed analytics, and make informed financial decisions.
This project utilizes HTML, CSS, JavaScript, Flask (a Python framework), and SQL Alchemy for database management.

## 📌 Features
- **User Authentication:** Secure login and signup pages that dynamically handle multiple databases.

-  **Expense Management:** Add, edit, and delete income and expenses with ease.

-  **Analytics:** Visualize your financial data using responsive bar charts.

- **Responsive Design:** Optimized for various devices, providing a seamless experience on desktops, tablets, and mobile phones.

## 📌 Technologies Used

🛠️**Frontend:** HTML, CSS, JavaScript

🛠️**Backend:** Flask (Python framework)

🛠️**Database:** SQL Alchemy

## 📌 Prerequisites

- A code editor (example, VSCode)

- Python installed on your machine

## 📌 Installation

**Clone the Repository**

```bash
git clone "https://github.com/Aditi-Gopinath/Dynamic-Expense-Tracker"
cd expense-tracker
```

**Set Up a Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
```
**Install the Required Dependencies**
```bash
pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug
```
**Configure the Database**
-	Update the database URI in the config.py file.
```bash
SQLALCHEMY_DATABASE_URI = 'sqlite:///expense_tracker.db'  # Example for SQLite
```

-	Set up the database:
```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```
**Run the Application**
```bash
flask run
```
Open your web browser and navigate to http://127.0.0.1:5000 to access the application.

## 📌 Usage

**Step 1:** REGISTRATION AND LOGIN

- **Sign Up:** Create an account by providing your personal details.

- **Login:** Access your account using your credentials.

**Step 2:** MANAGING EXPENSES

- **Add Expense:** Record your expenses by filling out the expense form.

- **View Expenses:** View a list of all recorded expenses.

- **Delete Expense:** Remove any unwanted expenses.

**Step 3:** VIEWING ANALYTICS

- **Bar Chart Visualization:** View your spending habits through dynamically generated bar charts for better financial insights.


## 📌Documentation

For detailed documentation about Flask ,visit 
[documentation](https://flask.palletsprojects.com/en/3.0.x/)


## 📌 Contributions

**Don't forget to star ⭐ the repository!**

Contributions make the open-source community an amazing place to learn, inspire, and create. Whether you're fixing bugs, adding new features, improving documentation, or spreading the word, your contributions are greatly appreciated.

We welcome contributions to improve the Expense Tracker! Here's how you can contribute:

- **_Explore the Issues:_** Start by checking the Issues page to see if someone has reported a problem or requested a feature you're interested in working on. If your idea or the bug you've found isn't listed, you can open a new issue. This lets the community discuss and validate the issue or enhancement before you spend time on it.

- **_Fork the Project:_** Fork the repository by clicking the 'Fork' button at the top right of the page. This creates a copy of the codebase under your GitHub account.

- **_Create Your Feature Branch:_** From your fork, create a new branch for your feature or bugfix. Use a clear and descriptive name for your branch, such as `git checkout -b feature/YourFeatureName` or `git checkout -b bugfix/YourBugfixDescription`.

- **_Make Your Changes:_** Implement your changes in your feature branch. Be sure to adhere to the coding standards and guidelines of the project. It's also a good practice to write meaningful commit messages that clearly describe the changes you've made.

- **_Test Your Changes:_** Before submitting your changes, thoroughly test them to ensure they work as expected and don't introduce new issues.

- **_Submit a Pull Request:_** Once you're happy with your changes, push your branch to your fork on GitHub and then submit a pull request to the original repository. In your pull request description, explain the changes you've made and reference any related issue numbers.

- **_Code Review:_** After submitting your pull request, the project maintainers will review your changes. Be open to feedback and be prepared to make further adjustments to your code. This is a collaborative process, and constructive discussions are key to making great contributions.


## 📌Additional Guidelines

- **Follow the Code of Conduct:** Always conduct yourself in a respectful and positive manner when interacting with the community.

- **Ask Questions:** Don't hesitate to ask for help or clarification if you're unsure about something. The community is here to support each other.

## 📌 Roadmap for Future Development

**Phase 1: Feature Enhancements**

- _User Profile:_ Add functionality for users to manage their profiles.

- _Advanced Analytics:_ Introduce more detailed analytics and reporting features.

**Phase 2: User Experience Improvements**

- _Notifications:_ Implement email and in-app notifications for expense tracking and reminders.

**Phase 3: Security and Compliance**

- _Enhanced Security:_ Implement additional security measures to protect user data.

- _Data Privacy Compliance:_ Ensure compliance with data protection regulations such as GDPR.

**Phase 4: Expansion and Scaling**

- _Multiple Currencies:_ Introduce support for multiple currencies.

- _Regional Expansion:_ Expand the platform's reach to additional regions and languages.


By following this roadmap, we aim to continuously improve the Expense Tracker and provide a reliable tool for managing personal finances.


## 📌 Feedback

If you have any feedback, please reach out at aditigopinath2@gmail.com
