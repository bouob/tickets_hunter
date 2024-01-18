var myInterval = null;
//console.log("assign appear");

function kktix_area_keyword(settings, register_info) 
{
    let area_keyword_array = [];
    if(settings.area_auto_select.area_keyword.length > 0) {
        area_keyword_array = JSON.parse('[' +  settings.area_auto_select.area_keyword +']');
    }
    // console.log(area_keyword_array);
    let target_area = [];
    if(area_keyword_array.length) {
        for (let i = 0; i < area_keyword_array.length; i++) {
            let matched_block=[];

            $("div.ticket-unit").each(function ()
            {
                let html_text=$(this).text();
                if(html_text.indexOf(area_keyword_array[i])>-1) {
                    matched_block.push($(this));
                }
                target_area = get_target_area_with_order(settings, matched_block);
            });

            if (matched_block.length) {
                console.log("match keyword:" + area_keyword_array[i]);
                break;
            }
        }
    } else {
        let query_string = "div.ticket-unit";
        let matched_block=$(query_string);
        target_area = get_target_area_with_order(settings, matched_block);
    }

    if (target_area.length) {
        let first_node = target_area.find(":first-child");
        let link_id = first_node.attr("id");
        //console.log("link_id: " + link_id);
        if(link_id) {
            $('input[type=checkbox]').each(function() {
                //$(this).prop('checked', true);
                if(!$(this).is(':checked')) {
                    $(this).click();
                }
            });

            let seat_inventory_key=link_id.split("_")[1];
            let seat_inventory_number=register_info.inventory.seatInventory[seat_inventory_key];
            let ticket_number = settings.ticket_number;
            if(seat_inventory_number<ticket_number) {
                ticket_number=seat_inventory_number;
            }

            if(ticket_number>0) {
                /*
                let target_input = target_area.find("input");
                target_input.click();
                target_input.prop("value", ticket_number);
                let down = $.Event('keydown');
                down.key=""+ticket_number;
                target_input.trigger(down);

                let up = $.Event('keyup');
                up.key=""+ticket_number;
                target_input.trigger(up);
                */
                let add_button = target_area.find('button[ng-click="quantityBtnClick(1)"]');
                for(let i=0; i<ticket_number; i++) {
                    add_button.click();
                }

                let $next_btn = $('div.register-new-next-button-area > button');
                $next_btn.click();
            }
        }
    } else {
        console.log("not target_area found.")
    }
}

function begin()
{
    console.log("begin to next");
    $("div#ticket-wrap a[onclick]").click();
}

function dom_ready()
{
    let ret=false;
    if($("#done").length>0) {
        $("#done").remove();
        ret=true;
        if(myInterval) clearInterval(myInterval);
        begin();
    }
    console.log("dom_ready:"+ret);
    return ret;
}

if(!dom_ready()) {
    myInterval = setInterval(() => {
        dom_ready();
    }, 100);    
}
