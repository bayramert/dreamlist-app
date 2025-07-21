import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'  # Gerçek ortamda güvenli anahtar kullan

# MongoDB bağlantısı için ortam değişkenleri
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))

mongo_uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
client = MongoClient(mongo_uri)
db = client.dreamlist_db

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = db.users.find_one({'username': email})
        if existing_user:
            flash("Kullanıcı zaten kayıtlı!", "danger")
            return redirect(url_for('register'))

        db.users.insert_one({'username': email, 'password': password})
        flash("Kayıt başarılı, giriş yapabilirsiniz.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

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
            flash("Kullanıcı adı veya şifre yanlış!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Başarıyla çıkış yapıldı.", "info")
    return redirect(url_for('login'))

@app.route('/dreamlist', methods=['GET', 'POST'])
def dreamlist():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    if request.method == 'POST':
        new_dream = request.form['dream']
        if new_dream.strip() != '':
            db.dreams.insert_one({'username': username, 'dream': new_dream})

    dreams = list(db.dreams.find({'username': username}))
    return render_template('detail.html', dreams=dreams)

@app.route('/delete/<dream_id>')
def delete_dream(dream_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    db.dreams.delete_one({'_id': ObjectId(dream_id), 'username': username})
    flash("Hayal silindi.", "success")
    return redirect(url_for('dreamlist'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
