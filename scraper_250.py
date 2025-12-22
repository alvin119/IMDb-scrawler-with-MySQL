import requests
from bs4 import BeautifulSoup
import time
import random
import json
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
        time.sleep(random.uniform(0.5, 1.2)) 
        res = session.get(detail_url, headers=get_headers())
        
        if res.status_code != 200:
            return None
            
        soup = BeautifulSoup(res.text, 'html.parser')
        # 海報
        meta_img = soup.find("meta", property="og:image")
        poster = meta_img["content"] if meta_img else ""
        # trailer
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
        # 簡介
        desc_tag = soup.select_one('[data-testid="plot"]')
        description = desc_tag.text.strip() if desc_tag else "No description available."
        # 導演
        director_item = soup.select_one('li[data-testid="title-pc-principal-credit"] a')
        director = director_item.text.strip() if director_item else ""
        # 演員
        stars_tags = soup.select('a[data-testid="title-cast-item__actor"]')
        stars = ", ".join([s.text.strip() for s in stars_tags[:3]])
        
        # 類型
        genres_tags = soup.select('div[class="ipc-chip-list__scroller"] a')
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
    
    # --- 關鍵修改：改用 JSON 解析 ---
    # IMDb 把完整資料藏在 id="__NEXT_DATA__" 的 script 標籤中
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    if not script_tag:
        print("Error: Could not find __NEXT_DATA__ script tag. IMDb layout might have changed.")
        return

    try:
        data = json.loads(script_tag.string)
        # 解析 JSON 路徑找到電影列表
        # 路徑通常是 props -> pageProps -> pageData -> chartTitles -> edges
        edges = data['props']['pageProps']['pageData']['chartTitles']['edges']
        print(f"Found {len(edges)} movies in JSON data. Processing...")
    except KeyError as e:
        print(f"Error parsing JSON structure: {e}")
        return

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
        for edge in edges:
            try:
                node = edge['node']
                
                # --- 從 JSON 直接提取基本資訊 ---
                imdb_id = node['id']  # 例如 "tt0111161"
                rank_num = node.get('currentRank', count + 1)
                title_text = node['titleText']['text']
                year = str(node['releaseYear']['year'])
                
                # 評分資訊
                rating_score = "0.0"
                if 'ratingsSummary' in node and node['ratingsSummary']:
                    rating_score = str(node['ratingsSummary']['aggregateRating'])
                
                # 片長 (JSON 裡是秒數，轉成文字)
                duration = ""
                if 'runtime' in node and node['runtime']:
                    seconds = node['runtime']['seconds']
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    duration = f"{hours}h {minutes}m"

                # JSON 裡其實也有海報，可以當作備用
                json_poster = ""
                if 'primaryImage' in node and node['primaryImage']:
                    json_poster = node['primaryImage']['url']

                detail_url = f"https://www.imdb.com/title/{imdb_id}/"

                print(f"Processing {rank_num}. {title_text} ({year})...")

                # --- 進入詳細頁面爬取預告片與其他資訊 ---
                # 因為 JSON 裡通常沒有預告片連結，所以還是要進去爬
                details_data = scrape_movie_details(session, detail_url)
                
                final_poster = details_data['poster'] if (details_data and details_data['poster']) else json_poster
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