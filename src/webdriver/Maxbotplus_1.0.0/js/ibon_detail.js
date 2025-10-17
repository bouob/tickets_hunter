const storage = chrome.storage.local;
var settings = null;

function ibon_detail_ajax_done(game_info)
{
    let date_keyword_array = [];
    if(settings) {
        if(settings.date_auto_select.date_keyword.length > 0) {
            date_keyword_array = JSON.parse('[' +  settings.date_auto_select.date_keyword +']');
        }
    }

    let reload=false;
    let target_href = "";

    //console.log(game_info.Item);
    if(game_info.Item.GIHtmls.length) {
        // one of game able to buy.
        let one_can_buy = false;

        for (let i = 0; i < game_info.Item.GIHtmls.length; i++) {
            let rs = game_info.Item.GIHtmls[i];
            if(game_info.Item.GIHtmls.length==1) {
                // single row.
                if(rs.Href==null) {
                    reload=true;
                } else {
                    if(rs.CanBuy==false) {
                        reload=true;
                    } else {
                        one_can_buy = true;
                        target_href = rs.Href;
                    }
                }
                if(reload) {
                    break;
                }
            } else {
                // multi rows.
                if(settings) {
                    let is_match_row = false;
                    if(date_keyword_array.length) {
                        for (let j = 0; j < date_keyword_array.length; j++) {
                            // TOOD: multi item matched, need sort.
                            // target_area = get_target_area_with_order(settings, matched_block);

                            if(rs.ShowSaleDate.indexOf(date_keyword_array[j])>-1) {
                                is_match_row = true;
                            }
                            if(rs.GameInfoName.indexOf(date_keyword_array[j])>-1) {
                                is_match_row = true;
                            }
                            if(is_match_row) {
                                break;
                            }
                        }
                    } else {
                        // empty keyword.
                        is_match_row = true;
                    }
                    if(is_match_row) {
                        if(rs.Href!=null) {
                            if(rs.CanBuy!=false) {
                                one_can_buy = true;
                                target_href = rs.Href;
                                break;
                            }
                        }
                    }
                }
            }
        }

        if(!reload) {
            if(one_can_buy == false) reload=true;
        }

    }

    //console.log("reload:"+reload);
    //console.log("target_href:"+target_href);
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
        // goto target event.
        //console.log(target_href);
        if(target_href.length > 0) {
            location.href= "https://ticket.ibon.com.tw/" + target_href;
        }
    }
}

function ibon_event_status_check()
{
    const currentUrl = window.location.href; 
    const event_code = currentUrl.split('/')[5];
    //console.log(currentUrl);
    //console.log(event_code);
    if(event_code){
        let api_url = "https://ticketapi.ibon.com.tw/api/ActivityInfo/GetGameInfoList";
        dataJSON = {
            id: parseInt(event_code, 10),
            hasDeadline: true,
            SystemBrowseType: 0
        }
        $.ajax({
            url: api_url,
            data: JSON.stringify(dataJSON),
            type: "POST",
            dataType: "json",
            xhrFields: {
                withCredentials: true
            },
            headers: {
                "x-xsrf-token": getCookie("XSRF-TOKEN")
            },
            contentType: "application/json",
            success: function(returnData){
                ibon_detail_ajax_done(returnData);
                //console.log(returnData);
            },
            error: function(xhr, ajaxOptions, thrownError){
                //console.log(xhr.status);
                //console.log(thrownError);
            }
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
        console.log("start to ibon detail.");
        //console.log(document.cookie);
        //console.log(getCookie("XSRF-TOKEN"));
        ibon_event_status_check();
    } else {
        console.log('no status found');
    }
});
