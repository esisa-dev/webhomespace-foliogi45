from flask import Flask ,render_template,request,redirect,session,url_for,flash
import hashlib
import os
import datetime
import crypt
import spwd
from urllib import response

app = Flask(__name__,template_folder='template/')

def generate_key(login):
    return hashlib.md5(str(login).encode('utf-8')).hexdigest()
app.secret_key='1234'

def searchUser(login,password):
    try:
        hashed_pw = spwd.getspnam(login).sp_pwd
        salt = hashed_pw[:hashed_pw.index('$', 3) + 1]
        encrypted_pw = crypt.crypt(password, salt)
        if encrypted_pw == hashed_pw:
            print(f"User {login} authenticated successfully.")
            return True
        else:
            print(f"Invalid password.")
            return True
    except KeyError:
        print(f"Invalid username or password.")
        return False


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login',methods=['Post'])
def login():

    login=request.form['login']
    password=request.form['password']

    if searchUser(login, password):
        app.secret_key=generate_key(login)
        path = os.path.expanduser('~'+login) # set default path to user directory
        items = get_directory_listing(path)
        return render_template('app.html', items=items, path=path)

    # if login=='Space' and password=='1234':  
    #     app.secret_key=generate_key(login)
    #     path = os.path.expanduser('~') # set default path to user directory
    #     items = get_directory_listing(path)
    #     return render_template('app.html', items=items, path=path)
    else:
        return render_template('login.html',error_auth="Invalid Authentifications")

def get_directory_listing(path):
    items = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            item_type = 'Directory'
            item_size = '-'
        else:
            item_type = 'File'
            item_size = os.path.getsize(item_path)
        mod_time = os.path.getmtime(item_path)
        mod_time_str = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
        items.append({'name': item, 'type': item_type, 'size': item_size, 'mod_time': mod_time_str})
    return items

@app.route('/show_directories', methods=['POST'])
def show_directories():
    path = request.form['path']
    items = get_directory_listing(path, only_directories=True)
    return render_template('app.html', items=items, path=path)


@app.route('/dir')
def view_directory():
    path = request.args.get('path')
    items = get_directory_listing(path)
    return render_template('app.html', items=items, path=path)


@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect(url_for('index'))

if __name__=='__main__':
    app.run(debug=True)


