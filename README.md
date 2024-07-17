FinRise web application designed to help users track their income and expenses, set financial goals, and monitor their progress towards achieving these goals. 
The application provides a user-friendly interface for inputting and updating financial data, generating detailed reports, and ensuring users remain on track with their financial planning.

Features

User Authentication: Secure user sign-up, login, and logout functionality using bcrypt for password hashing.

Expense Tracking: Users can input their monthly income and detailed expenses across various categories such as housing, transportation, utilities, and more.

Financial Goal Setting: Users can set financial goals and time periods to achieve these goals, and the system tracks their progress.

Dynamic Reporting: Generates reports summarizing expenses, remaining budget, highlights the categories with the highest expenses and get insights on how to manage their finances better.

Expense Importances: Allows users to specify the importance of each expense category to prioritize spending.

Data Persistence: Utilizes SQLite for storing user data, financial information, and expense records.


Technologies Used

Flask: Python web framework for building the web application.

SQLite: Database to store user and financial information.

bcrypt: Library for hashing passwords to ensure security.

HTML/CSS: Frontend for rendering templates.

JavaScript: For client-side functionality and API interactions.


Installation

1.Clone the repository:
git clone https://github.com/yourusername/Finrise.git
cd Finrise

2.Create a virtual environment:
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3.Insatll the package required
python -m pip install <package>

3.Run the file "create.py" to create the database and tables.

4.Finally run the file "app.py" to use the website.

