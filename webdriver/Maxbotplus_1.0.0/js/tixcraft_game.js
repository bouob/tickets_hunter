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
    if(settings.tixcraft.date_auto_select.date_keyword.length > 0) {
        date_keyword_array = JSON.parse('[' +  settings.tixcraft.date_auto_select.date_keyword +']');
    }
    //console.log(date_keyword_array);
    let target_date;
    if(date_keyword_array.length) {
        for (let i = 0; i < date_keyword_array.length; i++) {
            let query_string = "#gameList td:contains('"+ date_keyword_array[i] +"')";
            if(date_keyword_array[i]=="") {
                query_string = "#gameList td"
            }
            let matched_block=$(query_string);
            target_date = get_target_date_with_order(settings, matched_block);
            if (target_date.length) {
                console.log("match keyword:" + date_keyword_array[i]);
                break;
            }
        }
    } else {
        let query_string = "#gameList td";
        let matched_block=$(query_string);
        target_date = get_target_area_with_order(settings, matched_block);
    }
    
    if (target_date.length) {
        let link = target_date.parent().find("button").attr("data-href");
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
        //console.log("date_mode:"+ settings.tixcraft.date_auto_select.mode);
        //console.log("date_keyword:"+ settings.tixcraft.date_auto_select.date_keyword);
        date_keyword(settings);
    }, 200);
}

function date_auto_reload()
{
    if ($("#gameList button").length) {
        date_clean();
        if ($("#gameList button").length) {
            storage.get('settings', function (items)
            {
                if (items.settings)
                {
                    settings = items.settings;
                    date_main(settings);
                } else {
                    console.log('no settings found');
                }
            });

        } else {
            location.reload();
        }
    } else {
        location.reload();
    }
}

storage.get('status', function (items)
{
    console.log(items);
    if (items.status && items.status=='ON')
    {
        date_auto_reload();
    } else {
        console.log('no status found');
    }
});


