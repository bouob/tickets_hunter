const storage = chrome.storage.local;
var settings = null;

// price row.
$("table > tbody > tr.disabled").remove();
$("table > tbody > tr.sold-out").remove();
$("div.map > div > img").remove();
$("footer").remove();
let $tr=$("table > tbody > tr[onclick]");
//console.log("$tr.length:"+$tr.length);
if($tr.length==1) {
	//console.log("$tr.html:"+$tr.html());
	$tr.click();
}

function ibon_area_main() {
	let reload=false;
	let $tr=$("table > tbody > tr[onclick]");
	if($tr.length==0) {
		reload=true;
	}
    if(reload) {
        let auto_reload_page_interval = 0.0;
        if(settings) {
            auto_reload_page_interval = settings.advanced.auto_reload_page_interval;
        }
        if(auto_reload_page_interval == 0) {
            //console.log('Start to reload now.');
            location.reload();
        } else {
            console.log('We are going to reload after few seconeds.');
            setTimeout(function () {
                location.reload();
            }, auto_reload_page_interval * 1000);
        }
    }
}


storage.get('settings', function (items)
{
    if (items.settings)
    {
        settings = items.settings;
    }
});

storage.get('status', function (items)
{
    if (items.status && items.status=='ON')
    {
        ibon_area_main();
    } else {
        console.log('no status found');
    }
});
