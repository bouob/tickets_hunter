//const storage = chrome.storage.local;

const run_button = document.querySelector('#run_btn');
const save_button = document.querySelector('#save_btn');
const exit_button = document.querySelector('#exit_btn');
const pause_button = document.querySelector('#pause_btn');
const resume_button = document.querySelector('#resume_btn');

const homepage = document.querySelector('#homepage');
const ticket_number = document.querySelector('#ticket_number');
const date_select_mode = document.querySelector('#date_select_mode');
const date_keyword = document.querySelector('#date_keyword');
const area_select_mode = document.querySelector('#area_select_mode');
const area_keyword = document.querySelector('#area_keyword');
const keyword_exclude = document.querySelector('#keyword_exclude');

const auto_reload_page_interval = document.querySelector('#auto_reload_page_interval');
const auto_press_next_step_button = document.querySelector('#auto_press_next_step_button');
const kktix_status_api = document.querySelector('#kktix_status_api');
const max_dwell_time = document.querySelector('#max_dwell_time');
const disable_adjacent_seat = document.querySelector('#disable_adjacent_seat');
const ocr_captcha_enable = document.querySelector('#ocr_captcha_enable');
const ocr_captcha_use_public_server = document.querySelector('#ocr_captcha_use_public_server');
const remote_url = document.querySelector('#remote_url');
const user_guess_string = document.querySelector('#user_guess_string');

const PUBLIC_SERVER_URL = "http://maxbot.dropboxlike.com:16888/";


const tixcraft_sid = document.querySelector('#tixcraft_sid');
const ibonqware = document.querySelector('#ibonqware');
const facebook_account = document.querySelector('#facebook_account');
const kktix_account = document.querySelector('#kktix_account');
const fami_account = document.querySelector('#fami_account');
const kham_account = document.querySelector('#kham_account');
const ticket_account = document.querySelector('#ticket_account');
const udn_account = document.querySelector('#udn_account');
const ticketplus_account = document.querySelector('#ticketplus_account');
const cityline_account = document.querySelector('#cityline_account');
const urbtix_account = document.querySelector('#urbtix_account');
const hkticketing_account = document.querySelector('#hkticketing_account');

const facebook_password = document.querySelector('#facebook_password');
const kktix_password = document.querySelector('#kktix_password');
const fami_password = document.querySelector('#fami_password');
const kham_password = document.querySelector('#kham_password');
const ticket_password = document.querySelector('#ticket_password');
const udn_password = document.querySelector('#udn_password');
const ticketplus_password = document.querySelector('#ticketplus_password');
const urbtix_password = document.querySelector('#urbtix_password');
const hkticketing_password = document.querySelector('#hkticketing_password');

const idle_keyword = document.querySelector('#idle_keyword');
const resume_keyword = document.querySelector('#resume_keyword');
const idle_keyword_second = document.querySelector('#idle_keyword_second');
const resume_keyword_second = document.querySelector('#resume_keyword_second');

var settings = null;

load_changes();

run_button.addEventListener('click', maxbot_launch);
save_button.addEventListener('click', maxbot_save);
exit_button.addEventListener('click', maxbot_shutdown);
pause_button.addEventListener('click', maxbot_pause_api);
resume_button.addEventListener('click', maxbot_resume_api);

ocr_captcha_use_public_server.addEventListener('change', checkUsePublicServer);


function load_changes()
{
    let api_url = "http://127.0.0.1:16888/load";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        //console.log(data);
        settings = data;
        if (settings)
        {
            //console.log("ticket_number:"+ settings.ticket_number);
            homepage.value = settings.homepage;
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
            kktix_status_api.checked = settings.advanced.kktix_status_api;
            max_dwell_time.value = settings.advanced.max_dwell_time;
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

            tixcraft_sid.value = settings.advanced.tixcraft_sid;
            ibonqware.value = settings.advanced.ibonqware;
            facebook_account.value = settings.advanced.facebook_account;
            kktix_account.value = settings.advanced.kktix_account;
            fami_account.value = settings.advanced.fami_account;
            kham_account.value = settings.advanced.kham_account;
            ticket_account.value = settings.advanced.ticket_account;
            udn_account.value = settings.advanced.udn_account;
            ticketplus_account.value = settings.advanced.ticketplus_account;
            cityline_account.value = settings.advanced.cityline_account;
            urbtix_account.value = settings.advanced.urbtix_account;
            hkticketing_account.value = settings.advanced.hkticketing_account;

            facebook_password.value = settings.advanced.facebook_password;
            kktix_password.value = settings.advanced.kktix_password;
            fami_password.value = settings.advanced.fami_password;
            kham_password.value = settings.advanced.kham_password;
            ticket_password.value = settings.advanced.ticket_password;
            udn_password.value = settings.advanced.udn_password;
            ticketplus_password.value = settings.advanced.ticketplus_password;
            urbtix_password.value = settings.advanced.urbtix_password;
            hkticketing_password.value = settings.advanced.hkticketing_password;

            idle_keyword.value = settings.advanced.idle_keyword;
            if(idle_keyword.value=='""') {
                idle_keyword.value='';
            }
            resume_keyword.value = settings.advanced.resume_keyword;
            if(resume_keyword.value=='""') {
                resume_keyword.value='';
            }
            idle_keyword_second.value = settings.advanced.idle_keyword_second;
            if(idle_keyword_second.value=='""') {
                idle_keyword_second.value='';
            }
            resume_keyword_second.value = settings.advanced.resume_keyword_second;
            if(resume_keyword_second.value=='""') {
                resume_keyword_second.value='';
            }


            //message('Loaded saved settings.');
        } else {
            console.log('no settings found');
        }

    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });


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


