function begin()
{
    let settings = JSON.parse($("#settings").html());
    let status = $("#status").html();
    console.log("msg");
    console.log(settings);
    console.log(status);

    $("#settings").remove();
    $("#status").remove();

    let auto_reload_page_interval = 0.0;
    if(settings) {
        auto_reload_page_interval = settings.advanced.auto_reload_page_interval;
    }

    // too short to cause error.
    if(auto_reload_page_interval < 0.3) {
        auto_reload_page_interval = 0.3;
    }

    if(status=='ON') {
        setInterval(() => {
            retry();
        }, auto_reload_page_interval * 1000);
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