import os
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

# MongoDB bağlantısı için ortam değişkenleri
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
client = MongoClient(mongo_uri)
db = client.dreamlist_db

@app.route('/')
def index():
    return redirect(url_for('login'))

# Kullanıcı kayıt sayfası
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']      # formdaki 'email' ile eşleşiyor
        password = request.form['password']

        existing_user = db.users.find_one({'username': email})
        if existing_user:
            return "Kullanıcı zaten kayıtlı!"
        
        db.users.insert_one({'username': email, 'password': password})
        return redirect(url_for('login'))
    return render_template('register.html')

# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = db.users.find_one({'username': email, 'password': password})
        if user:
            session['username'] = email
            return redirect(url_for('dreamlist'))
        else:
            return "Kullanıcı adı veya şifre yanlış!"
    return render_template('login.html')

# Çıkış yap
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Kullanıcı hayal listesi (dreamlist)
@app.route('/dreamlist', methods=['GET', 'POST'])
def dreamlist():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']

    if request.method == 'POST':
        new_dream = request.form['dream']
        db.dreams.insert_one({'username': username, 'dream': new_dream})

    dreams = list(db.dreams.find({'username': username}))
    return render_template('dreamlist.html', dreams=dreams)

# Hayal sil
@app.route('/delete/<dream_id>')
def delete_dream(dream_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    db.dreams.delete_one({'_id': ObjectId(dream_id)})
    return redirect(url_for('dreamlist'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

