function getHtmlDocName() {
    var pathname = location.pathname;
   var pathParts = pathname.split('/');
   if(pathParts.length >= 3) return pathParts[2];
   return null;
}

function goToCityline(){
   window.location="https://www.cityline.com";
}

function setRetryUrl(requestUrl){
   urlThrottler = requestUrl;
}

function startCountDownTimer() {
   setRetryUrl(window.location.href);
   
   if (enableAutoRetry){
      setRemainTime(remainTime); 
      if (ddsScheduler == undefined) {
         ddsScheduler = setInterval(function(){
            updateRemainTime();
         }, 1000);
      }
   }else{
      document.getElementById("remainTime1").innerHTML = '';
      $('#btn-retry-en-1').removeAttr('disabled');
   }
}

function setRemainTime(sec) {
   document.getElementById("remainTime1").innerHTML = '(' +sec+ ')';
}

function goEvent(){
   window.location.href = urlThrottler;
}

/*
function goEvent(){
    if(urlThrottler) {
        if(window.location.href.indexOf("https://msg.cityline.com/") > -1) {
            if(urlThrottler == "https://event.cityline.com") {
                if(window.location.href.indexOf("?") > -1) {
                    urlThrottler = "https://event.cityline.com/queue?" + window.location.href.split("?")[1];
                }
                document.getElementById("multiple_tab_layout").innerHTML = '';
                $('#busy_zone').removeClass('d-none')
                document.getElementById("busy_zone").innerHTML = '<div class="event"><button id="btn-retry-en-1" class="btn_cta" type="button" onclick="javascript:goEvent()">請重試 Retry<span id="remainTime1"></span></button></div>';

                var ddsScheduler = undefined;
                setRemainTime(remainTime); 
                if (ddsScheduler == undefined) {
                 ddsScheduler = setInterval(function(){
                    updateRemainTime();
                 }, 1000);
                }

            }
        }

        if(urlThrottler.indexOf("?") > -1) {
            document.getElementById("multiple_tab_layout").innerHTML = urlThrottler;
            window.location.href = urlThrottler;
        }
    }
}
*/

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
            //retry();
            //console.log("trigger");
            $(".btn_cta").prop('disabled', false).trigger("click");
        }, target_interval);
    }

    if(window.IsDuplicate()) {
        window.IsDuplicate = function () {return false;};
        document.getElementById("busy_zone").innerHTML = '<button id="btn-retry-en-1" class="btn_cta" type="button" disabled="disabled" onclick="javascript:goEvent()">請重試 Retry<span id="remainTime1"></span></button>';
        setTimeout(startCountDownTimer, 1000);
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
    console.log('set item');
    SetItem(ItemType.Local, "");
}, 100);

