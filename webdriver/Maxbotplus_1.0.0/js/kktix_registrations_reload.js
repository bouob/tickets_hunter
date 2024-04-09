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

function clean_sold_out_row(register_info, base_info)
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
            let base_info_div="<div style='display:none' id='base_info'>" + JSON.stringify(base_info) + "</div>";
            $("body").append(base_info_div);
            kktix_clean_exclude(settings);
            //kktix_area_keyword(settings, register_info);
        }
    }
}

function kktix_ajax_return_base_info(base_info, register_info)
{
    //console.log(base_info.eventData.order_qualifications);
    $(function() {
        myInterval = setInterval(() => {
            clean_sold_out_row(register_info, base_info);
        }, 200);
    });
}

function kktix_ajax_return_register_info(register_info)
{
    let reload=false;
    //console.log(register_info.inventory.registerStatus);
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
        // memory not able to release soon.
        if (auto_reload_page_interval < 0.23) {
            auto_reload_page_interval = 0.23;
        }
        const rootElement = document.documentElement;
        rootElement.remove();
        register_info=null;
        settings = null;
        myInterval = null;
        for (var key in window) {
            key=null;
            delete key;
        }        
        if(auto_reload_page_interval == 0) {
            //console.log('Start to reload now.');
            window.location.reload();
        } else {
            //console.log('We are going to reload after few seconeds.');
            setTimeout(function () {
                window.location.reload();
            }, auto_reload_page_interval * 1000);
        }
    }
    else {
        kktix_event_base_info(register_info);
        kktix_force_auto_reload_by_timer();
    }
}

function kktix_event_base_info(register_info)
{
    const currentUrl = window.location.href;
    const event_code = currentUrl.split('/')[4];
    //console.log(currentUrl);
    //console.log(event_code);
    if(event_code){
        let api_url = "https://kktix.com/g/events/"+ event_code +"/base_info";
        $.get( api_url, function() {
            //alert( "success" );
        })
        .done(function(data) {
            //alert( "second success" );
            kktix_ajax_return_base_info(data, register_info);
        })
        .fail(function() {
            //alert( "error" );
        })
        .always(function() {
            //alert( "finished" );
        });
    }
}

function kktix_event_register_info()
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
            kktix_ajax_return_register_info(data);
        })
        .fail(function() {
            //alert( "error" );
        })
        .always(function() {
            //alert( "finished" );
        });
    }
}

function kktix_force_auto_reload_by_timer()
{
    if(settings) {
        //console.log("auto reload for kktix");
        if(settings.advanced.kktix_account.length > 0) {
            let max_dwell_time = 120;
            if(settings) {
                max_dwell_time = settings.advanced.max_dwell_time;
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
        let kktix_status_api = false;
        if(settings) {
            kktix_status_api = settings.advanced.kktix_status_api;
        }
        if(kktix_status_api) {
            kktix_event_register_info();
        } else {
            kktix_force_auto_reload_by_timer();
        }
    } else {
        //console.log('maxbot status is not ON');
    }
});
