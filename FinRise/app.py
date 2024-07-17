import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session,redirect,flash
import traceback
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = 'key'

def connect_db():
	return sqlite3.connect('database.db')

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if 'email' in session:
        return render_template('main.html', error_message="You are already logged in.")
    if request.method == 'POST':
        name = request.form.get('Username')
        email = request.form.get('Email')
        password = request.form.get('Password')
        hashed_password = hash_password(password)
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute("SELECT email FROM user WHERE email=?", (email,))
            result = cur.fetchone()
            if result: 
                return redirect(url_for('home'))
            else:
                cur.execute("INSERT INTO user (Username, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
                conn.commit() 
                session['signed_up'] = True
                return redirect(url_for('home'))
        except Exception as e:
            conn.rollback()
            flash('Error: ' + str(e), 'error')
            print('Error:', str(e)) 
            return redirect(url_for('home'))
        finally:
            cur.close()
            conn.close()
    else:
        return render_template('SignUp.html')

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('home'))

def verify_password(entered_password, hashed_password):
    if isinstance(entered_password, str):
        entered_password = entered_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(entered_password, hashed_password)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return render_template('main.html', error_message="You are already logged in.")
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT password FROM user WHERE email=?", (email,))
            hashed_password = cur.fetchone()
            if hashed_password:
                if verify_password(password, hashed_password[0]):
                    session['email'] = email
                    cur.close()
                    conn.commit()
                    conn.close()
                    return redirect(url_for('home')) 
                else:
                    error_message = 'Invalid email or password'
                    return render_template('login.html', error=error_message)
            else:
                error_message = 'Invalid email or password'
                return render_template('login.html', error=error_message)
        except Exception as e:
            error_message = 'An error occurred: ' + str(e)
            return render_template('login.html', error=error_message)
    else:
        return render_template('login.html')
    
