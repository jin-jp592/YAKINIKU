from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3


app = Flask(__name__)

######  sessionを使用できるようにするための設定 ###
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

######  sessionの設定はここまで ###


# データベース作成の部分
DB_NAME = 'yakiniku_user'
conn = sqlite3.connect(DB_NAME)
db = conn.cursor()

# usersテーブルの作成
db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_name TEXT NOT NULL, user_password TEXT NOT NULL)')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/call_yakiregi', methods=['GET', 'POST'])
def call_yakiregi():
    return render_template('yakiregi.html', error=None)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # ユーザーがログアウトしないでセッションをそのままにした場合を想定して，すべてのセッションをクリアする
    session.clear()

    # Postメソッドにアクセスをしたか場合の処理
    if request.method == "POST":

        conn = sqlite3.connect(DB_NAME)
        db = conn.cursor()

        register_name = request.form.get("username")

        register_password = request.form.get("password")

        register_confirm_password = request.form.get("confirm-password")

        # ユーザー名が入力されていないときはメッセージを表示して関数から脱出
        if not register_name:
            return render_template('yakiregi.html', error="ユーザーネームを入力してください！")

        # パスワードが入力されていないときはメッセージを表示して関数から脱出
        elif not register_password:
            return  render_template('yakiregi.html', error="パスワードを入力してください！")

        # パスワードが一致しないときはメッセージを表示して関数から脱出
        elif register_password != register_confirm_password:
            return render_template('yakiregi.html', error="パスワードが一致していません！")

        # データベースに同じユーザー名の人が存在するときはメッセージを表示して関数から脱出
        else:
            db.execute("SELECT * FROM users WHERE user_name = :user_name",
                    {"user_name":register_name})

            user_exists = db.fetchone()

            if user_exists is not None:
                return render_template('yakiregi.html', error="ユーザーネームはすで登録済み！")

        hash_password = generate_password_hash(request.form.get("password"))

        # データベースにユーザーを登録
        db.execute("INSERT INTO users(user_name, user_password) VALUES (:user_name, :user_password)",
                     {"user_name":register_name, "user_password":hash_password})

        conn.commit()

        # データベースの「ユーザ－」テーブルに登録したデータを抽出する
        db.execute("SELECT * FROM users WHERE user_name = :user_name",
                    {"user_name":register_name})

        rows = db.fetchone()

        # セッションを開始する。
        #毎回rowという新しい表がかってにつくられて0番目にコピーして上書きされるので0行目の1列を参照
        session["user_id"] = rows[0]

        session["user_name"] = register_name

        # ホームページindex.htmlを表示させる
        return redirect("/")

    # Getメソッドにアクセスをしたか場合の処理
    else:
        return render_template("yakiregi.html", error=None)
