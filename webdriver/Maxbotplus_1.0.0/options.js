const storage = chrome.storage.local;

const submitButton = document.querySelector('#save_btn');
const ticket_number = document.querySelector('#ticket_number');
const date_select_mode = document.querySelector('#date_select_mode');
const date_keyword = document.querySelector('#date_keyword');
const area_select_mode = document.querySelector('#area_select_mode');
const area_keyword = document.querySelector('#area_keyword');
const keyword_exclude = document.querySelector('#keyword_exclude');
const auto_reload_page_interval = document.querySelector('#auto_reload_page_interval');
const disable_adjacent_seat = document.querySelector('#disable_adjacent_seat');
const ocr_captcha_enable = document.querySelector('#ocr_captcha_enable');
const remote_url = document.querySelector('#remote_url');

var settings = null;

loadChanges();

submitButton.addEventListener('click', saveChanges);

async function saveChanges()
{
    const ticket_number_value = ticket_number.value;
    console.log(ticket_number_value);
    if (!ticket_number_value)
    {
        message('Error: No ticket_number specified');
    } else {
        if(settings) {
            settings.ticket_number = ticket_number_value;
            settings.date_auto_select.mode = date_select_mode.value;
            settings.date_auto_select.date_keyword = date_keyword.value;
            settings.area_auto_select.mode = area_select_mode.value;
            settings.area_auto_select.area_keyword = area_keyword.value;
            settings.keyword_exclude = keyword_exclude.value;
            settings.advanced.auto_reload_page_interval = auto_reload_page_interval.value;
            settings.advanced.disable_adjacent_seat = disable_adjacent_seat.checked;
            settings.ocr_captcha.enable = ocr_captcha_enable.checked;

            let remote_url_array = [];
            remote_url_array.push(remote_url.value);
            let remote_url_string = JSON.stringify(remote_url_array);
            remote_url_string = remote_url_string.substring(0,remote_url_string.length-1);
            remote_url_string = remote_url_string.substring(1);
            //console.log("final remote_url_string:"+remote_url_string);
            settings.advanced.remote_url = remote_url_string;

            await storage.set(
            {
                settings: settings
            }
            );
        }
        message('Settings saved');
    }
}

function loadChanges()
{
    storage.get('settings', function (items)
    {
        //console.log(items);
        if (items.settings)
        {
            settings = items.settings;
            //console.log("ticket_number:"+ settings.ticket_number);
            ticket_number.value = settings.ticket_number;
            date_select_mode.value = settings.date_auto_select.mode;
            date_keyword.value = settings.date_auto_select.date_keyword;
            area_select_mode.value = settings.area_auto_select.mode;
            area_keyword.value = settings.area_auto_select.area_keyword;
            keyword_exclude.value = settings.keyword_exclude;
            auto_reload_page_interval.value = settings.advanced.auto_reload_page_interval;
            disable_adjacent_seat.checked = settings.advanced.disable_adjacent_seat;
            ocr_captcha_enable.checked = settings.ocr_captcha.enable;

            let remote_url_string = "";
            let remote_url_array = [];
            if(settings.advanced.remote_url.length > 0) {
                remote_url_array = JSON.parse('[' +  settings.advanced.remote_url +']');
            }
            if(remote_url_array.length) {
                remote_url_string = remote_url_array[0];
            }
            remote_url.value = remote_url_string;

            //message('Loaded saved settings.');
        } else {
            console.log('no settings found');
        }

    }
    );
}


let messageClearTimer;
function message(msg)
{
    clearTimeout(messageClearTimer);
    const message = document.querySelector('#message');
    message.innerText = msg;
    messageClearTimer = setTimeout(function ()
        {
            message.innerText = '';
        }, 3000);
}
