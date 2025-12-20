## 1. 題目發想
IMDb (Internet Movie Database) 是個知名的電影網站，專門提供權威的評分與排名，但個人使用上感覺網站資訊量太繁雜，難以在單一頁面快速瀏覽、篩選並獲取關鍵資訊。
特別是如果想要觀看預告片需要點擊好幾層才能到達。

剛好以前在大一基於自己興趣有做過 IMDb 的網頁專案，當時單純使用 html、css、js 做出簡單的靜態網頁，這學期希望藉由資料庫這堂課的機會，能完善以前的專案，修改原本網頁，加上爬蟲以及資料庫系統，打造更接近現實生活中的電影網站。



## 2、3. 功能說明與成品功能描述
本專案在開發一個**整合爬蟲技術、Flask、mySQL**的電影資訊平台。
先透過爬蟲程式爬取 IMDb Top 250 網站，將資料轉化存放到資料庫，最後透過前端呈現。


### Crawler 部分
- **單獨爬蟲程式**：將爬蟲部分獨立出來一個 python程式，爬取 IMDb Top 250 列表。
- **資料持久化**：將爬取資料存入 MySQL 資料庫，建立table `top_movies` 與 `movie_details`
- `top_movies` : 爬取 top 列表，主要抓取每個電影的詳細資料 url
- `movie_details` : 進入每一部電影的詳細頁面 (Detail Page)，抓取圖片、導演、演員


### Frontend 跟 UI
前端分為5個部分:
(1)	Navigation bar
支援片名搜尋以及依「排名」、「評分 (高→低)」、「年份 (新→舊)」等條件篩選、排序。

(2)	電影輪播:
使用 Swiper.js，輪流播放電影海報，隨圖片切換會更新對應的電影資訊
(3)	電影卡片及詳細資訊
滑鼠放上去有放大特效，點擊卡片會出現彈窗，進一步顯示電影的詳細資料，另外有 watch trailer 按鈕可導向到 IMDb 的預告片網址
(4)	Footer
模仿 IMDb 的 footer
(5)	統計圖
使用 **Chart.js** 繪製長條圖，已「5年一個區間」進行統計，視覺化圖表

---

## 4. 實作技術


| 類別 | 技術 / 工具 | 說明 |
| :--- | :--- | :--- |
| **Backend** | **Python Flask** | python 的 Web 框架 |
| **Database** | **MySQL** | 儲存電影資料。 |
| **Crawler** | **Requests + BeautifulSoup4** | 發送 HTTP request 與解析 HTML DOM |
| **Frontend** | **HTML + Jinja2** | 前端頁面 |
| **Styling** | **SCSS (SASS)** | 幫助撰寫 CSS  |
| **Libraries** | **Swiper.js / Chart.js** | 輪播功能跟數據圖表。 |

### 系統架構圖
### 檔案結構
```
imdb-project/
├── app.py                 # Flask 主程式 (路由、資料庫連線)
├── scraper.py             # 爬蟲程式(爬取 IMDb 然後 寫到MySQL)
├── static/                
│   ├── style/               
│   │   └── style.css      
│   │   └── style.scss     
│   └── js/                
│       └── app.js         # frontend JS (Swiper.js等)
└── templates/             # Flask 預設的 HTML 模板資料夾
    └── index.html         # 預設頁面 
    └── dashboard.html     # 圖表頁面
```