@app.route('/input', methods=['POST', 'GET'])
def input():
    if 'email' in session:
        email = session['email'] 
        conn = connect_db()
        cur = conn.cursor()
        if request.method == 'GET':
            cur.execute("SELECT time_period, financial_goal FROM UserFinancialInfo WHERE email=?", (email,))
            financial_info = cur.fetchone()
            if financial_info:
                time_period, financial_goal = financial_info
                return render_template('input.html', time_period=time_period, financial_goal= financial_goal)
            else:
                return render_template('input.html')
        if request.method == 'POST':
            try:
                email = session['email']
                income = float(request.form.get('income', 0) or 0)
                month = request.form.get('month')
                year = request.form.get('year')
                time_period = int(request.form.get('timePeriod', 0))
                financial_goal = float(request.form.get('financialGoal', 0))
                cur.execute("SELECT COUNT(*) FROM UserFinancialInfo WHERE email=?", (email,))
                if cur.fetchone()[0] == 0:
                    cur.execute("INSERT INTO UserFinancialInfo (email, time_period, financial_goal) VALUES (?, ?, ?)",
                                (email, time_period, financial_goal))
                cur.execute("SELECT COUNT(*) FROM Expenses WHERE email=? AND month=? AND year=?", (email, month, year))
                if cur.fetchone()[0] > 0:
                    flash('Records already exist for this month and year.', 'info')
                    return redirect(url_for('input'))
                expenses = {key:request.form[key] if request.form[key] != '' else 0.0 for key in request.form if key not in ['income', 'month', 'year', 'timePeriod', 'financialGoal']}
                importances = {key.replace('-importance', ''): int(request.form.get(key, 0)) for key in request.form if key.endswith('-importance')}
                t = (session['email'], income, month, year) + tuple(expenses.get(key, 0) for key in ['Vacation', 'daily-transportation', 'utilities', 'savings',
                                                    'housing', 'debt-payments', 'healthcare', 'personal-care',
                                                    'food', 'insurance', 'education', 'entertainment',
                                                    'charity', 'taxes', 'miscellaneous']) + tuple(importances.get(key, 0) for key in ['Vacation', 'daily-transportation', 'utilities', 'savings',
                                                       'housing', 'debt-payments', 'healthcare', 'personal-care',
                                                       'food', 'insurance', 'education', 'entertainment',
                                                      'charity', 'taxes', 'miscellaneous'])
                cur.execute('''INSERT INTO Expenses 
               (email, income, month, year,
                vacation, daily_transportation, utilities, savings, housing, 
                debt_payments, healthcare, personal_care, food, insurance, 
                education, entertainment, charity, taxes, miscellaneous,
                vacation_importance, daily_transportation_importance, utilities_importance, 
                savings_importance, housing_importance, debt_payments_importance, 
                healthcare_importance, personal_care_importance, food_importance, 
                insurance_importance, education_importance, entertainment_importance, 
                charity_importance, taxes_importance, miscellaneous_importance) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', t)
                conn.commit()
                flash('Your expenses have been successfully submitted.', 'success')
                return redirect(url_for('input'))
            except Exception as e:
                traceback.print_exc()
                conn.rollback()
                return jsonify({'error': 'An error occurred while processing your request. Please try again later.'}), 500
            finally:
                cur.close()
                conn.close()
    else:
        return jsonify({'error': 'Unauthorized access. Please log in.'})
        
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    if 'email' in session: 
        email = session['email']
        month = request.args.get('month')
        year = int(request.args.get('year'))
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM Expenses WHERE email=? AND month=? AND year=?", (email, month, year))
            count = cur.fetchone()[0]
            if count > 0:
                return jsonify({'exists': True})  # Records exist
            else:
                cur.execute("SELECT financial_goal, time_period FROM UserFinancialInfo WHERE email=?", (email,))
                expenses = cur.fetchone() 
                if expenses:
                    return jsonify({'exists': False, 'financial_goal': expenses[0], 'time_period': expenses[1]}) 
                else:
                    return jsonify({'exists': False, 'financial_goal': 0, 'time_period': 0})
        except Exception as e:
            return jsonify({'error': str(e)})
        finally:
            cur.close()
            conn.close()
    else:
        return jsonify({'error': 'Unauthorized'})

@app.route('/update', methods=['POST', 'GET'])
def update():
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized access. Please log in.'})
    email = session['email']
    conn = connect_db()
    cur = conn.cursor()
    if request.method == 'GET':
        try:
            cur.execute("SELECT time_period, financial_goal FROM UserFinancialInfo WHERE email=?", (email,))
            financial_info = cur.fetchone()
            if financial_info:
                time_period, financial_goal = financial_info
                return render_template('update.html', time_period=time_period, financial_goal=financial_goal)
            else:
                return render_template('update.html')
        except Exception as e:
            conn.close()
            return jsonify({'error': str(e)})

    elif request.method == 'POST':
        try:
            income = float(request.form.get('income', 0) or 0)
            month = request.form.get('month')
            year = request.form.get('year')
            time_period = int(request.form.get('timePeriod', 0))
            financial_goal = float(request.form.get('financialGoal', 0))
            cur.execute("UPDATE UserFinancialInfo SET time_period=?, financial_goal=? WHERE email=?", (time_period, financial_goal, email))
            conn.commit()
            cur.execute("UPDATE Expenses SET income=? WHERE email=? AND month=? AND year=?", (income, email, month, year))
            conn.commit()
            if cur.execute("SELECT COUNT(*) FROM Expenses WHERE email=? AND month=? AND year=?", (email, month, year)).fetchone()[0] > 0:
                expenses = {key:request.form[key] if request.form[key] != '' else 0.0 for key in request.form if key not in ['income', 'month', 'year', 'timePeriod', 'financialGoal']}
                importances = {key.replace('-importance', ''): int(request.form.get(key, 0)) for key in request.form if key.endswith('-importance')}
                update_values = tuple(expenses.get(key, 0) for key in ['Vacation', 'daily-transportation', 'utilities', 'savings',
                                                    'housing', 'debt-payments', 'healthcare', 'personal-care',
                                                    'food', 'insurance', 'education', 'entertainment',
                                                    'charity', 'taxes', 'miscellaneous']) +tuple(importances.get(key, 0) for key in ['Vacation', 'daily-transportation', 'utilities', 'savings',
                                                       'housing', 'debt-payments', 'healthcare', 'personal-care',
                                                       'food', 'insurance', 'education', 'entertainment',
                                                      'charity', 'taxes', 'miscellaneous']) + (email, month, year)
                cur.execute('''UPDATE Expenses SET 
                        vacation=?, daily_transportation=?, utilities=?, savings=?, housing=?, 
                        debt_payments=?, healthcare=?, personal_care=?, food=?, insurance=?, 
                        education=?, entertainment=?, charity=?, taxes=?, miscellaneous=?, 
                        vacation_importance=?, daily_transportation_importance=?, utilities_importance=?, 
                         savings_importance=?, housing_importance=?, debt_payments_importance=?, 
                            healthcare_importance=?, personal_care_importance=?, food_importance=?, 
                        insurance_importance=?, education_importance=?, entertainment_importance=?, 
                    charity_importance=?, taxes_importance=?, miscellaneous_importance=? 
                    WHERE email=? AND month=? AND year=?
                        ''', update_values)
                conn.commit()
                flash('Your expenses have been successfully updated.', 'success')
                return redirect(url_for('update'))
            else:
                flash('No records found to update for this month and year.', 'error')
                return redirect(url_for('update'))
        except Exception as e:
            conn.rollback()
            flash(f'Database error: {str(e)}', 'error')
            return jsonify({'error': f'Database error: {str(e)}'})
        finally:
            conn.close()
    else:
        conn.close()
        return jsonify({'error': 'Invalid request method.'})

@app.route('/api/values', methods=['GET'])
def expenses():
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized access. Please log in.'})
    email = session['email']
    month = request.args.get('month')
    year = request.args.get('year') 
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT income, Vacation, Vacation_importance, daily_transportation, daily_transportation_importance,
                    utilities, utilities_importance, savings, savings_importance, housing, housing_importance,
                    debt_payments, debt_payments_importance, healthcare, healthcare_importance, personal_care,
                    personal_care_importance, food, food_importance, insurance, insurance_importance,
                    education, education_importance, entertainment, entertainment_importance, charity,
                    charity_importance, taxes, taxes_importance, miscellaneous, miscellaneous_importance
            FROM Expenses
            WHERE month = ? AND year = ? AND email = ?''', (month, year, email))
        row = cursor.fetchone()
        if not row:
            print("No data found for user.") 
            return jsonify({}), 404
        response = {
        "income": row[0],
        "Vacation": row[1], "Vacation_importance": row[2],
        "daily_transportation": row[3], "daily_transportation_importance": row[4],
        "utilities": row[5], "utilities_importance": row[6],
        "savings": row[7], "savings_importance": row[8],
        "housing": row[9], "housing_importance": row[10],
        "debt_payments": row[11], "debt_payments_importance": row[12],
        "healthcare": row[13], "healthcare_importance": row[14],
        "personal_care": row[15], "personal_care_importance": row[16],
        "food": row[17], "food_importance": row[18],
        "insurance": row[19], "insurance_importance": row[20],
        "education": row[21], "education_importance": row[22],
        "entertainment": row[23], "entertainment_importance": row[24],
        "charity": row[25], "charity_importance": row[26],
        "taxes": row[27], "taxes_importance": row[28],
        "miscellaneous": row[29], "miscellaneous_importance": row[30]
    }
        return jsonify(response)
    
