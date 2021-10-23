import os
import time
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, jsonify, redirect, render_template, request, session
#from flask.ext.session import Session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
from datetime import datetime, date
import sqlite3
import difflib
from difflib import SequenceMatcher
import requests
import json

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


#「dialect+driver://<ユーザー名>:<パスワード>@<ホスト>:<ポート>/<データベース名>」


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

@app.route('/call_task_index', methods=['GET', 'POST'])
def call_task_index():
    return render_template('task_index.html')


@app.route('/call_mypage', methods=['GET', 'POST'])
def call_mypage():
    return render_template('mypage.html')

@app.route('/call_yakilog', methods=['GET', 'POST'])
def call_yakilog():
    return render_template('yakilog.html', error=None)

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
        return render_template("afterlogin.html")

    # Getメソッドにアクセスをしたか場合の処理
    else:
        return render_template("yakiregi.html", error=None)



@app.route("/login", methods=["GET", "POST"])
def login():

    #同じパソコンで違う人が使うときに違う人のまま使えないようにセッションを一度クリアする
    #その後違うアカウントで使えるようにする
    session.clear()

    # Postメソッドにアクセスをしたか場合の処理
    if request.method == "POST":

        conn = sqlite3.connect(DB_NAME)
        db = conn.cursor()

        # ユーザーネームの確認
        if not request.form.get("username"):
            return render_template('yakilog.html', error="ユーザーネームを入力してください！")

        # パスワードの確認
        elif not request.form.get("password"):
            return render_template('yakilog.html', error="パスワードを入力してください！")

        # Query database for username
        db.execute("SELECT * FROM users WHERE user_name = :user_name", {"user_name":request.form.get("username")})

        rows=db.fetchone()

        # 読み込んだやつが1つではないときと暗号化されたパスワードと入力されたパスワードを比較して違うとき
        if not len(rows) != 1 or not check_password_hash(rows[2], request.form.get("password")):
            return render_template('yakilog.html', error="ユーザーネームまたはパスワードが間違っています！")

        # どのユーザーがログインしたのかセッションを確立
        session["user_id"] = rows[0]

        session["user_name"] = rows[1]


        conn.commit()
        conn.close()

        return render_template("afterlogin.html")

    # GETメソッドで入ったとき
    else:
        return render_template("yakilog.html")
        
@app.route("/logout")
def logout():
    """Log user out"""

    #セッションをクリアする。
    session.clear()

    #インデックスにリダイレクトする。
    return redirect("/")










#タスク管理のデータベース作成




app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yakiniku_user.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    # テーブル名を設定
    __tablename__ = 'todos'
    # 作成するテーブルのカラムを定義
    # ID
    id = db.Column(db.Integer, primary_key=True)
    # コンテンツ
    content = db.Column(db.String(200), nullable=False)
    # 作成日
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    #期限
    due_date = db.Column(db.DateTime)
    #期限（文字列）
    date_due = db.Column(db.String(50))
    #完了
    #check = db.Column(db.Boolean)
    
   
    
    

# ルートにアクセスされたらindexページを開く
@app.route('/task_index', methods=['POST', 'GET'])
def task_index():
    # POSTメソッドで要求されたら
    if request.method == 'POST':
        # コンテンツを取得
        task_content = request.form['content']

        # 新しいタスクを作成
        new_task = Todo(content=task_content)

        #期限の追加
        new_task.date_due = request.form['due_date']



        
     
      
       


        try:
            # データベースに新しいタスクを登録しトップページにリダイレクト
            db.session.add(new_task)
            db.session.commit()
            return redirect('/task_index')
        except:
            return "フォームの送信中に問題が発生しました"
    # 要求がない場合は、タスクリストを日付順に並べて表示
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('task_index.html',tasks=tasks)

# 削除画面
@app.route('/delete/<int:id>')
def delete(id):
    # 削除するタスクのIDを取得
    task_to_delete = Todo.query.get_or_404(id)

    try:
        # 削除対象のタスクをDBから削除しトップページにリダイレクト
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/task_index')
    except:
        return '削除中に問題が発生しました'



# 編集画面
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def update(id):
    # 編集するタスクのIDを取得
    task_to_edit = Todo.query.get_or_404(id)
    # POSTメソッドがきたら編集対象のIDのコンテンツを更新
    if request.method == 'POST':
        task_to_edit.content = request.form['content']
        task_to_edit.date_due = request.form['due_date']

        try:
            db.session.commit()
            return redirect('/task_index')
        except:
            return "タスクの編集中に問題が発生しました"
    else:
        return render_template('edit.html', task=task_to_edit)















if __name__ == "__main__":
    # モデルからテーブルを作成(データベースファイルを最初に作るときだけ実行)
    #db.create_all()
    
    # アプリを起動(データベースファイルを最初に作るときはコメントアウトして実行しない)
    app.run(host="127.0.0.1", port=8080)