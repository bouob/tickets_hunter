const storage = chrome.storage.local;
var settings = null;
var myInterval = null;

function kktix_clean_exclude(settings, register_info) 
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

function clean_sold_out_row(register_info)
{
    //console.log("clean_sold_out_row");

    let match_target = false;
    for (var key in register_info.inventory.ticketInventory) {
        if(register_info.inventory.ticketInventory[key]) {
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

        if(settings) {
            let settings_div="<div style='display:none' id='settings'>" + JSON.stringify(settings) + "</div>";
            $("body").append(settings_div);
            let register_info_div="<div style='display:none' id='register_info'>" + JSON.stringify(register_info) + "</div>";
            $("body").append(register_info_div);
            kktix_clean_exclude(settings, register_info);
            //kktix_area_keyword(settings, register_info);
        }
    }
}

function kktix_ajax_done(register_info)
{
    let reload=false;
    console.log(register_info.inventory.registerStatus);
    // IN_STOCK
    if(register_info.inventory.registerStatus=='OUT_OF_STOCK') {reload=true;}
    if(register_info.inventory.registerStatus=='COMING_SOON') {reload=true;}
    if(register_info.inventory.registerStatus=='SOLD_OUT') {reload=true;}
    //console.log(reload);
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
    else {
        $(function() {
            myInterval = setInterval(() => {
                clean_sold_out_row(register_info);
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
        kktix_event_status_check();
    } else {
        console.log('no status found');
    }
});
