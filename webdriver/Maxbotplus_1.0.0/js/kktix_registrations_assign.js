var myInterval = null;
var checkboxInterval = null;
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

function kktix_agree()
{
    $('input[type=checkbox]:not(:checked)').each(function() {
        $(this).click();
        if(checkboxInterval) clearInterval(checkboxInterval);
    });
}

function kktix_area_keyword(settings)
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
    let target_area = null;
    let matched_block=[];
    let query_string = "div.ticket-unit";
    if(area_keyword_array.length) {
        for (let i = 0; i < area_keyword_array.length; i++) {
            $(query_string).each(function ()
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
        $(query_string).each(function ()
        {
            matched_block.push($(this));
        });
        target_area = get_target_area_with_order(settings, matched_block);
    }

    if (target_area) {
        let first_node = target_area.find(":first-child");
        let link_id = first_node.attr("id");
        //console.log("link_id: " + link_id);
        if(link_id) {
            let seat_inventory_key=link_id.split("_")[1];
            //console.log("seat_inventory_key:"+seat_inventory_key);
            let ticket_number = settings.ticket_number;

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

                let add_button = target_area.find('button[ng-click="quantityBtnClick(1)"]');
                for(let i=0; i<ticket_number; i++) {
                    add_button.click();
                }

                let auto_click_next_btn = settings.kktix.auto_press_next_step_button;

                if(auto_click_next_btn) {
                    if(is_verification_conditions_popup) {
                        auto_click_next_btn = false;
                        let is_text_sent = kktix_verification_conditions(settings);
                        if(is_text_sent) {
                            auto_click_next_btn = true;
                        }
                    }
                }

                let hide_other_row = false;
                if(auto_click_next_btn) {
                    let $next_btn = $('div.register-new-next-button-area > button');
                    if($next_btn) {
                        if($next_btn.length>1) {
                            $next_btn.last().click();
                        } else {
                            $next_btn.click();
                        }
                        hide_other_row = true;
                    }
                }

                // due to racing with web driver.
                if(hide_other_row) {
                    for (let i = 0; i < matched_block.length; i++) {
                        if(target_area!=matched_block[i])
                        {
                            matched_block[i].remove();
                        }
                    }
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
    $("#settings").remove();
    //console.log(settings);

    //kktix_area_keyword(settings);
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

const rootElement = document.documentElement;
if(rootElement) {
    if(!dom_ready()) {
        myInterval = setInterval(() => {
            dom_ready();
        }, 200);
        
        checkboxInterval= setInterval(() => {
            //console.log("kktix_agree")
            kktix_agree();
        }, 200);
    }
    $("footer").remove();
    $("div.banner-wrapper div.img-wrapper img").remove();
}


