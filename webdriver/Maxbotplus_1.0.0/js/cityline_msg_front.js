function goEvent(){
    if(urlThrottler.indexOf('https://event.cityline.com/')>-1) {
        window.location.href = urlThrottler;
    } else {
        document.getElementById("multiple_tab_layout").innerHTML = 'start to retry';

        var ddsScheduler = undefined;
        var retryingMsg = "重試中...<br>Retrying...";
        var retryingMsg2 = "重試中... Retrying...";
        var enableAutoRetry = true;
        var remainTime = 10;
        var enableButtonTime = 7;
        
        document.getElementById("busy_zone").innerHTML = '<button id="btn-retry-en-1" class="btn_cta" type="button" onclick="javascript:goEvent()">請重試 Retry<span id="remainTime1"></span></button>';
        setTimeout(startCountDownTimer, 1000);
    }
    
}

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