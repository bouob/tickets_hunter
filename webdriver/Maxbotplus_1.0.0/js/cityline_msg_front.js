function begin()
{
    let settings = JSON.parse($("#settings").html());
    let status = $("#status").html();
    //console.log("msg");
    //console.log(settings);
    //console.log(status);

    $("#settings").remove();
    $("#status").remove();

    let auto_reload_page_interval = 0.0;
    if(settings) {
        auto_reload_page_interval = settings.advanced.auto_reload_page_interval;
    }

    // too short to cause error.
    if(auto_reload_page_interval < 0.05) {
        auto_reload_page_interval = 0.1;
    }

    if(status=='ON') {
        let target_interval = auto_reload_page_interval * 1000;
        setInterval(() => {
            //retry();
            //console.log("trigger");
            $(".eventposter").off();
            if (typeof setRetryUrl !== "undefined") { 
                setRetryUrl(window.location.href);
            }
            $(".btn_cta").prop('disabled', false);
            //$(".btn_cta").prop('disabled', false).trigger("click");
            if (typeof goEvent !== "undefined") { 
                if(location.href.indexOf('home?') > -1) {
                    goEvent();
                }
            }
        }, target_interval);
    }

    if (typeof window.IsDuplicate !== "undefined") { 
        if(window.IsDuplicate()) {
            window.IsDuplicate = function () {return false;};
            document.getElementById("busy_zone").innerHTML = '<button id="btn-retry-en-1" class="btn_cta" type="button" disabled="disabled" onclick="javascript:goEvent()">請重試 Retry<span id="remainTime1"></span></button>';
            setTimeout(startCountDownTimer, 1000);
        }
    }
}

function dom_ready()
{
    //console.log("checking...");
    if($("#settings").length>0) {
        clearInterval(myInterval);
        begin();
    }
}

myInterval = setInterval(() => {
    dom_ready();
}, 100);

var ItemType = {
    Session: 1,
    Local: 2
};

var localStorageTabKey = 'my-application-browser-tab';
function SetItem(itemtype, val) {
 switch (itemtype) {
    case ItemType.Session:
       window.name = val;
       break;
    case ItemType.Local:
       setCookie(localStorageTabKey, val);
       break;
 }
}

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

setInterval(() => {
    SetItem(ItemType.Local, "");
}, 100);

function getHtmlDocName() {
    var pathname = location.pathname;
    var pathParts = pathname.split('/');
    if(pathParts.length >= 3) return pathParts[2];
    return null;
}

if(getHtmlDocName()==null) {
    history.back();
}
if (typeof goEvent !== "undefined") { 
    if(location.href.indexOf('home?') > -1) {
        //goEvent();
    } else {
        history.back();
    }
}

