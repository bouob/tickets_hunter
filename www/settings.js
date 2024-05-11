
// action bar
const run_button = document.querySelector('#run_btn');
const save_button = document.querySelector('#save_btn');
const reset_button = document.querySelector('#reset_btn');
const exit_button = document.querySelector('#exit_btn');
const pause_button = document.querySelector('#pause_btn');
const resume_button = document.querySelector('#resume_btn');

// preference
const homepage = document.querySelector('#homepage');
const ticket_number = document.querySelector('#ticket_number');
const date_select_mode = document.querySelector('#date_select_mode');
const date_keyword = document.querySelector('#date_keyword');
const area_select_mode = document.querySelector('#area_select_mode');
const area_keyword = document.querySelector('#area_keyword');
const keyword_exclude = document.querySelector('#keyword_exclude');

// advance
const browser = document.querySelector('#browser');
const webdriver_type = document.querySelector('#webdriver_type');
const play_ticket_sound = document.querySelector('#play_ticket_sound');
const play_order_sound = document.querySelector('#play_order_sound');
const play_sound_filename = document.querySelector('#play_sound_filename');

const auto_press_next_step_button = document.querySelector('#auto_press_next_step_button');
const max_dwell_time = document.querySelector('#max_dwell_time');

const cityline_queue_retry = document.querySelector('#cityline_queue_retry');

const auto_reload_page_interval = document.querySelector('#auto_reload_page_interval');
const reset_browser_interval = document.querySelector('#reset_browser_interval');
const proxy_server_port = document.querySelector('#proxy_server_port');
const window_size = document.querySelector('#window_size');
const chrome_extension = document.querySelector('#chrome_extension');
const disable_adjacent_seat = document.querySelector('#disable_adjacent_seat');

const hide_some_image = document.querySelector('#hide_some_image');
const block_facebook_network = document.querySelector('#block_facebook_network');
const headless = document.querySelector('#headless');
const verbose = document.querySelector('#verbose');

const ocr_captcha_enable = document.querySelector('#ocr_captcha_enable');
const ocr_captcha_use_public_server = document.querySelector('#ocr_captcha_use_public_server');
const ocr_captcha_image_source = document.querySelector('#ocr_captcha_image_source');
const ocr_captcha_force_submit = document.querySelector('#ocr_captcha_force_submit');
const remote_url = document.querySelector('#remote_url');
const PUBLIC_SERVER_URL = "http://maxbot.dropboxlike.com:16888/";

// dictionary
const user_guess_string = document.querySelector('#user_guess_string');


// auto fill
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

// runtime
const idle_keyword = document.querySelector('#idle_keyword');
const resume_keyword = document.querySelector('#resume_keyword');
const idle_keyword_second = document.querySelector('#idle_keyword_second');
const resume_keyword_second = document.querySelector('#resume_keyword_second');

var settings = null;

maxbot_load_api();

function load_settins_to_form(settings)
{
    if (settings)
    {
        //console.log("ticket_number:"+ settings.ticket_number);
        // preference
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

        keyword_exclude.value = settings.keyword_exclude;
        
        // advanced
        browser.value = settings.browser;
        webdriver_type.value = settings.webdriver_type;
        
        play_ticket_sound.checked = settings.advanced.play_sound.ticket;
        play_order_sound.checked = settings.advanced.play_sound.order;
        play_sound_filename.value = settings.advanced.play_sound.filename;

        auto_press_next_step_button.checked = settings.kktix.auto_press_next_step_button;
        max_dwell_time.value = settings.kktix.max_dwell_time;

        cityline_queue_retry.checked = settings.cityline.cityline_queue_retry;

        auto_reload_page_interval.value = settings.advanced.auto_reload_page_interval;
        reset_browser_interval.value = settings.advanced.reset_browser_interval;
        proxy_server_port.value  = settings.advanced.proxy_server_port;
        window_size.value  = settings.advanced.window_size;

        chrome_extension.checked = settings.advanced.chrome_extension;
        disable_adjacent_seat.checked = settings.advanced.disable_adjacent_seat;

        hide_some_image.checked = settings.advanced.hide_some_image;
        block_facebook_network.checked = settings.advanced.block_facebook_network;
        headless.checked = settings.advanced.headless;
        verbose.checked = settings.advanced.verbose;

        ocr_captcha_enable.checked = settings.ocr_captcha.enable;
        ocr_captcha_image_source.value  = settings.ocr_captcha.image_source;
        ocr_captcha_force_submit.checked = settings.ocr_captcha.force_submit;

        let remote_url_string = "";
        let remote_url_array = [];
        if(settings.advanced.remote_url.length > 0) {
            remote_url_array = JSON.parse('[' +  settings.advanced.remote_url +']');
        }
        if(remote_url_array.length) {
            remote_url_string = remote_url_array[0];
        }
        remote_url.value = remote_url_string;

        // dictionary
        user_guess_string.value = settings.advanced.user_guess_string;
        if(user_guess_string.value=='""') {
            user_guess_string.value='';
        }

        // auto fill
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

        // runtime
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
    } else {
        console.log('no settings found');
    }
}

