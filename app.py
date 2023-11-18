import sqlite3
from flask import Flask, render_template, request,current_app,redirect,url_for,session
from functools import wraps
import smtplib
from email.message import EmailMessage
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

conn = sqlite3.connect('students.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS students (name TEXT, age INTEGER, email TEXT, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS DONORDETAILS(name TEXT,bloodgroup TEXT,email TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS BLOODAVAIL(BLOODGROUP TEXT,UNIT INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS NEED(HOSPITALNAME TEXT,HOSPITALID INTEGER ,BLOODGROUP TEXT,UNIT INTEGER,STATUS TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS ADMIN(ADMINNAME TEXT,ADMIN_ID INTEGER,ADMIN_EMAIL TEXT)')
conn.commit()
conn.close()


def send_email(subject, body, recipient_email, sender_email, sender_password):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function       
@app.route('/')
def index():
    return  redirect('/first')
@app.route('/first')
def first():
    return render_template("first.html")

@app.route('/login', methods=['GET','POST'])
def login():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        passwd = request.form['passwd']
        c.execute("SELECT * FROM students WHERE name=? OR email=?",(name,email))
        data = c.fetchone()
        if data:
            sregis = "already registered user please login"
            return render_template('login.html',sregis=sregis)
        else:
            send_email("SUCCESSFULLY REGISTERED","Dear "+ name + "You have successfully registered in the equality bloods community, expecting your active participation",email, "sathyaalh3@gmail.com", "ciwrjdwacdmauego")
            c.execute('INSERT INTO students VALUES (?, ?, ?,?)', (name, age, email,passwd))
            conn.commit()
            conn.close()
            sregis = "successfully registered please login"
            return render_template('login.html',sregis=sregis)
    else:
        return render_template('login.html')

app.config['DATABASE'] = 'students.db'
@app.route('/clear')
def clear_database():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students;')
    conn.commit()
    cursor.close()
    conn.close()
    return "register cleared"
@app.route('/cleardonord')
def cleardonord():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('DELETE FROM DONORDETAILS;')
    conn.commit()
    cursor.close()
    conn.close()
    return "donordetails cleared"
@app.route('/clearneed')
def clearneed():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('DELETE FROM NEED;')
    conn.commit()
    cursor.close()
    return "need table cleared"

@app.route('/show', methods=['GET','POST'])
def show():
    if session.get('logged_ina'):
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students")
        students = c.fetchall()
        c.execute('SELECT * FROM DONORDETAILS')
        donord = c.fetchall()
        c.execute("SELECT * FROM BLOODAVAIL")
        bloods = c.fetchall()
        c.execute("SELECT * FROM NEED")
        needs = c.fetchall()
        c.execute("SELECT * FROM ADMIN")
        admins = c.fetchall()
        conn.close()
        return render_template('show.html',students = students,donord=donord,bloods=bloods,needs=needs,admins=admins)
    else:
        return redirect(url_for('adminlogin'))

@app.route('/signin',methods=['GET','POST'])
def signin():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    if request.method=='POST':
        password = request.form['passwd']
        email = request.form['email']
        c.execute("SELECT * FROM students WHERE password=? AND email=?",(password,email))
        data = c.fetchone()
        c.close()
        if data:
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            send_email("LOGIN ACTIVITY","Dear Master There is a login activity on: "+formatted_datetime+" recorded in our EQUALITY BLOODS WEBSITE ",email, "sathyaalh3@gmail.com", "ciwrjdwacdmauego")
            session['logged_in'] = True
            return redirect('/home')
        else:
            sregis = "invalid credentials"
            return render_template('signin.html',sregis=sregis)
    else:
        return render_template('signin.html')
    
@app.route('/home')
@login_required
def home():
    return render_template('home.html')
