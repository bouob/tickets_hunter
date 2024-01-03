const storage = chrome.storage.local;

$("footer").remove();

setTimeout(function () {
    $("div.banner-wrapper").remove();
    $("div.ticket-img-wrapper").remove();
}, 300);


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
            let reload=false;
            console.log(data.inventory.registerStatus);
            // IN_STOCK
            if(data.inventory.registerStatus=='OUT_OF_STOCK') {reload=true;}
            if(data.inventory.registerStatus=='COMING_SOON') {reload=true;}
            if(data.inventory.registerStatus=='SOLD_OUT') {reload=true;}
            //console.log(reload);
            if(reload) {location.reload();}
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

