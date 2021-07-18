$('.slider').slick({
    centerMode: true,
    centerPadding: '5%',
    speed: 1500,
    infinite: true,
    autoplay:true, // 自動再生を設定
    autoplaySpeed:1500, // スライド切り替えの時間を設定
    dots:true, // インジケーターを表示
    slidesToShow: 6,
    slidesToScroll: 6,
    responsive: [{
         breakpoint: 768,
              settings: {
                   slidesToShow: 3,
                   slidesToScroll: 3,
         }
    },{
         breakpoint: 480,
              settings: {
                   slidesToShow: 2,
                   slidesToScroll: 2,
              }
         }
    ]
});

$(document).on('ready', function() {
    $(".regular").slick({
      autoplay: true,
      speed: 3000,
      autoplaySpeed: 3000,
      dots: true,
    });
  });