@app.route('/donor',methods = ['GET','POST'])
@login_required
def donor():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        bloodgroup = request.form['bloodgroup']
        email = request.form['email']
        c.execute('INSERT INTO DONORDETAILS VALUES (?, ?, ?)', (name, bloodgroup, email,))
        conn.commit()
        c.execute('UPDATE BLOODAVAIL SET UNIT = UNIT+1 WHERE BLOODGROUP=?',(bloodgroup,))
        conn.commit()
        conn.close()
        return render_template('bill.html',name = name,bloodgroup = bloodgroup,email = email)
    else:
        return render_template('donor.html')
@app.route('/need',methods=['POST','GET'])
@login_required
def need():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    if request.method == 'POST':
        hosname = request.form['hosname']
        hosid = request.form['hosid']
        bgroup = request.form['bgroup']
        units = request.form['units']
        posi = "successfull"
        faili = "unsuccessfull"
        c.execute("SELECT UNIT FROM BLOODAVAIL WHERE BLOODGROUP=?",(bgroup,))
        d = c.fetchone()
        print(d,d[0],int(units))
        if d[0]>=int(units):
            newu = d[0]-int(units)
            c.execute("INSERT INTO NEED VALUES(?,?,?,?,?)",(hosname,hosid,bgroup,units,posi))
            c.execute("UPDATE BLOODAVAIL SET UNIT= ? WHERE BLOODGROUP= ?",(newu,bgroup,))
            conn.commit()
            conn.close()
            text1 = "request accepted successfully you will receive the stock in few minutes"
            return render_template('need.html',text1 = text1 )
        else:
            text1 = "The amount of units of blood you requested is unavailable right now sorry for the inconvinience"
            c.execute('INSERT INTO NEED VALUES(?,?,?,?,?)',(hosname,hosid,bgroup,units,faili))
            conn.commit()
            conn.close()
            return render_template('need.html',text1=text1)
    else:
        return render_template('need.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('signin'))
@app.route('/adminlogin',methods = ['POST','GET'])
def adminlogin():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    if request.method=='POST':
        adminname = request.form['adminname']
        adminid = request.form['adminid']
        c.execute('SELECT * FROM ADMIN WHERE ADMINNAME=? AND ADMIN_ID=?',(adminname,adminid))
        data = c.fetchone()
        c.close()
        if data:
            session['logged_ina'] = True
            return redirect('/adminhome')
        else:
            error = "invalid credentials"
            return render_template('adminlogin.html',error=error)
    else:
        return render_template('adminlogin.html')
@app.route('/adminlogout')
def adminlogout():
    session.clear()
    return redirect(url_for('adminlogin'))

@app.route('/adminhome')
def adminhome():
    if session.get('logged_ina'):
        return render_template('adminhome.html')
    else:
        return redirect(url_for('adminlogin'))

@app.route('/registrationdetails')
def registrationdetails():
    if session.get('logged_ina'):
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students")
        students = c.fetchall()
        conn.close()
        return render_template('REGISTRATION.html',students=students)
    else:
        return redirect(url_for('adminlogin'))
    
@app.route('/donordetails')
def donordetails():
    if session.get('logged_ina'):
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute('SELECT * FROM DONORDETAILS')
        donord = c.fetchall()
        conn.close()
        return render_template('donordetails.html',donord=donord)
    else:
        return redirect(url_for('adminlogin'))
@app.route('/bloodrequest')
def bloodrequest():
    if session.get('logged_ina'):
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("SELECT * FROM NEED")
        needs = c.fetchall()
        conn.close()
        return render_template('bloodrequest.html',needs=needs)
    else:
        return redirect(url_for('adminlogin'))
@app.route('/admindetails')
def admindetails():
    if session.get('logged_ina'):
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("SELECT * FROM ADMIN")
        admins = c.fetchall()
        conn.close()
        return render_template('admindetails.html',admins=admins)
    else:
        return redirect(url_for('adminlogin'))
@app.route('/bloodavail')
def bloodavail():
    if session.get('logged_ina'):
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("SELECT * FROM BLOODAVAIL")
        bloods = c.fetchall()
        conn.close()
        return render_template('bloodavail.html',bloods=bloods)
    else:
        return redirect(url_for('adminlogin'))

if __name__ == '__main__':
    app.run(debug=True)
