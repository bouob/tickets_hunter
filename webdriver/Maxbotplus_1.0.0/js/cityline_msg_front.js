function begin()
{
    let settings = JSON.parse($("#settings").html());
    let status = $("#status").html();
    //console.log("msg");
    //console.log(settings);
    //console.log(status);

    $("#settings").remove();
    $("#status").remove();

    let cityline_queue_retry = true;
    if(settings) {
        cityline_queue_retry = settings.cityline.cityline_queue_retry;
    }

    if(status=='ON' && cityline_queue_retry) {
        setInterval(() => {
            if (typeof remainTime !== "undefined") {
                remainTime = 0;
            }
        }, 3000);
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

