var myInterval = null;

function dom_ready()
{
    let ret=false;
    if($("#done").length>0) {
        $("#done").remove();
        ret=true;
        if(myInterval) clearInterval(myInterval);
        (function () {
            $("div#ticket-wrap a[onclick]").click();
        })();
    }
    //console.log("dom_ready:"+ret);
    return ret;
}

if(!dom_ready()) {
    myInterval = setInterval(() => {
        dom_ready();
    }, 100);
}
