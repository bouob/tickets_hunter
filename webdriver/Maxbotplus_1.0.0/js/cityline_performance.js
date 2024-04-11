const storage = chrome.storage.local;
var settings = null;

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
    //console.log("cityline_performance");
    if(settings) {
        cityline_area_keyword(settings);

        $("#ticketType0").val(settings.ticket_number);
        
        if(settings.advanced.disable_adjacent_seat) {
          $('input[type=checkbox]:checked').each(function() {
              $(this).click();
          });
        }
    }

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
