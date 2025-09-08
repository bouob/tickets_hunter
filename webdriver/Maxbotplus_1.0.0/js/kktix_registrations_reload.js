const storage = chrome.storage.local;
var settings = null;
var myInterval = null;

function kktix_clean_exclude(settings)
{
    let exclude_keyword_array = [];
    if(settings) {
        if(settings.keyword_exclude.length > 0) {
            if(settings.keyword_exclude != '""') {
                exclude_keyword_array = JSON.parse('[' + settings.keyword_exclude +']');
            }
        }
    }

    for (let i = 0; i < exclude_keyword_array.length; i++) {
        $("div.ticket-unit").each(function ()
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


function kktix_force_auto_reload_by_timer()
{
    if(settings) {
        //console.log("auto reload for kktix");
        if(settings.advanced.kktix_account.length > 0) {
            let max_dwell_time = 120;
            if(settings) {
                max_dwell_time = settings.kktix.max_dwell_time;
            }
            if(max_dwell_time <= 10) {
                max_dwell_time = 10;
            }
            console.log('We are going to force reload after few seconeds.');
            setTimeout(function () {
                location.reload();
            }, max_dwell_time * 1000);
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
        
        kktix_force_auto_reload_by_timer();
        setTimeout(function () {
            kktix_clean_exclude(settings);
        }, 500);
    } else {
        //console.log('maxbot status is not ON');
    }
});
