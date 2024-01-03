const storage = chrome.storage.local;

$("div.description").remove();
$("footer").remove();

function kktix_event_redirect()
{
    const currentUrl = window.location.href; 
    const event_code = currentUrl.split('/')[4];
    //console.log(currentUrl);
    //console.log(event_code);
    if(event_code){
        let button_count = $("div.tickets > a.btn-point").length;
        console.log("length:"+button_count);
        if (button_count == 1) {
            let new_url = "https://kktix.com/events/"+ event_code +"/registrations/new";
            location.href=new_url;
        } else {
            // do nothing.
        }
    }
}

storage.get('status', function (items)
{
    if (items.status && items.status=='ON')
    {
        kktix_event_redirect();
    } else {
        console.log('no status found');
    }
});
