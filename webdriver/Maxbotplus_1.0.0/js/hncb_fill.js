const storage = chrome.storage.local;
var settings = null;
var inputInterval = null;

function hncb_main(settings) {
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
    let all_row = $("input[name='IDNO']");
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
                console.log("input value:" + $(this).val());
                if($(this).val()=="") {
                    if(user_guess_string_array[current_index].length) {
                        $(this).val(user_guess_string_array[current_index]);
                        is_text_sent = true;
                    }
                } else {
                    is_text_sent = true;
                }
            }
        });
    }

    if(is_text_sent) {
        console.log("start focus");
        document.querySelector("#TrxCaptchaKey").focus();
    }

    return is_text_sent;    
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
        inputInterval= setInterval(() => {
            hncb_main(settings);
        }, 200);
    } else {
        //console.log('maxbot status is not ON');
    }
});
