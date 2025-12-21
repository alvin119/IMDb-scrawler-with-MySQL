from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from collections import Counter 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/imdb_movies'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
        from scraper import scrape_imdb
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

@app.route('/scrape')
def manual_scrape():
    from scraper import scrape_imdb
    scrape_imdb()
    return "Scraped & Updated Successfully!"
@app.route('/dashboard')
def dashboard():
    movies = Movie.query.with_entities(Movie.year).all()
    
    years = []
    for m in movies:
        try:
            
            y = int(m.year)
            years.append(y)
        except:
            continue
            
    bins = Counter()
    for year in years:
        start_year = (year // 5) * 5
        range_label = f"{start_year}-{start_year + 4}"
        bins[range_label] += 1

    sorted_items = sorted(bins.items(), key=lambda x: int(x[0].split('-')[0]))
    
    labels = [item[0] for item in sorted_items] 
    values = [item[1] for item in sorted_items] 

    return render_template('dashboard.html', labels=labels, values=values)
if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all() 
    app.run(debug=True)