from flask import Flask, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# Database connection helper
def get_db():
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    return conn

# Create table if not exists
def create_table():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS auth(
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            phone_number VARCHAR(20) UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()

# Health route
@app.route('/health')
def health():
    return 'OK', 200

# Main page
@app.route('/')
def log():
    return render_template('login.html')

# Login
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT name, password FROM auth WHERE email=%s', (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            return f'Welcome {user[0]}'
        else:
            flash('Wrong credentials')

    return render_template('login.html')

# Register
@app.route('/register', methods=['POST','GET'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password1 = request.form['password']
        password2 = request.form['Confirm_password']

        if password1 != password2:
            flash('Password mismatch')
            return redirect('/register')

        password_hash = generate_password_hash(password1)

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT * FROM auth WHERE email=%s OR phone_number=%s', (email, phone_number))
            user_exists = cur.fetchone()
            if user_exists:
                flash('User already exists')
                cur.close()
                conn.close()
                return redirect('/register')

            cur.execute(
                'INSERT INTO auth(name,email,phone_number,password) VALUES (%s,%s,%s,%s)',
                (name,email,phone_number,password_hash)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('Registration successful')
            return redirect('/login')
        except Exception as e:
            flash(f'Error: {e}')
            return redirect('/register')

    return render_template('register.html')