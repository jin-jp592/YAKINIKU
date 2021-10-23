from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import time
import os

app = Flask(__name__)
# データベースの設定(sqliteファイルのパスを指定)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yakiniku_user.db'
db = SQLAlchemy(app)


# Todoリストのモデルを定義
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
@app.route('/', methods=['POST', 'GET'])
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
            return redirect('/')
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
        return redirect('/')
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
            return redirect('/')
        except:
            return "タスクの編集中に問題が発生しました"
    else:
        return render_template('edit.html', task=task_to_edit)

# 完了
#@app.route('/check/<int:id>', methods=['GET', 'POST'])
#def complete(id):
    # 編集するタスクのIDを取得
    task_to_check = Todo.query.get_or_404(id)
    # POSTメソッドがきたら編集対象のIDのコンテンツを更新
    if request.method == 'POST':
        task_to_check.check = request.form['check']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "タスクの編集中に問題が発生しました"
    else:
        return render_template('check.html', task=task_to_check)




if __name__ == "__main__":
    # モデルからテーブルを作成(データベースファイルを最初に作るときだけ実行)
    #db.create_all()
    
    # アプリを起動(データベースファイルを最初に作るときはコメントアウトして実行しない)
    app.run(host="127.0.0.1", port=8080)