// 1. Sticky Navigation Bar Logic
const header = document.querySelector("header");

window.addEventListener("scroll", () => {
  if (window.scrollY > 50) {
    header.classList.add("scrolled");
  } else {
    header.classList.remove("scrolled");
  }
});

// --- Hero Section Logic (Swiper + Text Update) ---

// 綁定左側文字元素
const heroTitle = document.getElementById("hero-title");
const heroYear = document.getElementById("hero-year");
const heroRating = document.getElementById("hero-rating");
const heroDesc = document.getElementById("hero-desc");
const heroBtn = document.getElementById("hero-trailer-btn");

function updateHeroContent(slide) {
    if (!slide) return;
    
    // 從 active slide 的 data attribute 抓取資料
    const title = slide.getAttribute("data-title");
    const year = slide.getAttribute("data-year");
    const rating = slide.getAttribute("data-rating");
    const desc = slide.getAttribute("data-desc");
    const trailer = slide.getAttribute("data-trailer");

    // 更新 DOM (加入淡入淡出動畫效果會更好，這裡先做直接替換)
    heroTitle.style.opacity = 0;
    heroDesc.style.opacity = 0;
    
    setTimeout(() => {
        heroTitle.innerText = title;
        heroYear.innerText = year;
        heroRating.innerHTML = `<i class="fa-solid fa-star"></i> ${rating}`;
        heroDesc.innerText = desc;
        
        if (trailer && trailer !== "None") {
            heroBtn.href = trailer;
            heroBtn.style.display = "inline-block";
        } else {
            heroBtn.style.display = "none";
        }

        heroTitle.style.opacity = 1;
        heroDesc.style.opacity = 1;
    }, 200); // 配合 CSS transition
}

// 2. Swiper Initialization
var swiper = new Swiper(".mySwiper", {
  effect: "coverflow",
  grabCursor: true,
  centeredSlides: true,
  slidesPerView: "auto",
  coverflowEffect: {
    rotate: 50,
    stretch: 0,
    depth: 100,
    modifier: 1,
    slideShadows: true,
  },
  autoplay: {
    delay: 3000,
    disableOnInteraction: false,
  },
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  loop: true,
  on: {
    init: function () {
        const activeSlide = this.slides[this.activeIndex];
        updateHeroContent(activeSlide);
    },
    slideChange: function () {
        const activeSlide = this.slides[this.activeIndex];
        updateHeroContent(activeSlide);
    }
  }
});

const modal = document.getElementById("movie-modal");
const closeModalBtn = document.querySelector(".close-modal");
const movieCards = document.querySelectorAll(".movie-card");

const mTitle = document.getElementById("m-title");
const mYear = document.getElementById("m-year");
const mGenres = document.getElementById("m-genres");
const mRating = document.getElementById("m-rating");
const mDirector = document.getElementById("m-director");
const mStars = document.getElementById("m-stars");
const mDesc = document.getElementById("m-desc");
const mPoster = document.getElementById("m-poster");

movieCards.forEach(card => {
    card.addEventListener("click", function() {
        const title = this.getAttribute("data-title");
        const year = this.getAttribute("data-year");
        const rating = this.getAttribute("data-rating");
        const genres = this.getAttribute("data-genres");
        const director = this.getAttribute("data-director");
        const stars = this.getAttribute("data-stars");
        const desc = this.getAttribute("data-desc");
        const poster = this.getAttribute("data-poster");

        mTitle.innerText = title;
        mYear.innerText = year;
        mRating.innerText = rating;
        mGenres.innerText = genres;
        mDirector.innerText = director;
        mStars.innerText = stars;
        mDesc.innerText = desc;
        mPoster.src = poster;

        modal.style.display = "block";
    });
});

const trailerLinks = document.querySelectorAll(".trailer-link");
trailerLinks.forEach(link => {
    link.addEventListener("click", (e) => {
        e.stopPropagation(); 
    });
});

if (closeModalBtn) {
    closeModalBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });
}

window.addEventListener("click", (e) => {
    if (e.target == modal) {
        modal.style.display = "none";
    }
});
