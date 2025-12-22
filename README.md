# IMDb Top 250 電影爬蟲+mySQL+Flask
## 1. 題目發想
IMDb (Internet Movie Database) 是個知名的電影網站，專門提供權威的評分與排名，但個人使用上感覺網站資訊量太繁雜，難以在單一頁面快速瀏覽、篩選並獲取關鍵資訊。

特別是如果想要觀看預告片需要點擊好幾層才能到達。

剛好以前在大一基於自己興趣有做過 IMDb 的網頁專案，當時單純使用 html、css、js 做出簡單的靜態網頁，這學期希望藉由學校期末專案的機會，能完善以前的專案，修改原本網頁，加上爬蟲以及資料庫系統，打造更接近現實生活中的電影網站。


## 2、3. 功能說明與成品功能描述
本專案在開發一個**整合爬蟲技術、Flask、mySQL**的電影資訊平台。

先透過爬蟲程式(beautifulsoup為主)爬取 IMDb Top 250 網站，將資料轉化存放到資料庫，最後透過前端呈現。

爬蟲程式:
1. `scraper.py` :
    - 初版的爬蟲程式，只能爬前 25 個電影
    - 因為 IMDb 首頁是動態載入網頁，此方法直接取得 IMDb首頁的 HTML，只會有一開始的 25 個電影
3. `scraper_250.py` :
    - 可以爬全部 250 個電影。
    - 改成取得 IMDb 首頁其中的 JSON 檔，裡面會包含全部的 250 個電影

### Crawler 及 Database 部分
- **單獨爬蟲程式**：將爬蟲部分獨立出來一個 python程式，爬取 IMDb Top 250 列表。
- **資料持久化**：將爬取資料存入 MySQL 資料庫，建立 table `top_movies` 、 `movie_details` 、 `user` 、 `favorites`
#### tables
- `top_movies` : 爬取 top 列表，主要抓取每個電影的詳細資料 url
![螢幕擷取畫面 2025-12-22 181542](https://hackmd.io/_uploads/SJUvqc8mbx.png)
- `movie_details` : 進入每一部電影的詳細頁面 (Detail Page)，抓取圖片、導演、演員
![螢幕擷取畫面 2025-12-22 181532](https://hackmd.io/_uploads/r18Pc9L7be.png)
- `user` : 使用者資料
![螢幕擷取畫面 2025-12-22 181547](https://hackmd.io/_uploads/HJ8wqcUmbl.png)
- `favorites` : 使用者及對應的收藏
![螢幕擷取畫面 2025-12-22 181522](https://hackmd.io/_uploads/SJ8wccLXWl.png)


### Frontend 跟 UI
前端分為5個部分:
1. Navigation bar
    - 支援片名搜尋以及依「rank」、「newest year」、「oldest year」等條件排序
    - 後面分別為圖表、收藏清單、登入功能按鈕。
![螢幕擷取畫面 2025-12-22 180801](https://hackmd.io/_uploads/BkGlY9UXZg.png)
3. 電影輪播:
    - 使用 `Swiper.js`，輪流播放電影海報，隨圖片切換會更新對應的電影資訊
    ![螢幕擷取畫面 2025-12-22 180816](https://hackmd.io/_uploads/SJaZY5L7-l.png)
![螢幕擷取畫面 2025-12-22 180834](https://hackmd.io/_uploads/BJzQY9Lm-x.png)
4. 電影卡片及詳細資訊
    - 滑鼠放上去有放大特效，點擊卡片會出現彈窗，進一步顯示電影的詳細資料，另外有 watch trailer 按鈕可導向到 IMDb 的預告片網址
    ![螢幕擷取畫面 2025-12-22 181058](https://hackmd.io/_uploads/BJ7HtcUX-x.png)
5. Footer
    - 模仿 IMDb 的 footer
    ![螢幕擷取畫面 2025-12-22 180917](https://hackmd.io/_uploads/BJW8Yc87be.png)
6. 統計圖
    - 使用 **Chart.js** 繪製長條圖跟圓餅圖
    - 長條圖以「5年一個區間」進行統計
    - 圓餅圖顯示前 12 多的電影種類，剩下為 other
    ![螢幕擷取畫面 2025-12-22 181338](https://hackmd.io/_uploads/Sy9kccLXWx.png)
    ![螢幕擷取畫面 2025-12-22 181342](https://hackmd.io/_uploads/Bk5199LXWg.png)
    


---

## 4. 實作技術及架構

### 使用到的技術
| 類別 | 技術 / 工具 | 說明 |
| :--- | :--- | :--- |
| **Backend** | **Python Flask** | python 的 Web 框架 |
| **Database** | **MySQL** | 儲存電影資料。 |
| **Crawler** | **Requests + BeautifulSoup4** | 發送 HTTP request 與解析 HTML DOM |
| **Frontend** | **HTML + Jinja2** | 前端頁面 |
| **Styling** | **SCSS (SASS)** | 幫助撰寫 CSS  |
| **Libraries** | **Swiper.js / Chart.js** | 輪播功能跟數據圖表。 |


### 檔案結構
```
imdb-project/
├── app.py                 # Flask 主程式 (路由、資料庫連線)
├── db.sql                 # 資料庫建置
├── scraper_250.py         # 爬蟲程式(爬取 IMDb 然後 寫到MySQL)
├── static/                
│   ├── style/               
│   │   └── style.css      
│   │   └── style.scss     
│   └── js/                
│       └── app.js         # frontend JS (Swiper.js等)
└── templates/             # Flask 預設的 HTML 模板資料夾
    └── index.html         # 預設頁面 
    └── dashboard.html     # 圖表頁面
    └── favorites.html     # 收藏頁面
    └── login.html         # 登入頁面
    └── register.html      # 註冊頁面
```

### 系統架構圖
![無標題](https://hackmd.io/_uploads/Hyu0IlQQZl.png) 


## 5. 自我評估
這次專題將原本的靜態網頁改成以 Flask 呈現前端及控制路由，以爬蟲抓取大量資料，並以 mySQL 作為資料庫。這次實作我覺得最困難的是爬蟲部分，原本只要爬取 Top 250 movies 的頁面，但因為此頁面的的圖片太模糊，導致需要改成先一一存取每個電影的詳細頁面連結到資料庫中，然後再進去每個詳細頁面抓取圖片，也因此增加了詳細頁面、trailer的功能。

礙於時間不足，有些功能尚未成功做完，希望將來能修改實現，並搭配 docker 進一步部屬到網頁上。
## 6. 執行方式
到 `app.py` 所在目錄並執行 `python app.py`
## 7. 相關連結
- GitHub : https://github.com/alvin119/IMDb-scrawler-with-MySQL
- Hackmd(此頁面) : https://hackmd.io/@M0Dqhe_USy-OrY2pBhL65g/Hy5ua1QXZg
