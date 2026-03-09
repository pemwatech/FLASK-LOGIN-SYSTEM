from flask import Flask, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

# Health route for pings
@app.route('/health')
def health():
    return 'OK', 200

# Database helpers
def connect_db():
    db = sqlite3.connect('auth.db')
    db.row_factory = sqlite3.Row
    return db

def create_table():
    db = connect_db()
    db.execute('CREATE TABLE IF NOT EXISTS auth(name,email,phone_number,password)')
    db.commit()
    db.close()

create_table()

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

        db = connect_db()
        user = db.execute('SELECT * FROM auth WHERE email=?', (email,)).fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
            return f'Welcome {user["name"]}'
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
            db = connect_db()
            user_exists = db.execute(
                'SELECT * FROM auth WHERE email=? OR phone_number=?',
                (email, phone_number)
            ).fetchone()
            if user_exists:
                flash('User already exists')
                db.close()
                return redirect('/register')

            db.execute(
                'INSERT INTO auth(name,email,phone_number,password) VALUES (?,?,?,?)',
                (name,email,phone_number,password_hash)
            )
            db.commit()
            db.close()
            flash('Registration successful')
            return redirect('/login')
        except Exception as e:
            flash(f'Error: {e}')
            return redirect('/register')

    return render_template('register.html')