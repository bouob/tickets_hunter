function setTopAlertReadCookie() {
    var expires = new Date();
    expires.setTime(expires.getTime() + 24 * 60 * 60 * 1000);
    document.cookie = 'readMsg=true;expires=' + expires.toUTCString();
}

//====================== TOP NEWS ======================
function initTopAlert() {
    var status = getUserStatus("readMsg");

    if (status.session !== "true" && status.cookie !== "true") {
        $("#topAlert").show();
        return true;
    }
    return false;
}

function getUserStatus(name) {
    var sessionStatus, cookieStatus;
    try {
        sessionStatus = sessionStorage.getItem(name);
    } catch (e) {
        cookieStatus = getCookie(name);
    }

    return {
        "session": sessionStatus,
        "cookie": cookieStatus,
    };
}
//====================== CLOSE ALERT ======================
jQuery(document).ready(function() {
    jQuery('.close-alert').on('click', function() {
        if (sessionStorage) {
            sessionStorage.setItem('readMsg', true);
        } else {
            setTopAlertReadCookie();
        }
        jQuery('#topAlert').hide();
        jQuery(this).off('click');
    });
    initTopAlert();
});
//====================== BACK-TO-TOP BUTTON ======================
jQuery(document).ready(function() {
    var a = 220,
        b = 400;
    jQuery(window).scroll(function() {
        jQuery(this).scrollTop() > a ? jQuery(".back-to-top").fadeIn(b) : jQuery(".back-to-top").fadeOut(b)
    }), jQuery(".back-to-top").click(function(a) {
        return a.preventDefault(), jQuery("html, body").animate({
            scrollTop: 0
        }, b), !1
    });
});

function navbarReset() {
    $(".nav-menu li").removeClass("active");
    if (location.pathname.match(new RegExp("/activity"))) {
        $("li[id=activity]").addClass("active");
    } else if (location.pathname.match(new RegExp("/tour"))) {
        $("li[id=tour]").addClass("active");
    } else if (location.pathname.match(new RegExp("/partner"))) {
        $("li[id=partner]").addClass("active");
    } else if (location.pathname.match(new RegExp("/news"))) {
        $("li[id=news]").addClass("active");
    } else if (location.pathname.match(new RegExp("/faq"))) {
        $("li[id=faq]").addClass("active");
    } else if (location.pathname.match(new RegExp("/order"))) {
        $("li[id=order]").addClass("active");
    }
}


function byteLength(str) {
  // returns the byte length of an utf8 string
  var s = str.length;
  for (var i=str.length-1; i>=0; i--) {
    var code = str.charCodeAt(i);
    if (code > 0x7f && code <= 0x7ff) s++;
    else if (code > 0x7ff && code <= 0xffff) s+=2;
    if (code >= 0xDC00 && code <= 0xDFFF) i--; //trail surrogate    
  }
  return s;
}
