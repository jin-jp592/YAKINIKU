from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
import os
from flask_session import Session
# import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' 
db = SQLAlchemy(app)

#SQLiteのDBテーブル情報

# class FLASKDB(db.Model):
#     __tablename__ = 'flask_table'

#     ID = db.Column(Integer, primary_key=True)
#     YOURNAME = db.Column(String(32))
#     AGE = db.Column(Integer)
#     TEXTS = db.Column(db.String(300), nullable=False)
#     LIST = db.Column(String(32))

# #DBの作成
# db.create_all()


@app.route("/")
def mypage():
    return render_template("mypage.html")

@app.route('/mypage', methods = ['POST'])
def bunsyou():
    if request.method == 'POST':
      yourname = request.form['yourname']
      age = request.form['age']
      texts = request.form['texts']
      list = request.form['list']
      flask = FLASKDB(YOURNAME=yourname, AGE=age, TEXTS=texts, LIST=list)

      db.session.add(flask)
      db.session.commit()
      db.session.close()
      FLASKDB_infos = db.session.query(FLASKDB.ID, FLASKDB.YOURNAME, FLASKDB.AGE, FLASKDB.TEXTS, FLASKDB.LIST).all()
      return render_template('mypage2.html', FLASKDB_infos=FLASKDB_infos, message = '登録完了')


@app.route('/call_rutin', methods=['GET', 'POST'])
def call_rutin():
    return render_template('tasl_index.html', error=None)


@app.route('/call_logout', methods=['GET', 'POST'])
def call_logout():
    return render_template('index.html', error=None)


@app.route("/call_mypage2")
def call_mypage2():
    return render_template("mypage.html", error=None)  

#python app立ち上げ

if __name__ == '__main__':
    
    app.run()



    # .YAKINIKU\Scripts\activate.bat
