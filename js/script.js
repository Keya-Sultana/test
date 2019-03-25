$(document).ready(function () {
    //    Menu Responsive Js Start
    $(".menu-bar").click(function () {
        $("ul").slideToggle();
    });
    //    Menu Responsive Js End
    //    MagnificPopup Js Start
    $('.popup-portfolio').each(function () { // the containers for all your galleries
        $(this).magnificPopup({
            delegate: 'a', // the selector for gallery item
            type: 'image',
            gallery: {
                enabled: true
            }
        });
    });
    //    MagnificPopup Js End
    //    Owl Carosel Js Start
    $('.owl-carousel').owlCarousel({
        loop: true,
        margin: 10,
        responsiveClass: true,
        autoplay:true,
        navText:['<i class="fas fa-angle-left"></i>','<i class="fas fa-angle-right"></i>'],
        responsive: {
            0: {
                items: 1,
                nav: true
            },
            600: {
                items: 1,
                nav: false
            },
            1000: {
                items: 1,
                nav: true,
                loop: true
            }
        }
    })
    //    Owl Carosel Js End
});