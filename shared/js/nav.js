
;(function () {
    /**
     Sets .container-fluids min Width so that it doesn't get smaller than 
     either the header or the navigation bar, depending on which one is
     smaller.
     */

    var header = document.querySelector('.hero-unit');
    var headerWidth = header.offsetLeft + header.offsetWidth + 10 + "px";

    var nav = document.querySelector('.navbar ul.nav');
    var navWidth = nav.offsetLeft + nav.offsetWidth + 10 + "px";

    var minWidth = headerWidth > navWidth ? headerWidth : navWidth;

    document.querySelector('.container-fluid').style.minWidth = minWidth;
})();
