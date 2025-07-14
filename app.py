from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from credit_score import calculate_credit_score

app = Flask(__name__)
app.secret_key = 'secretkey'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Init DB
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']

        # Password rules
        if len(password) < 6 or not any(c.isdigit() for c in password):
            return render_template('register.html', error="Password must be 6+ chars and include a number")

        hashed_password = generate_password_hash(password)
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)',
                         (fullname, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Email already exists")
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get user input from form
        data = {
            'on_time_payments': int(request.form['on_time_payments']),
            'missed_payments': int(request.form['missed_payments']),
            'credit_limit': float(request.form['credit_limit']),
            'current_balance': float(request.form['current_balance']),
            'credit_age': int(request.form['credit_age']),
            'loan_types': int(request.form['loan_types']),
            'recent_inquiries': int(request.form['recent_inquiries']),
        }

        score = calculate_credit_score(data)
        return render_template('dashboard.html', score=score)

    return render_template('dashboard.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
