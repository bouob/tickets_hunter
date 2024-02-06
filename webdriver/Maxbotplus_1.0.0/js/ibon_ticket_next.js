var myInterval = null;
//console.log("assign appear");

function begin()
{
    console.log("begin to next");
    $("div#ticket-wrap a[onclick]").click();
}

function dom_ready()
{
    let ret=false;
    if($("#done").length>0) {
        $("#done").remove();
        ret=true;
        if(myInterval) clearInterval(myInterval);
        begin();
    }
    console.log("dom_ready:"+ret);
    return ret;
}

if(!dom_ready()) {
    myInterval = setInterval(() => {
        dom_ready();
    }, 100);    
}
