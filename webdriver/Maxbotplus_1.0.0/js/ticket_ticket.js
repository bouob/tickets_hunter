const storage = chrome.storage.local;
var settings = null;

$("footer").remove();

function ticket_assign_adjacent_seat(flag) {
    //console.log("disable_adjacent_seat flag:"+flag);
    if(flag) {
        $('input[type=checkbox]').each(function() {
           $(this).prop('checked', true);
        });
    }
}

function ticket_focus_on_captcha()
{
    $("div.login-form input[autocomplete='off']").focus();
}

var myInterval = null;

function ticket_get_ocr_image()
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
    ticket_set_ocr_answer(message.answer);
});

function ticket_set_ocr_answer(answer)
{
    //console.log("answer:"+answer);
    if(answer.length > 0) {
        const currentUrl = window.location.href;
        const domain = currentUrl.split('/')[2];
        const scrip_page = currentUrl.split('/')[5];

        if(answer.length == 4) {
            answer = answer.toUpperCase();
            let query_string = "div.form-group input[autocomplete='off']";
            if(domain.indexOf('kham') > -1) {
                query_string = ".step2Login input[maxlength='4']";
            }
            $(query_string).val(answer);
            //console.log($(query_string).length);
            //$("div#ticket-wrap a[onclick]").click();
            //$("#aspnetForm").submit();
            let done_div="<div style='display:none' id='done'></div>";
            $("body").append(done_div);
        } else {
            let query_string = "div.form-group a img";
            if(domain.indexOf('kham') > -1) {
                query_string = ".step2Login a img";
            }
            let onclick_event = $(query_string).attr("onclick");
            let onclick_url = onclick_event.split('?')[1];
            let ocr_type = get_url_parameter("TYPE", onclick_url);
            //console.log("get new captcha:", onclick_event);
            if(ocr_type && ocr_type.length > 0) {
                let new_image_src = "/pic.aspx?TYPE="+ ocr_type +"&ts=" + new Date().getTime();
                $("#chk_pic").attr("src", new_image_src);

                let remote_url_string = get_remote_url(settings);
                myInterval = setInterval(() => {
                    ticket_orc_image_ready(remote_url_string);
                }, 400);
            }
        }

    }
}

async function ticket_get_ocr_answer(api_url, image_data)
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

function ticket_orc_image_ready(api_url)
{
    let ret=false;
    let image_data = ticket_get_ocr_image();
    if(image_data.length>0) {
        ret=true;
        if(myInterval) clearInterval(myInterval);
        ticket_get_ocr_answer(api_url, image_data);
    }
    //console.log("ticket_orc_image_ready:"+ret);
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

function ticket_assign_ticket(settings)
{
    if(settings) {
        $('div.qty-select input[type="text"]').val(settings.ticket_number);
    }
}

storage.get('status', function (items)
{
    if (items.status && items.status=='ON')
    {
        //console.log("ticket_number:"+ settings.ticket_number);
        //ticket_assign_adjacent_seat(settings.advanced.disable_adjacent_seat);

        ticket_assign_ticket(settings);

        // ocr
        if(settings.ocr_captcha.enable) {
            let remote_url_string = get_remote_url(settings);
            if(!ticket_orc_image_ready(remote_url_string)) {
                myInterval = setInterval(() => {
                    ticket_orc_image_ready(remote_url_string);
                }, 100);
            }
        } else {
            // no orc, just focus;
            ticket_focus_on_captcha();
        }
    } else {
        console.log('no status found');
    }
});
