from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from collections import Counter 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/imdb_movies'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my_secret_key_12345' 

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('top_movies.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    favorite_movies = db.relationship('Movie', secondary=favorites, backref='favorited_by')

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



@app.route('/')
def index():
    if Movie.query.count() == 0:
        from scraper_250 import scrape_imdb
        print("Database empty, starting initial scrape...")
        scrape_imdb()
    
    query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'rank') 

    sql_query = Movie.query

    if query:
        sql_query = sql_query.filter(Movie.title.ilike(f'%{query}%'))
    if sort_by == 'year_desc':
        sql_query = sql_query.order_by(Movie.year.desc())
    elif sort_by == 'year_asc':
        sql_query = sql_query.order_by(Movie.year.asc())
    elif sort_by == 'rating_desc':
        sql_query = sql_query.order_by(Movie.rating.desc())
    else: 
        sql_query = sql_query.order_by(Movie.rank_num)

    movies = sql_query.all()
    swiper_movies = [m for m in movies if m.poster_url][:10]
    
    return render_template('index.html', movies=movies, swiper_movies=swiper_movies, search_query=query, current_sort=sort_by)


# 註冊頁面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 檢查帳號有沒有存在
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        
        # 建立新user
        new_user = User(username=username, password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/add_favorite/<int:movie_id>')
@login_required
def add_favorite(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie not in current_user.favorite_movies:
        current_user.favorite_movies.append(movie)
        db.session.commit()
    return redirect(request.referrer or url_for('index')) 

@app.route('/remove_favorite/<int:movie_id>')
@login_required
def remove_favorite(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie in current_user.favorite_movies:
        current_user.favorite_movies.remove(movie)
        db.session.commit()
    return redirect(request.referrer or url_for('favorites'))

@app.route('/favorites')
@login_required
def favorites():
    user_favs = current_user.favorite_movies
    total_movies_count = Movie.query.count() 
    if total_movies_count == 0: total_movies_count = 250 # 避免除以零

    user_fav_count = len(user_favs)
    
    # 計算收藏數/總數
    progress = 0
    if total_movies_count > 0:
        progress = int((user_fav_count / total_movies_count) * 100)
    
    return render_template('favorites.html', movies=user_favs, progress=progress, count=user_fav_count, total=total_movies_count)


@app.route('/scrape')
def manual_scrape():
    from scraper import scrape_imdb
    scrape_imdb()
    return "Scraped & Updated Successfully!"

@app.route('/dashboard')
def dashboard():
    # Bar Chart
    movies = Movie.query.with_entities(Movie.year).all()
    years = []
    for m in movies:
        try:
            y = int(m.year)
            years.append(y)
        except:
            continue
    
    year_bins = Counter()
    for year in years:
        start_year = (year // 5) * 5
        range_label = f"{start_year}-{start_year + 4}"
        year_bins[range_label] += 1
    
    sorted_years = sorted(year_bins.items(), key=lambda x: int(x[0].split('-')[0]))
    year_labels = [item[0] for item in sorted_years] 
    year_values = [item[1] for item in sorted_years] 

    
    details = MovieDetail.query.with_entities(MovieDetail.genres).all()
    genre_counts = Counter()

    for d in details:
        if d.genres:
            genres_list = [g.strip() for g in d.genres.split(',')]
            genre_counts.update(genres_list)
    
    # 依數量多到少排序 
    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    
    # 現在先取前 12 名
    top_n = 12
    final_genres = sorted_genres[:top_n]
    if len(sorted_genres) > top_n:
        others_count = sum(item[1] for item in sorted_genres[top_n:])
        final_genres.append(('Others', others_count))

    genre_labels = [item[0] for item in final_genres]
    genre_values = [item[1] for item in final_genres]

    return render_template('dashboard.html', 
                           year_labels=year_labels, year_values=year_values,
                           genre_labels=genre_labels, genre_values=genre_values)

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all() 
    app.run(debug=True)