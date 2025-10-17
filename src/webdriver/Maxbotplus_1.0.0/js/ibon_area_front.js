var myInterval = null;

function dom_ready()
{
    let ret=false;
    if($("#maxbot").length>0) {
    	let target_id = $("#maxbot").text();
    	//console.log(target_id);
        $("#maxbot").remove();
        ret=true;
        if(myInterval) clearInterval(myInterval);
        (function () {
            if(target_id) {
                console.log(target_id);
                console.log($("#"+target_id).text());
                //https://orders.ibon.com.tw/application/UTK02/UTK0201_000.aspx?PERFORMANCE_ID=B06PV2MC&PRODUCT_ID=B06PS1OC
                //https://orders.ibon.com.tw/application/UTK02/UTK0202_.aspx?PERFORMANCE_ID=B06PV2MC&GROUP_ID=&PERFORMANCE_PRICE_AREA_ID=B06PV2PH
                $("#"+target_id).trigger("click");
                onTicketArea(target_id);
            }
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
