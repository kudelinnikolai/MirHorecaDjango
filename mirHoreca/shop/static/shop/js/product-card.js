$(document).ready(() => {
  $(".product-card__slider-main").slick({
    dots: false,
    infinite: true,
    arrows: true,
    fade: true,
    cssEase: "linear",
    autoplay: false,
    speed: 300,

    slidesToShow: 1,
    slidesToScroll: 1,
    asNavFor: ".product-card__slider-nav",
    adaptiveHeight: true,
  });
});

$(".product-card__slider-nav").slick({
  slidesToShow: 1,
  asNavFor: ".product-card__slider-main",
  centerMode: false,
  focusOnSelect: true,
  arrows: false,
  dots: false,
  infinite: false,
  swipe: false,
  touchMove: false,
});
