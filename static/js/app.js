const header = document.querySelector("header");

window.addEventListener("scroll", () => {
  if (window.scrollY > 50) {
    header.classList.add("scrolled");
  } else {
    header.classList.remove("scrolled");
  }
});

const heroTitle = document.getElementById("hero-title");
const heroYear = document.getElementById("hero-year");
const heroRating = document.getElementById("hero-rating");
const heroDesc = document.getElementById("hero-desc");
const heroBtn = document.getElementById("hero-trailer-btn");

// 只有當輪播物件在時，才更新函式
if (heroTitle) {
    function updateHeroContent(slide) {
        if (!slide) return;
        
        const title = slide.getAttribute("data-title");
        const year = slide.getAttribute("data-year");
        const rating = slide.getAttribute("data-rating");
        const desc = slide.getAttribute("data-desc");
        const trailer = slide.getAttribute("data-trailer");

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
        }, 200); 
    }

    // 只有當 Swiper 在時才 initialize Swiper
    if (document.querySelector(".mySwiper")) {
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
    }
}

// movie modal
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

if (modal && movieCards.length > 0) {
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

            if(mTitle) mTitle.innerText = title;
            if(mYear) mYear.innerText = year;
            if(mRating) mRating.innerText = rating;
            if(mGenres) mGenres.innerText = genres;
            if(mDirector) mDirector.innerText = director;
            if(mStars) mStars.innerText = stars;
            if(mDesc) mDesc.innerText = desc;
            if(mPoster) mPoster.src = poster;

            modal.style.display = "block";
        });
    });
}

const trailerLinks = document.querySelectorAll(".trailer-link");
trailerLinks.forEach(link => {
    link.addEventListener("click", (e) => {
        e.stopPropagation(); 
    });
});

// 處理收藏連結
const favLinks = document.querySelectorAll(".fav-icon a");
favLinks.forEach(link => {
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