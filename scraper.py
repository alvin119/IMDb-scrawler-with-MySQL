import requests
from bs4 import BeautifulSoup
import time
import random
from app import app, db, Movie, MovieDetail

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

def scrape_movie_details(session, detail_url):
    """
    爬取單一電影詳細頁面
    """
    try:
        time.sleep(random.uniform(0.2, 0.8)) 
        res = session.get(detail_url, headers=get_headers())
        
        if res.status_code != 200:
            return None
            
        soup = BeautifulSoup(res.text, 'html.parser')

        meta_img = soup.find("meta", property="og:image")
        poster = meta_img["content"] if meta_img else ""

        trailer_url = ""
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href']
            label = link.get('aria-label', '').lower()
            if '/video/' in href and 'trailer' in label:
                trailer_url = f"https://www.imdb.com{href}"
                break
        
        if not trailer_url:
             play_btn = soup.select_one('a[aria-label*="trailer"]')
             if play_btn and play_btn.get('href'):
                 trailer_url = f"https://www.imdb.com{play_btn['href']}"

        desc_tag = soup.select_one('[data-testid="plot"]')
        description = desc_tag.text.strip() if desc_tag else "No description available."

        director_item = soup.select_one('li[data-testid="title-pc-principal-credit"] a')
        director = director_item.text.strip() if director_item else ""
        
        stars_tags = soup.select('a[data-testid="title-cast-item__actor"]')
        stars = ", ".join([s.text.strip() for s in stars_tags[:3]])
        
        genres_tags = soup.select('[data-testid="genres"] a')
        genres = ", ".join([g.text.strip() for g in genres_tags])

        return {
            "poster": poster,
            "trailer": trailer_url,
            "desc": description,
            "director": director,
            "stars": stars,
            "genres": genres
        }

    except Exception as e:
        print(f"  Error scraping details for {detail_url}: {e}")
        return None

def scrape_imdb():
    print("Starting IMDb Full Scrape (List + Details)...")
    session = requests.Session()
    
    url = "https://www.imdb.com/chart/top/"
    
    try:
        response = session.get(url, headers=get_headers())
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching chart: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    movie_items = soup.select('li.ipc-metadata-list-summary-item')
    
    if not movie_items:
        print("No movie items found!")
        return

    print(f"Found {len(movie_items)} movies. Processing...")

    with app.app_context():
        try:
            db.session.query(MovieDetail).delete()
            db.session.query(Movie).delete()
            db.session.commit()
            print("Old data cleared.")
        except Exception as e:
            db.session.rollback()
            print(f"Note on clear DB: {e}")

        count = 0
        for item in movie_items:
            
            try:
                title_tag = item.select_one('h3.ipc-title__text')
                full_title_text = title_tag.text.strip() if title_tag else "Unknown"
                
                rank_num = 0
                title_text = full_title_text
                if '. ' in full_title_text:
                    rank_str, title_text = full_title_text.split('. ', 1)
                    rank_num = int(rank_str)
                else:
                    rank_tag = item.select_one('.ipc-signpost__text')
                    if rank_tag:
                         rank_num = int(rank_tag.text.replace('#', '').strip())

                link_tag = item.select_one('a.ipc-title-link-wrapper')
                detail_url = "https://www.imdb.com" + link_tag['href'] if link_tag else ""

                metadata_items = item.select('span.cli-title-metadata-item')
                year = metadata_items[0].text.strip() if len(metadata_items) > 0 else ""
                duration = metadata_items[1].text.strip() if len(metadata_items) > 1 else ""
                
                rating_tag = item.select_one('span.ipc-rating-star--rating')
                rating_score = rating_tag.text.strip() if rating_tag else "0.0"

                img_tag = item.select_one('img.ipc-image')
                temp_poster = img_tag.get('src', '') if img_tag else ""

                details_data = scrape_movie_details(session, detail_url)
                
                final_poster = details_data['poster'] if (details_data and details_data['poster']) else temp_poster
                final_trailer = details_data['trailer'] if details_data else ""
                
                movie = Movie(
                    rank_num=rank_num,
                    title=title_text,
                    year=year,
                    duration=duration,
                    rating=rating_score,
                    poster_url=final_poster,
                    detail_url=detail_url,
                    trailer_url=final_trailer 
                )
                db.session.add(movie)
                db.session.flush() 

                if details_data:
                    detail = MovieDetail(
                        movie_id=movie.id,
                        description=details_data['desc'],
                        director=details_data['director'],
                        stars=details_data['stars'],
                        genres=details_data['genres']
                    )
                    db.session.add(detail)

                count += 1
                print(f"Saved: {rank_num}. {title_text} | Trailer found: {'Yes' if final_trailer else 'NO'}")
                
                if count % 10 == 0:
                    db.session.commit()

            except Exception as inner_e:
                print(f"Error parsing movie index {count}: {inner_e}")
                continue

        try:
            db.session.commit()
            print("Successfully updated database!")
        except Exception as e:
            db.session.rollback()
            print(f"Error final commit: {e}")

if __name__ == "__main__":
    scrape_imdb()