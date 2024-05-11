const storage = chrome.storage.local;

const submitButton = document.querySelector('#save_btn');
const ticket_number = document.querySelector('#ticket_number');
const date_select_mode = document.querySelector('#date_select_mode');
const date_keyword = document.querySelector('#date_keyword');
const area_select_mode = document.querySelector('#area_select_mode');
const area_keyword = document.querySelector('#area_keyword');
const keyword_exclude = document.querySelector('#keyword_exclude');
const auto_reload_page_interval = document.querySelector('#auto_reload_page_interval');
const auto_press_next_step_button = document.querySelector('#auto_press_next_step_button');
const max_dwell_time = document.querySelector('#max_dwell_time');
const disable_adjacent_seat = document.querySelector('#disable_adjacent_seat');
const ocr_captcha_enable = document.querySelector('#ocr_captcha_enable');
const ocr_captcha_use_public_server = document.querySelector('#ocr_captcha_use_public_server');
const remote_url = document.querySelector('#remote_url');
const user_guess_string = document.querySelector('#user_guess_string');

const PUBLIC_SERVER_URL = "http://maxbot.dropboxlike.com:16888/";

var settings = null;

loadChanges();

submitButton.addEventListener('click', saveChanges);
ocr_captcha_use_public_server.addEventListener('change', checkUsePublicServer);

async function saveChanges()
{
    const ticket_number_value = ticket_number.value;
    //console.log(ticket_number_value);
    if (!ticket_number_value)
    {
        message('Error: No ticket_number specified');
    } else {
        if(settings) {
            settings.ticket_number = ticket_number_value;
            settings.date_auto_select.mode = date_select_mode.value;

            let date_keyword_string = date_keyword.value;
            if(date_keyword_string.indexOf('"')==-1) {
                date_keyword_string = '"' + date_keyword_string + '"';
            }
            settings.date_auto_select.date_keyword = date_keyword_string;

            settings.area_auto_select.mode = area_select_mode.value;

            let area_keyword_string = area_keyword.value;
            if(area_keyword_string.indexOf('"')==-1) {
                area_keyword_string = '"' + area_keyword_string + '"';
            }
            settings.area_auto_select.area_keyword = area_keyword_string;

            let user_guess_string_string = user_guess_string.value;
            if(user_guess_string_string.indexOf('"')==-1) {
                user_guess_string_string = '"' + user_guess_string_string + '"';
            }
            settings.advanced.user_guess_string = user_guess_string_string;

            settings.keyword_exclude = keyword_exclude.value;

            settings.advanced.auto_reload_page_interval = auto_reload_page_interval.value;
            settings.kktix.auto_press_next_step_button = auto_press_next_step_button.checked;
            settings.kktix.max_dwell_time = max_dwell_time.value;
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
            if(date_keyword.value=='""') {
                date_keyword.value='';
            }

            area_select_mode.value = settings.area_auto_select.mode;
            area_keyword.value = settings.area_auto_select.area_keyword;
            if(area_keyword.value=='""') {
                area_keyword.value='';
            }

            user_guess_string.value = settings.advanced.user_guess_string;
            if(user_guess_string.value=='""') {
                user_guess_string.value='';
            }

            keyword_exclude.value = settings.keyword_exclude;
            auto_reload_page_interval.value = settings.advanced.auto_reload_page_interval;
            auto_press_next_step_button.checked = settings.kktix.auto_press_next_step_button;
            max_dwell_time.value = settings.kktix.max_dwell_time;
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

async function checkUsePublicServer()
{
    if(ocr_captcha_enable.checked) {
        remote_url.value = PUBLIC_SERVER_URL;
    } else {

    }
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
