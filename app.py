import os
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

app = Flask("_name_")
app.secret_key = 'gizli_anahtar'

# Ortam değişkenlerini oku
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# 🔍 Debug çıktıları
print("🧪 DEBUG: Flask başlatılıyor...")
print("🧪 DEBUG: Ortam değişkenleri:", MONGO_USERNAME, MONGO_PASSWORD)

client = None
db = None
users_collection = None
dreams_collection = None

if MONGO_USERNAME and MONGO_PASSWORD:
    mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
    print(f"🧪 DEBUG: Mongo URI => mongodb://{MONGO_USERNAME}:@{MONGO_HOST}:{MONGO_PORT}/")
else:
    mongo_uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
    print(f"🧪 DEBUG: Mongo URI => {mongo_uri}")
    print("⚠  WARNING: Kimlik bilgileri eksik olabilir, bağlantı başarısız olabilir.")

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ DEBUG: MongoDB bağlantısı başarılı!")
    db = client['dreamlist_db']
    users_collection = db['users']
    dreams_collection = db['dreams']
    print("✅ DEBUG: Koleksiyonlar bağlandı.")
except ConnectionFailure as e:
    print(f"❌ CRITICAL ERROR: MongoDB'ye bağlanılamadı (ConnectionFailure): {e}")
except OperationFailure as e:
    print(f"❌ CRITICAL ERROR: MongoDB kimlik doğrulama hatası (OperationFailure): {e}")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Beklenmedik hata: {e}")
finally:
    if db is None:
        print("⚠  WARNING: Veritabanı bağlantısı kurulamadı.")

@app.route("/")
def home():
    if db is None:
        return "<h1>Veritabanı bağlantısı kurulamadı. Lütfen sunucu loglarını kontrol edin.</h1>"
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if db is None:
        return "Veritabanı bağlantısı yok. Kayıt yapılamıyor."
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if users_collection.find_one({"email": email}):
            return "Bu email zaten kayıtlı."
        users_collection.insert_one({"email": email, "password": password})
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if db is None:
        return "Veritabanı bağlantısı yok. Giriş yapılamıyor."
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = users_collection.find_one({"email": email, "password": password})
        if user:
            session["email"] = email
            return redirect(url_for("create"))
        else:
            return "Hatalı giriş."
    return render_template("login.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    if db is None:
        return "Veritabanı bağlantısı yok. Hayal oluşturulamıyor."
    if "email" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        hayal = request.form["dream"]
        dreams_collection.insert_one({"email": session["email"], "dream": hayal})
        return redirect(url_for("detail"))
    return render_template("create.html")

@app.route("/detail")
def detail():
    if db is None:
        return "Veritabanı bağlantısı yok. Detaylar görüntülenemiyor."
    if "email" not in session:
        return redirect(url_for("login"))
    user_dreams = dreams_collection.find({"email": session["email"]})
    return render_template("detail.html", dreams=user_dreams)

if "_name_" == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)