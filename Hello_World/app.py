from flask import Flask,redirect,url_for

app = Flask(__name__)   # Creating WSGI Application

@app.route('/')
def welcome():
    return 'Hello, Welcome to the Page!!'

@app.route('/success/<name>')
def login_success(name):
    return " You have successfully logged in, " + name

@app.route('/fail/<name>')
def login_fail(name):
    return "Sorry " + name + ", log in failed, please try again!"

@app.route('/login/<username>')
def login_check(username):
    page = ""
    if username == 'sandra':
        page = 'login_success'
    else:
        page = 'login_fail'
    return redirect(url_for(page,name=username))

if __name__ == '__main__':
    app.run(debug=True)