import os
import io
from flask import Flask, g, render_template, send_file, abort
import pymysql
import pymysql.cursors

app = Flask(__name__)

# 資料庫連線設定
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'scraper'
app.config['MYSQL_DB'] = 'scraper520db'
# 密碼從環境變數獲取，如果沒有則為空字串
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '1qaz2wsx')

def get_db_connection():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor # 返回字典形式的結果
        )
    return g.db

@app.teardown_appcontext
def close_db_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_all_posts():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = "SELECT id, tag, title, author, post_date, replies, views, thumbnail, url, created_at FROM posts"
        cursor.execute(sql)
        result = cursor.fetchall()
    return result

@app.route('/')
def index():
    posts = get_all_posts()
    return render_template('index.html', posts=posts)

def get_post_by_id(post_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = "SELECT id, tag, title, author, post_date, replies, views, thumbnail, url, created_at FROM posts WHERE id = %s"
        cursor.execute(sql, (post_id,))
        result = cursor.fetchone()
    return result

@app.route('/thumbnail/<int:post_id>')
def thumbnail(post_id):
    post = get_post_by_id(post_id)
    if post and post['thumbnail']:
        # 假設縮圖是 JPEG 格式。如果需要支援多種格式，可能需要額外欄位儲存 Content-Type
        return send_file(
            io.BytesIO(post['thumbnail']),
            mimetype='image/jpeg', # 預設為 JPEG，實際應根據儲存的圖片類型判斷
            as_attachment=False
        )
    else:
        # 如果找不到貼文或縮圖為空，返回 404 錯誤
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)