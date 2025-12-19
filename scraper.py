import requests
from bs4 import BeautifulSoup
import time
import random
# 確保從 app 匯入正確的模型
from app import app, db, Movie, MovieDetail

def get_headers():
    # 使用英文語系抓取，確保 aria-label 是英文 (例如 "Watch Official Trailer")
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

def scrape_movie_details(session, detail_url):
    """
    爬取單一電影詳細頁面
    """
    # print(f"  -> Scraping details: {detail_url}") # 除錯用
    try:
        time.sleep(random.uniform(0.2, 0.8)) # 稍微縮短等待時間加速
        res = session.get(detail_url, headers=get_headers())
        
        if res.status_code != 200:
            return None
            
        soup = BeautifulSoup(res.text, 'html.parser')

        # 1. 抓取高畫質圖片 (優先抓 meta og:image)
        meta_img = soup.find("meta", property="og:image")
        poster = meta_img["content"] if meta_img else ""

        # 2. [改進版] 抓取預告片連結
        # 邏輯：搜尋所有 <a>，找出 href 包含 '/video/' 且 aria-label 包含 'trailer' (不分大小寫)
        trailer_url = ""
        # 先抓所有連結
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href']
            label = link.get('aria-label', '').lower()
            
            # 判斷條件：連結要是影片類，且標籤要有 trailer 關鍵字
            if '/video/' in href and 'trailer' in label:
                # 組合完整網址 (IMDb 連結通常是相對路徑)
                trailer_url = f"https://www.imdb.com{href}"
                break # 找到第一個就跳出
        
        # 如果還是沒找到，試試看另一種常見結構 (aria-label="Play trailer")
        if not trailer_url:
             play_btn = soup.select_one('a[aria-label*="trailer"]')
             if play_btn and play_btn.get('href'):
                 trailer_url = f"https://www.imdb.com{play_btn['href']}"

        # 3. 簡介
        desc_tag = soup.select_one('[data-testid="plot"]')
        description = desc_tag.text.strip() if desc_tag else "No description available."

        # 4. 導演、演員、類型
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
        # 1. 確保資料表被清空
        try:
            # 刪除舊資料
            db.session.query(MovieDetail).delete()
            db.session.query(Movie).delete()
            db.session.commit()
            print("Old data cleared.")
        except Exception as e:
            db.session.rollback()
            # 如果因為資料表不存在而報錯，這裡會忽略，交由 create_all 處理
            print(f"Note on clear DB: {e}")

        # 2. 爬取並寫入
        count = 0
        for item in movie_items:
            # 測試時可以只抓前 5 部，確認 Trailer 正常後再全抓
            # if count >= 5: break 
            
            try:
                # --- 基本資訊 ---
                title_tag = item.select_one('h3.ipc-title__text')
                full_title_text = title_tag.text.strip() if title_tag else "Unknown"
                
                rank_num = 0
                title_text = full_title_text
                if '. ' in full_title_text:
                    rank_str, title_text = full_title_text.split('. ', 1)
                    rank_num = int(rank_str)
                else:
                    # 嘗試另一種排名抓法
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

                # 預設小圖
                img_tag = item.select_one('img.ipc-image')
                temp_poster = img_tag.get('src', '') if img_tag else ""

                # --- 進入詳細頁面 ---
                details_data = scrape_movie_details(session, detail_url)
                
                final_poster = details_data['poster'] if (details_data and details_data['poster']) else temp_poster
                final_trailer = details_data['trailer'] if details_data else ""
                
                # --- 寫入 DB ---
                movie = Movie(
                    rank_num=rank_num,
                    title=title_text,
                    year=year,
                    duration=duration,
                    rating=rating_score,
                    poster_url=final_poster,
                    detail_url=detail_url,
                    trailer_url=final_trailer # 這裡是關鍵
                )
                db.session.add(movie)
                db.session.flush() # 取得 ID

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