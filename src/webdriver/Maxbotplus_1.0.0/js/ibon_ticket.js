const storage = chrome.storage.local;
var settings = null;

$("footer").remove();

function ibon_assign_ticket_number(ticket_number)
{
    let $main_table = $("table.table");
    if ($main_table.length > 0)
    {
        console.log("found main table");
        let $ticket_options = $main_table.find("select:first option");
        if ($ticket_options.length)
        {
            let is_ticket_number_assign = false;
            if (ticket_number > 0)
            {
                console.log("target ticket_number:"+ticket_number);
                $ticket_options.each(function ()
                {
                    if ($(this).val() == ticket_number)
                    {
                        $(this).prop('selected', true);
                        is_ticket_number_assign = true;
                        return false;
                    }
                }
                );
            }
            console.log("is_ticket_number_assign:"+is_ticket_number_assign);
            if (!is_ticket_number_assign)
            {
                $ticket_options.last().prop('selected', true);
            }
        }
    }
}

function ibon_assign_adjacent_seat(flag) {
    //console.log("disable_adjacent_seat flag:"+flag);
    if(flag) {
        $('input[type=checkbox]').each(function() {
           $(this).prop('checked', true);
        });
    }
}

function ibon_focus_on_captcha()
{
    $("div.editor-box > div > input[type='text']").focus();
}

var myInterval = null;

function ibon_get_ocr_image()
{
    //console.log("get_ocr_image");
    let image_data = "";

    // PS: tixcraft have different domain to use the same content script.
    const currentUrl = window.location.href;
    const domain = currentUrl.split('/')[2];

    let image_id = 'chk_pic';
    let img = document.getElementById(image_id);
    if(img!=null) {
        let canvas = document.createElement('canvas');
        let context = canvas.getContext('2d');
        canvas.height = img.naturalHeight;
        canvas.width = img.naturalWidth;
        context.drawImage(img, 0, 0);
        let img_data = canvas.toDataURL();
        if(img_data) {
            image_data = img_data.split(",")[1];
                //console.log(image_data);
        }
    }
    return image_data;
}

chrome.runtime.onMessage.addListener((message) => {
    //console.log('sent from background', message);
    ibon_set_ocr_answer(message.answer);
});

function ibon_set_ocr_answer(answer)
{
    console.log("answer:"+answer);
    if(answer.length > 0) {
        $("div.editor-box > div > input[type='text']").val(answer);
        //console.log($("div#ticket-wrap a[onclick]").length);
        //$("div#ticket-wrap a[onclick]").click();
        //$("#aspnetForm").submit();
        let done_div="<div style='display:none' id='done'></div>";
        $("body").append(done_div);

    }
}

async function ibon_get_ocr_answer(api_url, image_data)
{
    let bundle = {
      action: 'ocr',
      data: {
        'url': api_url + 'ocr',
        'image_data':image_data,
      }
    };
    
    let bundle_string = JSON.stringify(bundle);
    const return_answer = await chrome.runtime.sendMessage(bundle);
    //console.log(return_answer);
}

function ibon_orc_image_ready(api_url)
{
    let ret=false;
    let image_data = ibon_get_ocr_image();
    if(image_data.length>0) {
        ret=true;
        if(myInterval) clearInterval(myInterval);
        ibon_get_ocr_answer(api_url, image_data);
    }
    //console.log("ibon_orc_image_ready:"+ret);
    return ret;
}

storage.get('settings', function (items)
{
    if (items.settings)
    {
        settings = items.settings;
    } else {
        console.log('no settings found');
    }
});


storage.get('settings', function (items)
{
    if (items.settings)
    {
        settings = items.settings;
    }
});

function get_remote_url(settings)
{
    let remote_url_string = "";
    if(settings) {
        let remote_url_array = [];
        if(settings.advanced.remote_url.length > 0) {
            remote_url_array = JSON.parse('[' +  settings.advanced.remote_url +']');
        }
        if(remote_url_array.length) {
            remote_url_string = remote_url_array[0];
        }
    }
    return remote_url_string;
}

storage.get('status', function (items)
{
    if (items.status && items.status=='ON')
    {
        //console.log("ticket_number:"+ settings.ticket_number);
        ibon_assign_ticket_number(settings.ticket_number);
        ibon_assign_adjacent_seat(settings.advanced.disable_adjacent_seat);
        
        // ocr
        if(settings.ocr_captcha.enable) {
            let remote_url_string = get_remote_url(settings);
            if(!ibon_orc_image_ready(remote_url_string)) {
                myInterval = setInterval(() => {
                    ibon_orc_image_ready(remote_url_string);
                }, 100);
            }
        } else {
            // no orc, just focus;
            ibon_focus_on_captcha();
        }
        } else {
        console.log('no status found');
    }
});
