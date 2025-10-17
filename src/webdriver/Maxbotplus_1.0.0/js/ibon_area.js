const storage = chrome.storage.local;
var settings = null;

//console.log("start ibon area");

// price row.
$("table.table > tbody > tr.disabled").remove();
$("table.table > tbody > tr.sold-out").remove();
$("div.map > div > img").remove();
$("footer").remove();

var $tr=$("table.table > tbody > tr[onclick]");
//console.log("$tr.length:"+$tr.length);
if($tr.length==1) {
	//console.log("$tr.html:"+$tr.html());
	$tr.click();
}

function ibon_area_ready(settings) {
    let area_keyword_array = [];
    if(settings) {
        if(settings.area_auto_select.area_keyword.length > 0) {
            if(settings.area_auto_select.area_keyword!='""') {
                area_keyword_array = JSON.parse('[' +  settings.area_auto_select.area_keyword +']');
            }
        }
    }
    //let target_area = [];

    let target_row=null;
    let all_row = $("table.table > tbody > tr[onclick]");
    if (all_row.length > 0)
    {
        if (all_row.length == 1) {
            // single select.
            target_row=all_row;
        } else {
            // multi select.
            try {
                all_row.each(function ()
                {
                    //console.log(all_row.index(this));
                    let is_match_keyword = false;

                    if(area_keyword_array.length) {
                        let html_text=$(this).text();
                        //console.log("html:"+html_text);

                        // TOOD: multi item matched, need sort.
                        for (let i = 0; i < area_keyword_array.length; i++) {
                            // target_area = get_target_area_with_order(settings, matched_block);
                            //console.log("area_keyword:"+area_keyword_array[i]);

                            if(area_keyword_array[i].indexOf(" ")>-1) {
                                // TODO: muti keywords with AND logic.
                            } else {
                                // single keyword.
                                if(html_text.indexOf(area_keyword_array[i])>-1) {
                                    is_match_keyword = true;
                                    target_row=$(this);
                                    break;
                                }
                            }
                        }
                    } else {
                        if(all_row.index(this)==0) {
                            is_match_keyword = true;
                            target_row=$(this);
                        }
                    }

                    //console.log("is_match_keyword:"+is_match_keyword);
                    if(is_match_keyword) {
                        throw {};
                    }
                });
            } catch { }
        }
        if(target_row) {
            //console.log("found target, clicking");
            // click fail on sandbox world.
            //target_row.click();
            let done_div="<div style='display:none' id='maxbot'>"+ target_row.attr("id") +"</div>";
            $("body").append(done_div);
        }
    } else {
        location.reload();
    }
}

function ibon_area_clean_exclude(settings)
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
        $("table.table > tbody > tr").each(function ()
        {
            let html_text=$(this).text();
            //console.log("html:"+html_text);
            if(html_text.indexOf(exclude_keyword_array[i])>-1) {
                $(this).remove();
            }
        });
    }
}


function ibon_area_main() {
	let reload=false;
	let $tr=$("table.table > tbody > tr[onclick]");
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
    } else {
        ibon_area_clean_exclude(settings);
        ibon_area_ready(settings);
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
