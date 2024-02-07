var myInterval = null;
//console.log("assign appear");

function kktix_verification_conditions(settings) 
{
    let is_text_sent = false;
    let user_guess_string_array = [];
    if(settings) {
        if(settings.advanced.user_guess_string.length > 0) {
            if(settings.advanced.user_guess_string!='""') {
                user_guess_string_array = JSON.parse('[' +  settings.advanced.user_guess_string +']');
            }
        }
    }

    let target_row=null;
    let all_row = $("div.control-group > div.controls > label > input[type='text']");
    if (all_row.length > 0 && user_guess_string_array.length > 0)
    {
        //console.log("input count:" + all_row.length);
        let travel_index=0;
        all_row.each(function ()
        {
            let current_index = all_row.index(this);
            //console.log("current_index:" + current_index);
            if(current_index+1 <= user_guess_string_array.length) {
                //console.log("input data:" + user_guess_string_array[current_index]);
                $(this).val(user_guess_string_array[current_index]);
                is_text_sent = true;
            }
        });
    }

    return is_text_sent;
}

function kktix_area_keyword(settings, base_info, register_info) 
{
    let area_keyword_array = [];
    if(settings) {
        if(settings.area_auto_select.area_keyword.length > 0) {
            if(settings.area_auto_select.area_keyword!='""') {
                area_keyword_array = JSON.parse('[' +  settings.area_auto_select.area_keyword +']');
            }
        }
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
            //console.log("seat_inventory_key:"+seat_inventory_key);
            let seat_inventory_number=register_info.inventory.seatInventory[seat_inventory_key];
            let ticket_number = settings.ticket_number;
            if(seat_inventory_number<ticket_number) {
                ticket_number=seat_inventory_number;
            }

            if(ticket_number>0) {
                /*
                // trigger events by jQuery.
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

                //console.log(base_info);
                let is_verification_conditions_popup = false;
                if(base_info && base_info.eventData.hasOwnProperty("order_qualifications")) {
                    //console.log(base_info.eventData.order_qualifications.length);
                    for (let i = 0; i < base_info.eventData.order_qualifications.length; i++) {
                        let rs = base_info.eventData.order_qualifications[i];
                        //console.log(rs);
                        for(let j=0; j < rs.conditions.length; j++) {
                            let rs_j = JSON.parse(rs.conditions[j]);
                            //console.log(rs_j);
                            if(rs_j.hasOwnProperty("ticket_ids")) {
                                //console.log(rs_j.ticket_ids.length);
                                for(let k=0; k < rs_j.ticket_ids.length; k++) {
                                    let rs_k = rs_j.ticket_ids[k]
                                    //console.log(rs_k);
                                    if(""+rs_k==seat_inventory_key) {
                                        is_verification_conditions_popup = true;
                                    }
                                }
                            }

                        }
                    }
                }

                let add_button = target_area.find('button[ng-click="quantityBtnClick(1)"]');
                for(let i=0; i<ticket_number; i++) {
                    add_button.click();
                }

                let auto_click_next_btn = true;
                
                if(is_verification_conditions_popup) {
                    auto_click_next_btn = false;
                    let is_text_sent = kktix_verification_conditions(settings);
                    if(is_text_sent) {
                        auto_click_next_btn = true;
                    }
                }

                if(auto_click_next_btn) {
                    let $next_btn = $('div.register-new-next-button-area > button');
                    $next_btn.click();
                }
            }
        }
    } else {
        console.log("not target_area found.")
    }
}

function begin()
{
    let settings = JSON.parse($("#settings").html());
    let base_info = JSON.parse($("#base_info").html());
    let register_info = JSON.parse($("#register_info").html());
    //console.log(settings);
    //console.log(register_info);
    kktix_area_keyword(settings, base_info, register_info);
}

function dom_ready()
{
    let ret=false;
    //console.log("checking...");
    if($("#settings").length>0) {
        ret=true;
        if(myInterval) clearInterval(myInterval);
        begin();
    }
    //console.log("dom_ready:"+ret);
    return ret;
}

if(!dom_ready()) {
    myInterval = setInterval(() => {
        dom_ready();
    }, 100);    
}
