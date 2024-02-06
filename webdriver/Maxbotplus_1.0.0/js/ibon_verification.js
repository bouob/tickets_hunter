const storage = chrome.storage.local;
var settings = null;

function ibon_verification_main() {
    let user_guess_string_array = [];
    if(settings) {
        if(settings.advanced.user_guess_string.length > 0) {
            if(settings.advanced.user_guess_string!='""') {
                user_guess_string_array = JSON.parse('[' +  settings.advanced.user_guess_string +']');
            }
        }
    }

    let target_row=null;
    let all_row = $("div.editor-box > div > div.form-group > input[type='text']");
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
        ibon_verification_main();
    } else {
        console.log('no status found');
    }
});
