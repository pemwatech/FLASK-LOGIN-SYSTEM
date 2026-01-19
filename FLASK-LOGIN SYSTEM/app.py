from flask import Flask,render_template,url_for,flash,request,redirect
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3

app=Flask(__name__)
app.secret_key=your secret_key(any random number)


def connect_db():
    db=sqlite3.connect('auth.db')
    db.row_factory=sqlite3.Row
    return db

def create_table():
    db=connect_db()
    db.execute('CREATE TABLE IF NOT EXISTS auth(name,email,phone_number,password)')
    db.close()
create_table()


@app.route('/',methods=['POST','GET'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']

        db=connect_db()
        user=db.execute('SELECT * FROM auth WHERE email=?',(email,)).fetchone()
        if user and check_password_hash(user['password'],password):
            return 'welcome ' +user['name']
        else:
            flash('wrong credentials')
            
            
            

    return render_template('login.html')


@app.route('/register',methods=['POST','GET'])
def register_user():
    if request.method=='POST':
        #get form data
        name=request.form['name']
        email=request.form['email']
        phone_number=request.form['phone_number']
        password1=request.form['password']
        password2=request.form['Confirm_password']
        password=generate_password_hash(password1)
        


        if password1 != password2:
            flash('password mismatch')
            
        else:
            try:
                db=connect_db()
                users=db.execute('SELECT * FROM auth WHERE email=? AND phone_number=? ',(email,phone_number)).fetchall() 
                if users:
                    flash('user already exists')
                    return redirect('/')   
                    
                else:
                    #insert data into database
                    db.execute('INSERT INTO auth(name,email,phone_number,password) VALUES (?,?,?,?)',(name,email,phone_number,password))
                    db.commit()
                    db.close()
                    flash('registration successful')
                    
                    return redirect ('/')
            except Exception as e:
                flash(f'{e}')
                
            except sqlite3.IntegrityError as e:
                flash(f'{e}')
    return render_template('register.html')
if __name__=="__main__":
    app.run(debug=True)   

