const storage = chrome.storage.local;

var myInterval = null;

function clean_sold_out_row(data)
{
    console.log("clean_sold_out_row");

    let match_target = false;
    for (var key in data.inventory.ticketInventory) {
        if(data.inventory.ticketInventory[key]) {
            //console.log("key:"+key);
            if($("#ticket_"+key).length) {
                match_target = true;
                break;
            }
            
        }
    }
    //console.log("match_target:"+match_target);
    if(match_target) {
        $("footer").remove();
        $("div.banner-wrapper").remove();
        $("div.ticket-img-wrapper").remove();

        $("span.ticket-quantity[ng-if=\"!purchasableAndSelectable\"]").each(function ()
        {
            $(this).parent().parent().parent().remove();
        });
        clearInterval(myInterval);
    }
}

function kktix_ajax_done(data)
{
    let reload=false;
    console.log(data.inventory.registerStatus);
    // IN_STOCK
    if(data.inventory.registerStatus=='OUT_OF_STOCK') {reload=true;}
    if(data.inventory.registerStatus=='COMING_SOON') {reload=true;}
    if(data.inventory.registerStatus=='SOLD_OUT') {reload=true;}
    //console.log(reload);
    if(reload) {
        location.reload();
    } else {
        $(function() {
            myInterval = setInterval(() => {
                clean_sold_out_row(data);
            }, 200);
        });
    }
}

function kktix_event_status_check()
{
    const currentUrl = window.location.href; 
    const event_code = currentUrl.split('/')[4];
    //console.log(currentUrl);
    //console.log(event_code);
    if(event_code){
        let api_url = "https://kktix.com/g/events/"+ event_code +"/register_info";
        $.get( api_url, function() {
            //alert( "success" );
        })
        .done(function(data) {
            //alert( "second success" );
            kktix_ajax_done(data);
        })
        .fail(function() {
            //alert( "error" );
        })
        .always(function() {
            //alert( "finished" );
        });
    }
}


storage.get('status', function (items)
{
    if (items.status && items.status=='ON')
    {
        kktix_event_status_check();
    } else {
        console.log('no status found');
    }
});