function maxbot_launch()
{
    let api_url = "http://127.0.0.1:16888/run";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

function maxbot_shutdown()
{
    let api_url = "http://127.0.0.1:16888/shutdown";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        window.close();
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

function save_changes_to_dict()
{
    const ticket_number_value = ticket_number.value;
    //console.log(ticket_number_value);
    if (!ticket_number_value)
    {
        message('Error: No ticket_number specified');
    } else {
        if(settings) {
            settings.homepage = homepage.value;
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
            settings.advanced.kktix_status_api = kktix_status_api.checked;
            settings.advanced.max_dwell_time = max_dwell_time.value;
            settings.advanced.disable_adjacent_seat = disable_adjacent_seat.checked;
            settings.ocr_captcha.enable = ocr_captcha_enable.checked;

            let remote_url_array = [];
            remote_url_array.push(remote_url.value);
            let remote_url_string = JSON.stringify(remote_url_array);
            remote_url_string = remote_url_string.substring(0,remote_url_string.length-1);
            remote_url_string = remote_url_string.substring(1);
            //console.log("final remote_url_string:"+remote_url_string);
            settings.advanced.remote_url = remote_url_string;

            settings.tixcraft_sid = tixcraft_sid.value;
            settings.ibonqware = ibonqware.value;
            settings.facebook_account = facebook_account.value;
            settings.kktix_account = kktix_account.value;
            settings.fami_account = fami_account.value;
            settings.kham_account = kham_account.value;
            settings.ticket_account = ticket_account.value;
            settings.udn_account = udn_account.value;
            settings.ticketplus_account = ticketplus_account.value;
            settings.cityline_account = cityline_account.value;
            settings.urbtix_account = urbtix_account.value;
            settings.hkticketing_account = hkticketing_account.value;

            settings.facebook_password = facebook_password.value;
            settings.kktix_password = kktix_password.value;
            settings.fami_password = fami_password.value;
            settings.kham_password = kham_password.value;
            settings.ticket_password = ticket_password.value;
            settings.udn_password = udn_password.value;
            settings.ticketplus_password = ticketplus_password.value;
            settings.urbtix_password = urbtix_password.value;
            settings.hkticketing_password = hkticketing_password.value;

            settings.advanced.idle_keyword = idle_keyword.value;
            settings.advanced.resume_keyword = resume_keyword.value;
            settings.advanced.idle_keyword_second = idle_keyword_second.value;
            settings.advanced.resume_keyword_second = resume_keyword_second.value;

        }
        message('Settings saved');
    }
}

function maxbot_save_api()
{
    let api_url = "http://127.0.0.1:16888/save";
    if(settings) {
        $.post( api_url, JSON.stringify(settings), function() {
            //alert( "success" );
        })
        .done(function(data) {
            //alert( "second success" );
        })
        .fail(function() {
            //alert( "error" );
        })
        .always(function() {
            //alert( "finished" );
        });
    }
}

function maxbot_pause_api()
{
    let api_url = "http://127.0.0.1:16888/pause";
    if(settings) {
        $.get( api_url, function() {
            //alert( "success" );
        })
        .done(function(data) {
            //alert( "second success" );
        })
        .fail(function() {
            //alert( "error" );
        })
        .always(function() {
            //alert( "finished" );
        });
    }
}

function maxbot_resume_api()
{
    let api_url = "http://127.0.0.1:16888/resume";
    if(settings) {
        $.get( api_url, function() {
            //alert( "success" );
        })
        .done(function(data) {
            //alert( "second success" );
        })
        .fail(function() {
            //alert( "error" );
        })
        .always(function() {
            //alert( "finished" );
        });
    }
}
function maxbot_save()
{
    //$('#saveModal').modal('show')
    save_changes_to_dict();
    maxbot_save_api();
}

function maxbot_status_api()
{
    let api_url = "http://127.0.0.1:16888/status";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        let status_text = "已暫停";
        let status_class = "badge text-bg-danger";
        if(data.status) {
            status_text="已啟動";
            status_class = "badge text-bg-success";
            $("#pause_btn").removeClass("disappear");
            $("#resume_btn").addClass("disappear");
        } else {
            $("#pause_btn").addClass("disappear");
            $("#resume_btn").removeClass("disappear");
        }
        $("#last_url").html(data.last_url);
        $("#maxbot_status").html(status_text).prop( "class", status_class);
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

function update_system_time()
{
    var currentdate = new Date(); 
    var datetime = currentdate.getHours() + ":"  
                + currentdate.getMinutes() + ":" 
                + currentdate.getSeconds();
    $("#system_time").html(datetime);
}

var status_interval= setInterval(() => {
    maxbot_status_api();
    update_system_time();
}, 200);
