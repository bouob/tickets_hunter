const storage = chrome.storage.local;
var settings = null;
var myInterval = null;

// price row.
$("#salesTable > tbody > tr.Soldout").remove();
$("div.footer").remove();

function kham_clean_exclude(settings)
{
	console.log("kham_clean_exclude");
	
    let exclude_keyword_array = [];
    if(settings) {
        if(settings.keyword_exclude.length > 0) {
            if(settings.keyword_exclude != '""') {
                exclude_keyword_array = JSON.parse('[' + settings.keyword_exclude +']');
            }
        }
    }

    for (let i = 0; i < exclude_keyword_array.length; i++) {
        $("#salesTable > tbody > tr").each(function ()
        {
            let html_text=$(this).text();
            let is_match_keyword=false;
            if(html_text.indexOf(exclude_keyword_array[i])>-1) {
                is_match_keyword=true;
            }
            if(is_match_keyword) {
                $(this).remove();
            }
        }
        );
    }
}

function kktix_area_main() {
	if(settings) {	
		kham_clean_exclude(settings);
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
        kktix_area_main();
    } else {
        //console.log('maxbot status is not ON');
    }
});


