var myInterval = null;

function dom_ready()
{
    let ret=false;
    if($("#buyTicketBtn").length>0) {
        ret=true;
        if(myInterval) clearInterval(myInterval);

        (function () {
            console.log($("#buyTicketBtn").length);
            if($("#buyTicketBtn").length) {
                console.log("clicking");
                $("#buyTicketBtn").trigger("click");
                //go();
            }
        })();

    }
    console.log("dom_ready:"+ret);
    return ret;
}

if(!dom_ready()) {
    myInterval = setInterval(() => {
        dom_ready();
    }, 100);
}


