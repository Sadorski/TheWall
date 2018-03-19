from flask import Flask, redirect, render_template, session, flash, request
from mysqlconnection import MySQLConnector
app = Flask(__name__)
import re, datetime, time, md5
app.secret_key = "penguins"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
mysql = MySQLConnector(app, 'thewall')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def reg():
    print "hello"
    print request.form['action']
    if request.form['action'] == 'register':
        print "hello"
        if len(request.form['first_name']) < 2 or (request.form['first_name'].isalpha()) != True:
            flash("letters only, at least 2 characters and that it was submitted")
            return redirect('/')

        if len(request.form['last_name']) < 2 or (request.form['last_name'].isalpha()) != True:
            flash("Letters only, at least 2 characters and that it was submitted")
            return redirect('/')
       
        if len(request.form['email']) < 1:
            flash("You will need to enter at least one digit for email address")
            return redirect('/')
        elif re.search('[0-9]', request.form['password']) is None:
            flash("your password should include at least one Number")
            return redirect('/')
        elif re.search('[A-Z]', request.form['password']) is None:
            flash("Your password should have one capital letter")
            return redirect('/')
        elif not EMAIL_REGEX.match(request.form['email']):
            flash("Invalid email address")
            return redirect('/')

        if len(request.form['password']) < 8:
            flash("Your password must be at least 8 characters long")
            return redirect('/')
        elif request.form['password'] != request.form['confirm']:
            flash("Your passwords do not match")
            return redirect('/')

        password = md5.new(request.form['password']).hexdigest()
        query = "INSERT INTO users(first_name, last_name, email, password, created_at, updated_at) VALUES(:first, :last, :email, :password, NOW(), NOW())"
        data = {
            "first": request.form['first_name'],
            "last": request.form['last_name'],
            "email": request.form['email'],
            "password": password,
        }
        user = mysql.query_db(query, data)
        session['first_name'] = user[0]['first_name']
        session['user_id'] = user[0]['id']
        return redirect ('/wall')
    elif request.form['action'] == 'login':
        password = md5.new(request.form['password']).hexdigest()
        email = request.form['email']
        query = "SELECT * FROM users where users.email = :email AND users.password = :password"
        data = {
            'email': email,
            'password': password
        }
        user = mysql.query_db(query, data)
        if len(user) > 0:
            session['first_name'] = user[0]['first_name']
            session['user_id'] = user[0]['id']
            
            return redirect('/wall')
        else:
            flash("Your username or password is incorrect")
            return redirect('/')
@app.route('/wall')
def wall():
    messages = mysql.query_db("SELECT * FROM messages ORDER BY created_at desc")
    users = mysql.query_db("SELECT * FROM users")
    comments = mysql.query_db("SELECT * FROM comments")

    return render_template('wall.html', messages=messages, users=users, comments=comments)

@app.route('/post', methods=['POST'])
def post():
    print "hello"

    if request.form['action'] == "message":
        if len(request.form['message']) < 1:
            flash("You must enter a message to submit it.")
            return redirect('/wall')
        else:
            query = "INSERT INTO messages(user_id, message, created_at, updated_at) VALUES(:user_id, :message, NOW(), NOW())"
            data = {
                "user_id": session['user_id'],
                "message": request.form['message']
            }
            mysql.query_db(query, data)
            return redirect('/wall')
    
    if request.form['action'] == "comment":
        if len(request.form['comment']) < 1:
            flash("You must enter a comment to submit it.")
            return redirect('/wall')
        else:
            query = "INSERT INTO comments(message_id, USER_id, comment, created_at, updated_at) VALUES(:message_id, :user_id, :comment, NOW(), NOW())"
            data = {
                "message_id": request.form['msgid'],
                "user_id": session['user_id'],
                "comment": request.form['comment']
            }
            mysql.query_db(query, data)
            return redirect('/wall')
    
    if request.form['action'] == "delete_message":
        print "hello"

        query = "SELECT TIMESTAMPDIFF(MINUTE, created_at, NOW()) AS diff FROM messages WHERE id = :mess_id"
        data = {
            "mess_id": request.form['delmsg']
        }
        timediff = mysql.query_db(query, data)
        if timediff[0]['diff'] > 30:
            print timediff
            flash("Its been 30 minutes, you cannot delete this message")
            return redirect ('/wall')
        else:
            query2 ="DELETE FROM comments WHERE message_id = :message_id"
            data2 = {
                "message_id": request.form['delmsg']
            }
            mysql.query_db(query2, data2)

            query3 = "DELETE FROM messages WHERE id = :msg_id"
            data3 = {
            "msg_id": request.form['delmsg'],
            }
            mysql.query_db(query3, data3)
            return redirect('/wall')

    if request.form['action'] == "delete_comment":
        print "hello"
        query = "SELECT TIMESTAMPDIFF(MINUTE, created_at, NOW()) AS diff FROM comments WHERE id = :com_id"
        data = {
            "com_id": request.form['delcom']
        }
        timediff = mysql.query_db(query, data)
        if timediff[0]['diff'] > 30:
            print timediff
            flash("Its been 30 minutes, you cannot delete this comment")
            return redirect ('/wall')
        else:
            query2 = "DELETE FROM comments WHERE id = :comment_id"
            data2 = {
                "comment_id": request.form['delcom'],
            }
            mysql.query_db(query2, data2)
            return redirect('/wall')

    
        
    

@app.route('/clear')
def clear():
    session.clear()
    return redirect('/')


app.run(debug=True)