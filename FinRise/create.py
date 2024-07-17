import sqlite3
conn=sqlite3.connect("database.db")
cur=conn.cursor()
cur.execute('''CREATE TABLE UserFinancialInfo (
    email TEXT PRIMARY KEY,
    financial_goal FLOAT,
    time_period INTEGER,
    FOREIGN KEY (email) REFERENCES Users(email)
);''')
cur.execute("CREATE TABLE IF NOT EXISTS user( Username TEXT,email TEXT PRIMARY KEY,password TEXT)")
cur.execute('''CREATE TABLE IF NOT EXISTS Expenses(
                email TEXT ,
                income REAL,
                month TEXT,
                year INTEGER,
                vacation REAL DEFAULT 0,
                vacation_importance INTEGER DEFAULT 0,
                daily_transportation REAL DEFAULT 0,
                daily_transportation_importance INTEGER DEFAULT 0,
                utilities REAL DEFAULT 0,
                utilities_importance INTEGER DEFAULT 0,
                savings REAL DEFAULT 0,
                savings_importance INTEGER DEFAULT 0,
                housing REAL DEFAULT 0,
                housing_importance INTEGER DEFAULT 0,
                debt_payments REAL DEFAULT 0,
                debt_payments_importance INTEGER DEFAULT 0,
                healthcare REAL DEFAULT 0,
                healthcare_importance INTEGER DEFAULT 0,
                personal_care REAL DEFAULT 0,
                personal_care_importance INTEGER DEFAULT 0,
                food REAL DEFAULT 0,
                food_importance INTEGER DEFAULT 0,
                insurance REAL DEFAULT 0,
                insurance_importance INTEGER DEFAULT 0,
                education REAL DEFAULT 0,
                education_importance INTEGER DEFAULT 0,
                entertainment REAL DEFAULT 0,
                entertainment_importance INTEGER DEFAULT 0,
                charity REAL DEFAULT 0,
                charity_importance INTEGER DEFAULT 0,
                taxes REAL DEFAULT 0,
                taxes_importance INTEGER DEFAULT 0,
                miscellaneous REAL DEFAULT 0,
                miscellaneous_importance INTEGER DEFAULT 0,
                amount_saved REAL DEFAULT 0,
            FOREIGN KEY (email) REFERENCES user(email)
                )''')
cur.close()
conn.close()
