const storage = chrome.storage.local;
var settings = null;
var myInterval = null;

$("div.masthead-wrap").remove();

function date_clean()
{
    remove_list=['Currently Unavailable',
        'Sale ended on 20',
        'Sold out',
        '暫停販售',
        ':00 截止',
        '已售完',
        '00に発売終了',
        '販売一時中止',
        '完売した'
    ];
    for (let i = 0; i < remove_list.length; i++) {
        $("#gameList td:contains('"+ remove_list[i] +"')").each(function ()
        {
            $(this).parent().remove();
        });
    }
}

function date_keyword(settings)
{
    let date_keyword_array = [];
    if(settings) {
        if(settings.date_auto_select.date_keyword.length > 0) {
            if(settings.date_auto_select.date_keyword!='""') {
                date_keyword_array = JSON.parse('[' +  settings.date_auto_select.date_keyword +']');
            }
        }
    }
    //console.log(date_keyword_array);
    let target_date=null;
    if(date_keyword_array.length) {
        for (let i = 0; i < date_keyword_array.length; i++) {
            let query_string = "#gameList td:contains('"+ date_keyword_array[i] +"')";
            if(date_keyword_array[i]=="") {
                query_string = "#gameList td"
            }
            let matched_block=[];
            $(query_string).each(function ()
            {
                matched_block.push($(this));
            });
            target_date = get_target_date_with_order(settings, matched_block);
            if (target_date) {
                console.log("match keyword:" + date_keyword_array[i]);
                break;
            }
        }
    } else {
        let query_string = "#gameList td";
        let matched_block=[];
        $(query_string).each(function ()
        {
            matched_block.push($(this));
        });
        target_date = get_target_area_with_order(settings, matched_block);
    }
    
    if (target_date) {
        let button_tag = "button";
        const currentUrl = window.location.href; 
        const domain = currentUrl.split('/')[2];
        if(domain=="ticketmaster.sg") {
            button_tag = "a";
        }

        let link = target_date.parent().find(button_tag).attr("data-href");
        if (link) {
            //console.log("link: " + link);
            clearInterval(myInterval);
            window.location.href = link;
        }
    } else {
        //console.log("not target_date found.")
    }
}

function date_main(settings)
{
    myInterval = setInterval(() => {
        //console.log("date_mode:"+ settings.date_auto_select.mode);
        //console.log("date_keyword:"+ settings.date_auto_select.date_keyword);
        date_keyword(settings);
    }, 200);
}

function date_auto_reload()
{
    let reload=false;
    
    let button_tag = "button";
    const currentUrl = window.location.href; 
    const domain = currentUrl.split('/')[2];
    if(domain=="ticketmaster.sg") {
        button_tag = "a";
    }

    const query_string = "#gameList "+button_tag;
    if ($(query_string).length) {
        date_clean();
        if ($(query_string).length) {
            if (settings)
            {
                date_main(settings);
            }
        } else {
            reload=true;
        }
    } else {
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
        date_auto_reload();
    } else {
        console.log('no status found');
    }
});
