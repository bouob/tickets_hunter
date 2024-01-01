const storage = chrome.storage.local;
var settings = null;
var myInterval = null;

$("div.masthead-wrap").remove();
if ($("#gameList button").length) {
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
        }
        );
    }
    if ($("#gameList button").length) {
        storage.get('settings', function (items)
        {
            if (items.settings)
            {
                settings = items.settings;
                myInterval = setInterval(() => {
                    //console.log("date_mode:"+ settings.tixcraft.date_auto_select.mode);
                    //console.log("date_keyword:"+ settings.tixcraft.date_auto_select.date_keyword);
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
                            if(settings.tixcraft.date_auto_select.mode=="from top to bottom")
                                target_date = $(query_string).first();
                            if(settings.tixcraft.date_auto_select.mode=="from bottom to top")
                                target_date = $(query_string).last();
                            if(settings.tixcraft.date_auto_select.mode=="center")
                                target_date = $(query_string).first();
                            if(settings.tixcraft.date_auto_select.mode=="random")
                                target_date = $(query_string).first();

                            if (target_date.length) {
                                //console.log("match keyword:" + date_keyword_array[i]);
                                break;
                            }
                        }
                    } else {
                        target_date = $("#gameList td").first();
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
                }, 200);
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