var myInterval = null;
function dom_ready()
{
    let ret=false;
    if($("#done").length>0) {
        $("#done").remove();
        ret=true;
        if(myInterval) clearInterval(myInterval);
        (function () {
            var btn_e = document.createEvent('MouseEvents');
            btn_e.initEvent('click', true, true );

            let btn1 = document.querySelector("div#ticket-wrap > a[onclick]");
            if(btn1 > 0) {
                console.log("trigger btn1 click");
                //btn1.click();
                let btn1 = document.querySelector("div#ticket-wrap > a[onclick]");
                btn1.dispatchEvent(btn_e);
            } else {
                let btn2 = document.querySelector("div#ticket-wrap > a[href]");
                if(btn2) {
                    console.log("trigger btn2 click");
                    //btn2.click();
                    btn2.dispatchEvent(btn_e);
                }
            }
        })();
    }
    console.log("dom_ready:"+ret);
    return ret;
}

myInterval = setInterval(() => {
    dom_ready();
}, 1000);
