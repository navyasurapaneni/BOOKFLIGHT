from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import json
import requests
app = Flask(__name__)
app.secret_key = 'a'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=bnz17181;PWD=Tj5kCYGEKITBhBaT",'','')
print("connected")

@app.route('/',methods=['POST','GET'])
def home():
    return render_template('home.html')

@app.route("/login", methods=["POST", 'GET'])
def login():
    global Userid
    msg = ''

    if request.method == "POST":
        EMAIL = request.form["email"]
        PASSWORD = request.form["psw"]
        sql = "SELECT * FROM REGISTER WHERE EMAIL=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, EMAIL)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['Loggedin'] = True
            session['id'] = account['USERNAME']
            Userid = account['USERNAME']
            session['USERNAME'] = account['USERNAME']
            session['USERID'] = account['USERID']
            msg = "logged in successfully !"
            return redirect(url_for('checkav', msg=msg))
        else:
            msg = "Incorrect username/password"
    return render_template('login.html', msg=msg)


@app.route("/register", methods=["POST", 'GET'])
def register():
    msg = ''
    if request.method == 'POST':
        USERNAME = request.form["username"]
        EMAIL = request.form["email"]
        PASSWORD = request.form["password"]
        sql = "SELECT * FROM REGISTER WHERE USERNAME = ? AND PASSWORD =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)  
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'You have already Registered!'
        else:
            sql ="SELECT count (*)  FROM REGISTER"
            stmt = ibm_db. prepare(conn,sql)
            ibm_db.execute(stmt)
            length = ibm_db.fetch_assoc(stmt)
            print(length)
            insert_sql = "INSERT INTO REGISTER VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, length['1']+1)
            ibm_db.bind_param(prep_stmt, 2, USERNAME)
            ibm_db.bind_param(prep_stmt, 3, EMAIL)
            ibm_db.bind_param(prep_stmt, 4, PASSWORD)
            ibm_db.execute(prep_stmt)
            msg = "You have successfully registered !"
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        msg = "Please fill out the form!"
        
    return render_template('register.html', msg=msg)  

@app.route("/avail", methods=["POST", 'GET'])
def  checkav():
    msg = ''
    if request.method == 'POST':
        DEPART = request.form["Depart"]
        RETURN = request.form["Return"]
        START = request.form["Start"]
        DESTINATION = request.form["Destination"]
        SELECTSEAT = request.form["seats"] 
        sql = "SELECT * FROM REGISTER WHERE USERID =" +str(session['USERID']) 
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)  
        data = ibm_db.fetch_assoc(stmt)
        print(data)

        sql = "SELECT * FROM BOOKFLIGHT WHERE USERID =" +str(session['USERID']) 
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)  
        myseat = ibm_db.fetch_tuple(stmt)
        print(myseat)

        if SELECTSEAT == myseat[6]  and START== myseat[4] and DESTINATION == myseat[5]:
            msg = 'The seat has been already booked!'
        else:
            insert_sql = "INSERT INTO BOOKFLIGHT VALUES (?,?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, data['USERID'] )
            ibm_db.bind_param(prep_stmt, 2, data['USERNAME'] ) 
            ibm_db.bind_param(prep_stmt, 3, DEPART )          
            ibm_db.bind_param(prep_stmt, 4, RETURN)
            ibm_db.bind_param(prep_stmt, 5, START)
            ibm_db.bind_param(prep_stmt, 6, DESTINATION)
            ibm_db.bind_param(prep_stmt, 7, SELECTSEAT)
            ibm_db.execute(prep_stmt)
            msg = "The seat is successfully booked !"          

    return render_template('availableflight.html',msg=msg) 

@app.route('/data')
def data():
    user1=[]
    sql1="SELECT * FROM BOOKFLIGHT"
    stmt1=ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    all_users = ibm_db.fetch_tuple(stmt1)
    print(all_users)
    while all_users!= False:
        user1.append(all_users)
        all_users = ibm_db.fetch_tuple(stmt1)
    print(user1)
    return render_template("data.html", rows=user1)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)                                                                                                                                                         
    return render_template('home.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080,debug=True)