from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from collections import Counter # 新增這個 import 用來計算數量

app = Flask(__name__)

# 配置 MySQL 連線
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/imdb_movies'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 定義 ORM 模型 (保持不變) ---
class Movie(db.Model):
    __tablename__ = 'top_movies'
    id = db.Column(db.Integer, primary_key=True)
    rank_num = db.Column(db.Integer)
    title = db.Column(db.String(255))
    year = db.Column(db.String(10))
    duration = db.Column(db.String(20))
    rating = db.Column(db.String(10))
    poster_url = db.Column(db.Text)
    detail_url = db.Column(db.Text)
    trailer_url = db.Column(db.Text)
    details = db.relationship('MovieDetail', backref='movie', uselist=False, cascade="all, delete-orphan")

class MovieDetail(db.Model):
    __tablename__ = 'movie_details'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('top_movies.id'), unique=True)
    description = db.Column(db.Text)
    director = db.Column(db.String(255))
    stars = db.Column(db.Text)
    genres = db.Column(db.String(255))

# --- 路由設定 ---

@app.route('/')
def index():
    # 資料庫初始化檢查
    if Movie.query.count() == 0:
        from scraper import scrape_imdb
        print("Database empty, starting initial scrape...")
        scrape_imdb()
    
    # 1. 取得搜尋參數
    query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'rank') # 預設依排名排序

    # 2. 基礎查詢
    sql_query = Movie.query

    # 3. 搜尋過濾 (搜尋片名)
    if query:
        sql_query = sql_query.filter(Movie.title.ilike(f'%{query}%'))

    # 4. 排序邏輯
    if sort_by == 'year_desc':
        sql_query = sql_query.order_by(Movie.year.desc())
    elif sort_by == 'year_asc':
        sql_query = sql_query.order_by(Movie.year.asc())
    elif sort_by == 'rating_desc':
        sql_query = sql_query.order_by(Movie.rating.desc())
    else: # default rank
        sql_query = sql_query.order_by(Movie.rank_num)

    movies = sql_query.all()
    
    # 5. Swiper 資料：改為傳遞完整的 Movie 物件，以便在前端顯示資訊
    # 取前 10 部有海報的電影作為精選
    swiper_movies = [m for m in movies if m.poster_url][:10]
    
    return render_template('index.html', movies=movies, swiper_movies=swiper_movies, search_query=query, current_sort=sort_by)

@app.route('/scrape')
def manual_scrape():
    from scraper import scrape_imdb
    scrape_imdb()
    return "Scraped & Updated Successfully!"
@app.route('/dashboard')
def dashboard():
    # 1. 取出所有電影的年份
    movies = Movie.query.with_entities(Movie.year).all()
    
    # 2. 資料處理：清洗與分組
    years = []
    for m in movies:
        try:
            # 資料庫存的是字串且可能包含雜訊，先轉成整數
            y = int(m.year)
            years.append(y)
        except:
            continue
            
    # 3. 建立 5 年區間的統計
    # 邏輯：(年份 // 5) * 5 可以得到該區間的起始年
    # 例如：1994 -> 區間起始 1990 (範圍 1990-1994)
    bins = Counter()
    for year in years:
        start_year = (year // 5) * 5
        range_label = f"{start_year}-{start_year + 4}"
        bins[range_label] += 1
    
    # 4. 排序資料 (讓圖表依照年份從小到大顯示)
    # 將 keys 轉回數字進行排序，然後再轉回字串
    sorted_items = sorted(bins.items(), key=lambda x: int(x[0].split('-')[0]))
    
    labels = [item[0] for item in sorted_items] # X軸: ['1920-1924', '1925-1929'...]
    values = [item[1] for item in sorted_items] # Y軸: [2, 5...]

    return render_template('dashboard.html', labels=labels, values=values)
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)