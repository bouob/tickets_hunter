const storage = chrome.storage.local;
var settings = null;

$('input[type=checkbox]').each(function ()
{
    $(this).prop('checked', true);
}
);
$("img[style='width: 100%; padding: 0;']").remove();
$("footer").remove();

function assign_ticket_number(ticket_number)
{
    if ($("#ticketPriceList select").length > 0)
    {
        let $ticket_options = $("#ticketPriceList select:first option");
        if ($ticket_options.length)
        {
            let is_ticket_number_assign = false;
            if (ticket_number > 0)
            {
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
            if (!is_ticket_number_assign)
            {
                $ticket_options.last().prop('selected', true);
            }
        }
    }
}

var myInterval = null;

function get_ocr_image()
{
    //console.log("get_ocr_image");
    let image_data = "";

    // PS: tixcraft have different domain to use the same content script.
    const currentUrl = window.location.href;
    const domain = currentUrl.split('/')[2];

    let image_id = 'TicketForm_verifyCode-image';
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
    set_ocr_answer(message.answer);
});

function set_ocr_answer(answer)
{
    console.log("answer:"+answer);
    if(answer.length > 0) {
        $('#TicketForm_verifyCode').val(answer);
        $("button[type='submit']").click();
    }
}

async function get_ocr_answer(api_url, image_data)
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

    // fail due to CORS error
    //ocr(bundle.data.url, bundle.data.image_data, bundle.data.callback);
}

function orc_image_ready(api_url)
{
    let ret=false;
    let image_data = get_ocr_image();
    if(image_data.length>0) {
        ret=true;
        if(myInterval) clearInterval(myInterval);
        get_ocr_answer(api_url, image_data);
    }
    console.log("orc_image_ready:"+ret);
    return ret;
}


storage.get('settings', function (items)
{
    if (items.settings)
    {
        settings = items.settings;
        //console.log("ticket_number:"+ settings.ticket_number);
        assign_ticket_number(settings.ticket_number);
        if(settings.ocr_captcha.enable) {
            let remote_url_string = "";
            let remote_url_array = [];
            if(settings.advanced.remote_url.length > 0) {
                remote_url_array = JSON.parse('[' +  settings.advanced.remote_url +']');
            }
            if(remote_url_array.length) {
                remote_url_string = remote_url_array[0];
            }
            if(!orc_image_ready(remote_url_string)) {
                myInterval = setInterval(() => {
                    orc_image_ready(remote_url_string);
                }, 100);
            }
        }
    } else {
        console.log('no settings found');
    }
});