@app.route('/report', methods=['POST', 'GET'])
def generate_report():
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized access. Please log in.'}) 
    financial_info = None
    expenses_data = None
    remaining = 0
    max_category = None
    if request.method == 'GET':
        return render_template('report.html', financial_info=financial_info, expenses_data=expenses_data,
                               remaining=remaining, max_category=max_category)
    user_email = session['email']
    month = request.form.get('month')
    year = request.form.get('year')
    if not month or not year:
        return jsonify({'error': "Month and year must be provided."})

    try:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute('''SELECT financial_goal, time_period FROM UserFinancialInfo WHERE email=?''', (user_email,))
            financial_info = cur.fetchone()
            financial_goal=financial_info[0]
            time_period=financial_info[1]
            if not financial_info:
                return jsonify({'error': "Financial information not available."})

            cur.execute('''SELECT income, Vacation, daily_transportation, utilities, savings,
                        housing, debt_payments, healthcare, personal_care, food, insurance, 
                        education, entertainment, charity, taxes, miscellaneous 
                        FROM Expenses WHERE email=? AND month=? AND year=?''', (user_email, month, year))
            expenses_data = cur.fetchone()
            if not expenses_data:
                return jsonify({
                    'financial_info': financial_info,
                    'expenses_data': [],
                    'remaining': remaining,
                    'max_category': max_category,
                    'message': 'No expenses found for the selected period.'
                })


            cur.execute('''SELECT income FROM Expenses where email=? AND month=? AND year=?''', (user_email, month, year))
            income = cur.fetchone()[0]
            
            cur.execute('''SELECT housing, utilities, daily_transportation, food, debt_payments, healthcare, insurance, taxes FROM Expenses where email=? AND month=? AND year=?''', (user_email, month, year))
            essential_data = cur.fetchone()
            total=sum(essential_data)
            cur.execute('''SELECT housing_importance, utilities_importance, daily_transportation_importance, food_importance, debt_payments_importance, healthcare_importance, insurance_importance, taxes_importance FROM Expenses where email=? AND month=? AND year=?''', (user_email, month, year))
            essential_imp = cur.fetchone()
    
        
            cur.execute('''SELECT education, charity FROM Expenses where email=? AND month=? AND year=?''', (user_email, month, year))
            savings_data = cur.fetchone()
            total+=sum(savings_data)
            cur.execute('''SELECT education_importance, charity_importance FROM Expenses where email=? AND month=? AND year=?''', (user_email, month, year))
            savings_imp = cur.fetchone()

        
            cur.execute('''SELECT entertainment, personal_care, miscellaneous, vacation FROM Expenses where email=? AND month=? AND year=?''', (user_email, month, year))
            personal_data = cur.fetchone()
            total+=sum(personal_data)
            cur.execute('''SELECT entertainment_importance, personal_care_importance, miscellaneous_importance, vacation_importance FROM Expenses where email=? AND month=? AND year=?''', (user_email, month, year))
            personal_imp = cur.fetchone()  

        
            essential_limit = 0.6 * income
            savings_limit = 0.2 * income
            personal_limit = 0.2 * income

            if sum(personal_data) > personal_limit:
                personal_imp_filtered = [imp for imp, expense in zip(personal_imp, personal_data) if expense != 0]
                personal_data_filtered = [expense for expense in personal_data if expense != 0]
                personal_category = [expense for imp, expense in zip(personal_imp_filtered, personal_data_filtered) if imp == min(personal_imp_filtered)]
                max_index = personal_data.index(max(personal_category))
                personal_attributes = ['entertainment', 'personal_care', 'miscellaneous', 'vacation']
                max_category = personal_attributes[max_index]

            elif sum(essential_data) > essential_limit:
                essential_imp_filtered = [imp for imp, expense in zip(essential_imp, essential_data) if expense != 0]
                essential_data_filtered = [expense for expense in essential_data if expense != 0]
                essential_category = [expense for imp, expense in zip(essential_imp_filtered, essential_data_filtered) if imp == min(essential_imp_filtered)]
                max_index = essential_data.index(max(essential_category))
                essential = ['housing', 'utilities', 'daily_transportation', 'food', 'debt_payments', 'healthcare', 'insurance', 'taxes']                    
                max_category = savings_attributes[max_index]
                
            elif sum(savings_data) > savings_limit:
                savings_imp_filtered = [imp for imp, expense in zip(savings_imp, savings_data) if expense != 0]
                savings_data_filtered = [expense for expense in savings_data if expense != 0]
                savings_category = [expense for imp, expense in zip(savings_imp_filtered, savings_data_filtered) if imp == min(savings_imp_filtered)]
                max_index = savings_data.index(max(savings_category))
                savings_attributes = ['education', 'charity']
                max_category = savings_attributes[max_index]
            
            cur.execute("""UPDATE Expenses SET amount_saved= ? WHERE email=? AND month=? AND year=? """,(income-total,user_email, month, year))
            conn.commit()
            cur.execute('''SELECT month, year, amount_saved, savings FROM Expenses WHERE email=? ''', (user_email,))
            rows = cur.fetchall()
            index = -1
            for i, row in enumerate(rows):
                m, y, _, _ = row 
                if m == month and y == int(year):
                    index = i
                    break
            total_saved_up_to_index = 0
            for i, row in enumerate(rows):
                if i <= index:
                    amount_saved, savings = row[2], row[3] 
                    total_saved_up_to_index += amount_saved + savings
            remaining = financial_goal - total_saved_up_to_index
            average_monthly_savings=total_saved_up_to_index//(index+1)
            months_to_goal =remaining//average_monthly_savings
            cur.execute('''SELECT month,year FROM EXPENSES WHERE email=? ''', (user_email,))
            ind = cur.fetchall().index((month,int(year))) + 1
            remaining_months = time_period - ind
            if remaining_months == 0:
                time_period_reached = True
            else:
                time_period_reached = False

            return jsonify({
                'financial_info': financial_info,
                'expenses_data': expenses_data,
                'remaining': remaining,
                'total_saved_up_to_index':total_saved_up_to_index,
                'max_category': max_category,
                'months_to_goal': months_to_goal,
                'time_period_reached': time_period_reached,
                'remaining_months': remaining_months
            })
        
    except Exception as e:
        return jsonify({'error': 'An error occurred: ' + str(e)})


if __name__ == '__main__':
	app.run(debug=True,port=5000)
