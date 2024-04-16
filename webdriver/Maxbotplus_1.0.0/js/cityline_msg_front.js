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
    if(auto_reload_page_interval < 0.1) {
        auto_reload_page_interval = 0.1;
    }

    if(status=='ON') {
        let target_interval = auto_reload_page_interval * 1000;
        setInterval(() => {
            $(".eventposter").off();
            $(".btn_cta").prop('disabled', false);
            if(location.href.indexOf('?loc=') > -1) {
                if(location.href.indexOf('%2F') > -1) {
                const myArray = url.split("lang=TW");
                if(myArray.length >=3) {
                    if(myArray[1]=="utsvInternet") {
                        let new_url = "https://event.cityline.com/utsvInternet/"+myArray[1]+"/home?lang=TW";
                        location.href = new_url;
                    }
                }
            }
            if (typeof setRetryUrl !== "undefined") { 
                setRetryUrl(window.location.href);
            }
            if (typeof goEvent !== "undefined") { 
                let is_need_goEvent = false;
                if(location.href.indexOf('home?') > -1) is_need_goEvent = true;
                if(location.href.indexOf('?loc=') > -1) is_need_goEvent = true;
                if(location.href.indexOf('lang=') > -1) is_need_goEvent = true;
                if(is_need_goEvent) {
                    //goEvent();
                    remainTime = 0;
                }
            } else {
                //$("#btn-retry-en-1").prop('disabled', false).trigger("click");
            }
        }, target_interval);
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
    let is_need_back = true;
    if(location.href.indexOf('home?') > -1) is_need_back = false;
    if(location.href.indexOf('?loc=') > -1) is_need_back = false;
    if(location.href.indexOf('lang=') > -1) is_need_back = false;
    if (is_need_back) {
        history.back();
    }
}

