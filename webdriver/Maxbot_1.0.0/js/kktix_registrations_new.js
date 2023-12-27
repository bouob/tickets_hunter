$("footer").hide();
function hideBannerAndImage() {
    $("div.banner-wrapper").hide();
    $("div.ticket-img-wrapper").hide();
    $('input[type=checkbox]').each(function() {
        $(this).prop('checked', true);
    });
}
setTimeout(hideBannerAndImage, 300);