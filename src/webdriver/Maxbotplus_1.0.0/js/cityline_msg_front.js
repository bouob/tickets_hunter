function begin()
{
    let settings = JSON.parse($("#settings").html());
    let status = $("#status").html();
    //console.log("msg");
    //console.log(settings);
    //console.log(status);

    $("#settings").remove();
    $("#status").remove();

    // cityline_queue_retry feature removed (no longer functional)
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

