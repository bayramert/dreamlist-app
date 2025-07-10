import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'  # Gerçek ortamda daha güvenli bir anahtar kullan

# MongoDB bağlantısı için ortam değişkenleri
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")  # Kubernetes servis adı muhtemelen mongo
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

# Eğer kullanıcı adı ve şifre yoksa mongo URI farklı olur, ona göre ayarla
if MONGO_USERNAME and MONGO_PASSWORD:
    mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
else:
    mongo_uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

client = MongoClient(mongo_uri)
db = client.dreamlist_db

# Ana sayfa: /home olarak açılır, giriş yoksa /login yönlendirilir
@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dreamlist'))

# Kayıt sayfası
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
            flash("Kullanıcı adı veya şifre yanlış!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# Çıkış yap
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Başarıyla çıkış yapıldı.", "info")
    return redirect(url_for('login'))

# Kullanıcı hayal listesi sayfası
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
    return render_template('dreamlist.html', dreams=dreams)

# Hayal silme işlemi
@app.route('/delete/<dream_id>')
def delete_dream(dream_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Sadece o kullanıcıya ait hayal silinsin diye kontrol ekleyelim
    username = session['username']
    db.dreams.delete_one({'_id': ObjectId(dream_id), 'username': username})
    flash("Hayal silindi.", "success")
    return redirect(url_for('dreamlist'))


if __name__ == "__main__":
    # debug=True hata detayları için (prod ortamda kapat)
    app.run(host="0.0.0.0", port=5000, debug=True)