function maxbot_load_api()
{
    let api_url = "http://127.0.0.1:16888/load";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        //console.log(data);
        settings = data;
        load_settins_to_form(data);
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

function maxbot_reset_api()
{
    let api_url = "http://127.0.0.1:16888/reset";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        //console.log(data);
        settings = data;
        load_settins_to_form(data);
        check_unsaved_fields();
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

function checkUsePublicServer()
{
    if(ocr_captcha_enable.checked) {
        remote_url.value = PUBLIC_SERVER_URL;
    } else {

    }
}

let messageClearTimer;

function message(msg)
{
    $("#message_detail").html("存檔完成");
    $("#message_modal").modal("show");
}

function message_old(msg)
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
    save_changes_to_dict(true);
    maxbot_save_api(maxbot_run_api());
}

function maxbot_run_api()
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

function maxbot_shutdown_api()
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

function save_changes_to_dict(silent_flag)
{
    const ticket_number_value = parseInt(ticket_number.value);
    //console.log(ticket_number_value);
    if (!ticket_number_value)
    {
        message('提示: 請指定張數');
    } else {
        if(settings) {

            // preference
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

            settings.keyword_exclude = keyword_exclude.value;

            // advanced
            settings.browser = browser.value;
            settings.webdriver_type = webdriver_type.value;
        
            settings.advanced.play_sound.ticket = play_ticket_sound.checked;
            settings.advanced.play_sound.order = play_order_sound.checked;
            settings.advanced.play_sound.filename = play_sound_filename.value;

            settings.kktix.auto_press_next_step_button = auto_press_next_step_button.checked;
            settings.kktix.max_dwell_time = parseInt(max_dwell_time.value);

            settings.cityline.cityline_queue_retry = cityline_queue_retry.checked;


            settings.advanced.auto_reload_page_interval = Number(auto_reload_page_interval.value);
            settings.advanced.reset_browser_interval = parseInt(reset_browser_interval.value);
            settings.advanced.proxy_server_port = proxy_server_port.value;
            settings.advanced.window_size = window_size.value;

            settings.advanced.chrome_extension = chrome_extension.checked;
            settings.advanced.disable_adjacent_seat = disable_adjacent_seat.checked;

            settings.advanced.hide_some_image = hide_some_image.checked;
            settings.advanced.block_facebook_network = block_facebook_network.checked;
            settings.advanced.headless = headless.checked;
            settings.advanced.verbose = verbose.checked;

            settings.ocr_captcha.enable = ocr_captcha_enable.checked;
            settings.ocr_captcha.image_source = ocr_captcha_image_source.value;
            settings.ocr_captcha.force_submit = ocr_captcha_force_submit.checked;

            let remote_url_array = [];
            remote_url_array.push(remote_url.value);
            let remote_url_string = JSON.stringify(remote_url_array);
            remote_url_string = remote_url_string.substring(0,remote_url_string.length-1);
            remote_url_string = remote_url_string.substring(1);
            //console.log("final remote_url_string:"+remote_url_string);
            settings.advanced.remote_url = remote_url_string;

            // dictionary
            let user_guess_string_string = user_guess_string.value;
            if(user_guess_string_string.indexOf('"')==-1) {
                user_guess_string_string = '"' + user_guess_string_string + '"';
            }
            settings.advanced.user_guess_string = user_guess_string_string;

            // auto fill
            settings.advanced.tixcraft_sid = tixcraft_sid.value;
            settings.advanced.ibonqware = ibonqware.value;
            settings.advanced.facebook_account = facebook_account.value;
            settings.advanced.kktix_account = kktix_account.value;
            settings.advanced.fami_account = fami_account.value;
            settings.advanced.kham_account = kham_account.value;
            settings.advanced.ticket_account = ticket_account.value;
            settings.advanced.udn_account = udn_account.value;
            settings.advanced.ticketplus_account = ticketplus_account.value;
            settings.advanced.cityline_account = cityline_account.value;
            settings.advanced.urbtix_account = urbtix_account.value;
            settings.advanced.hkticketing_account = hkticketing_account.value;

            settings.advanced.facebook_password = facebook_password.value;
            settings.advanced.kktix_password = kktix_password.value;
            settings.advanced.fami_password = fami_password.value;
            settings.advanced.kham_password = kham_password.value;
            settings.advanced.ticket_password = ticket_password.value;
            settings.advanced.udn_password = udn_password.value;
            settings.advanced.ticketplus_password = ticketplus_password.value;
            settings.advanced.urbtix_password = urbtix_password.value;
            settings.advanced.hkticketing_password = hkticketing_password.value;

            // runtime
            settings.advanced.idle_keyword = idle_keyword.value;
            settings.advanced.resume_keyword = resume_keyword.value;
            settings.advanced.idle_keyword_second = idle_keyword_second.value;
            settings.advanced.resume_keyword_second = resume_keyword_second.value;
        }
        if(!silent_flag) {
            message('已存檔');
        }
    }
}

function maxbot_save_api(callback)
{
    let api_url = "http://127.0.0.1:16888/save";
    if(settings) {
        $.post( api_url, JSON.stringify(settings), function() {
            //alert( "success" );
        })
        .done(function(data) {
            //alert( "second success" );
            check_unsaved_fields();
            if(callback) callback;
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
    save_changes_to_dict(false);
    maxbot_save_api();
}

function check_unsaved_fields()
{
    if(settings) {
        const field_list_basic = ["homepage","ticket_number","browser","webdriver_type"];
        field_list_basic.forEach(f => {
            const field = document.querySelector('#'+f);
            if(field.value != settings[f]) {
                $("#"+f).addClass("is-invalid");
            } else {
                $("#"+f).removeClass("is-invalid");
            }
        });
        const field_list_advance = [
            "tixcraft_sid",
            "ibonqware",
            "facebook_account",
            "kktix_account",
            "fami_account",
            "cityline_account",
            "urbtix_account",
            "hkticketing_account",
            "kham_account",
            "ticket_account",
            "udn_account",
            "ticketplus_account",
            "facebook_password",
            "kktix_password",
            "fami_password",
            "urbtix_password",
            "hkticketing_password",
            "kham_password",
            "ticket_password",
            "udn_password",
            "ticketplus_password",
            "user_guess_string",
            "remote_url",
            "auto_reload_page_interval",
            "reset_browser_interval",
            "proxy_server_port",
            "window_size",
            "idle_keyword",
            "resume_keyword",
            "idle_keyword_second",
            "resume_keyword_second"
        ];
        field_list_advance.forEach(f => {
            const field = document.querySelector('#'+f);
            let formated_input = field.value;
            let formated_saved_value = settings["advanced"][f];
            //console.log(f);
            //console.log(field.value);
            //console.log(formated_saved_value);
            if(typeof formated_saved_value == "string") {
                if(formated_input=='') 
                    formated_input='""';
                if(formated_saved_value=='') 
                    formated_saved_value='""';
                if(formated_saved_value.indexOf('"') > -1) {
                    if(formated_input.length) {
                        if(formated_input != '""') {
                            formated_input = '"' + formated_input + '"';
                        }
                    }
                }
            }
            let is_not_match = (formated_input != formated_saved_value);
            if(is_not_match) {
                //console.log(f);
                //console.log(formated_input);
                //console.log(formated_saved_value);
                $("#"+f).addClass("is-invalid");
            } else {
                $("#"+f).removeClass("is-invalid");
            }
        });

        // check spcial feature for sites.
        if(homepage.value.length) {
            let special_site = "";
            const special_site_list = ["kktix", "cityline"];
            for(let i=0; i<special_site_list.length; i++) {
                const site=special_site_list[i];
                const match_url_1 = "." + site + ".com/";
                const match_url_2 = "/" + site + ".com/";
                //console.log(match_url);
                if(homepage.value.indexOf(match_url_1) > 0 || homepage.value.indexOf(match_url_2) > 0) {
                    special_site = site;
                }
            }
            $('div[data-under]').addClass("disappear");
            if(special_site.length) {
                $('div[data-under="'+ special_site +'"]').removeClass("disappear");
            }
        }
    }
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
    var datetime = ("0" + currentdate.getHours()).slice(-2) + ":"  
                + ("0" + currentdate.getMinutes()).slice(-2) + ":" 
                + ("0" + currentdate.getSeconds()).slice(-2);
    $("#system_time").html(datetime);
}

var status_interval= setInterval(() => {
    maxbot_status_api();
    update_system_time();
}, 500);

run_button.addEventListener('click', maxbot_launch);
save_button.addEventListener('click', maxbot_save);
reset_button.addEventListener('click', maxbot_reset_api);
exit_button.addEventListener('click', maxbot_shutdown_api);
pause_button.addEventListener('click', maxbot_pause_api);
resume_button.addEventListener('click', maxbot_resume_api);
ocr_captcha_use_public_server.addEventListener('change', checkUsePublicServer);

const onchange_tag_list = ["input","select","textarea"];
onchange_tag_list.forEach((tag) => {
    const input_items = document.querySelectorAll(tag);
    input_items.forEach((userItem) => {
        userItem.addEventListener('change', check_unsaved_fields);
    });
});

homepage.addEventListener('keyup', check_unsaved_fields);
