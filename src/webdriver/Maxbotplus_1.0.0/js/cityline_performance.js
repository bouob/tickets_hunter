const storage = chrome.storage.local;
var settings = null;

function cityline_clean_exclude(settings)
{
    let exclude_keyword_array = [];
    if(settings) {
        if(settings.keyword_exclude.length > 0) {
            if(settings.keyword_exclude != '""') {
                exclude_keyword_array = JSON.parse('[' + settings.keyword_exclude +']');
            }
        }
    }

    let query_string = "div.price > div.form-check";
    for (let i = 0; i < exclude_keyword_array.length; i++) {
        $(query_string).each(function ()
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

function cityline_area_keyword(settings)
{
    let area_keyword_array = [];
    if(settings) {
        if(settings.area_auto_select.area_keyword.length > 0) {
            if(settings.area_auto_select.area_keyword!='""') {
                area_keyword_array = JSON.parse('[' +  settings.area_auto_select.area_keyword +']');
            }
        }
    }
    
    //console.log(area_keyword_array);
    let target_area = null;
    let matched_block=[];
    let query_string = "div.price > div.form-check";
    if(area_keyword_array.length) {
        for (let i = 0; i < area_keyword_array.length; i++) {
            $(query_string).each(function ()
            {
                let html_text=$(this).text();
                //console.log("html_text:"+html_text);
                if(html_text.indexOf('售罄')>-1) {
                  // do nothing.
                } else {
                  if(html_text.indexOf(area_keyword_array[i])>-1) {
                      matched_block.push($(this));
                  }
                }
                target_area = get_target_area_with_order(settings, matched_block);
            });

            if (matched_block.length) {
                console.log("match keyword:" + area_keyword_array[i]);
                break;
            }
        }
    } else {
        $(query_string).each(function ()
        {
            let html_text=$(this).text();
            //console.log("html_text:"+html_text);
            if(html_text.indexOf('售罄')>-1) {
              // do nothing.
            } else {
              matched_block.push($(this));
            }
        });
        target_area = get_target_area_with_order(settings, matched_block);
    }
    
    if (target_area) {
      target_area.find("input").click();
    } else {
        console.log("not target_area found.")
    }
}

function cityline_performance()
{
    cityline_clean_exclude(settings);
    //console.log("cityline_performance");
    if(settings) {
        cityline_area_keyword(settings);

        //$("#ticketType0").val(settings.ticket_number);
        let target_row=$("#ticketType0");
        let ticket_options = target_row.find("option");
        if (ticket_options.length)
        {
            let is_ticket_number_assign = false;
            if (settings.ticket_number > 0)
            {
                ticket_options.each(function ()
                {
                    if ($(this).val() == settings.ticket_number)
                    {
                        $(this).prop('selected', true);
                        is_ticket_number_assign = true;
                        return false;
                    }
                });
            }
            if (!is_ticket_number_assign)
            {
                ticket_options.last().prop('selected', true);
            }
        }
        
        if(settings.advanced.disable_adjacent_seat) {
          $('input[type=checkbox]:checked').each(function() {
              $(this).click();
          });
        }

        if($("#ticketType0").val()+"" != "0") {
            $('#expressPurchaseBtn').click();
        }
    }
    $("#commonWarningMessageModal").hide();

    setTimeout(() => {
      cityline_performance()
    }, "500");
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
        cityline_performance();
    } else {
        console.log('no status found');
    }
});

$("#s_footer").remove();
$("footer").remove();
