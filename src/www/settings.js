
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
const refresh_datetime = document.querySelector('#refresh_datetime');
const date_select_mode = document.querySelector('#date_select_mode');
const date_keyword = document.querySelector('#date_keyword');
const date_auto_fallback = document.querySelector('#date_auto_fallback');
const area_select_mode = document.querySelector('#area_select_mode');
const area_keyword = document.querySelector('#area_keyword');
const area_auto_fallback = document.querySelector('#area_auto_fallback');
const keyword_exclude = document.querySelector('#keyword_exclude');

// advance
const browser = document.querySelector('#browser');
const webdriver_type = document.querySelector('#webdriver_type');
const play_ticket_sound = document.querySelector('#play_ticket_sound');
const play_order_sound = document.querySelector('#play_order_sound');
const play_sound_filename = document.querySelector('#play_sound_filename');
const discord_webhook_url = document.querySelector('#discord_webhook_url');

const auto_press_next_step_button = document.querySelector('#auto_press_next_step_button');
const max_dwell_time = document.querySelector('#max_dwell_time');

const auto_reload_page_interval = document.querySelector('#auto_reload_page_interval');
const reset_browser_interval = document.querySelector('#reset_browser_interval');
const server_port = document.querySelector('#server_port');
const proxy_server_port = document.querySelector('#proxy_server_port');
const window_size = document.querySelector('#window_size');
const chrome_extension = document.querySelector('#chrome_extension');
const disable_adjacent_seat = document.querySelector('#disable_adjacent_seat');

const hide_some_image = document.querySelector('#hide_some_image');
const block_facebook_network = document.querySelector('#block_facebook_network');
const headless = document.querySelector('#headless');
const verbose = document.querySelector('#verbose');


const ocr_captcha_enable = document.querySelector('#ocr_captcha_enable');
const ocr_captcha_image_source = document.querySelector('#ocr_captcha_image_source');
const ocr_captcha_force_submit = document.querySelector('#ocr_captcha_force_submit');
const remote_url = document.querySelector('#remote_url');
const ocr_model_path = document.querySelector('#ocr_model_path');

// dictionary
const user_guess_string = document.querySelector('#user_guess_string');
const auto_guess_options = document.querySelector('#auto_guess_options');


// user info - personal data
const real_name = document.querySelector('#real_name');
const phone = document.querySelector('#phone');
const credit_card_prefix = document.querySelector('#credit_card_prefix');

// auto fill
const tixcraft_sid = document.querySelector('#tixcraft_sid');
const ibonqware = document.querySelector('#ibonqware');
const funone_session_cookie = document.querySelector('#funone_session_cookie');
const fansigo_cookie = document.querySelector('#fansigo_cookie');
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
const discount_code = document.querySelector('#discount_code');
const urbtix_password = document.querySelector('#urbtix_password');
const hkticketing_password = document.querySelector('#hkticketing_password');

// runtime
const idle_keyword = document.querySelector('#idle_keyword');
const resume_keyword = document.querySelector('#resume_keyword');
const idle_keyword_second = document.querySelector('#idle_keyword_second');
const resume_keyword_second = document.querySelector('#resume_keyword_second');
const dark_mode_toggle = document.querySelector('#dark_mode_toggle');
const theme_status = document.querySelector('#theme_status');

var settings = null;

maxbot_load_api();

// Keyword conversion functions (aligned with util.py logic)
function format_keyword_for_display(keyword_string) {
    // Convert JSON format to user display format
    // Input:  "AA BB","CC","DD"
    // Output: AA BB;CC;DD
    if (!keyword_string || keyword_string.length === 0) {
        return '';
    }

    // Replace "," or ',' with ";" or ';' (convert delimiter)
    keyword_string = keyword_string.replace(/","/g, '";').replace(/','/, "';");

    // Remove all quotes for display
    keyword_string = keyword_string.replace(/["']/g, '');

    return keyword_string;
}

function format_config_keyword_for_json(user_input) {
    // Convert user input to JSON format
    // Input:  AA BB;CC;DD
    // Output: "AA BB","CC","DD"
    if (!user_input || user_input.length === 0) {
        return '';
    }

    // Remove any existing quotes first
    user_input = user_input.replace(/["']/g, '');

    // Use semicolon as the ONLY delimiter (Issue #23)
    if (user_input.includes(';')) {
        const items = user_input.split(';')
            .map(item => item.trim())
            .filter(item => item.length > 0);
        return items.map(item => `"${item}"`).join(',');
    } else {
        return `"${user_input.trim()}"`;
    }
}

// Toggle Cityline login hint visibility based on account input
function updateCitylineHintVisibility() {
    const citylineHint = document.querySelector('#cityline-login-hint');
    if (citylineHint && cityline_account) {
        citylineHint.style.display = cityline_account.value.trim() !== '' ? '' : 'none';
    }
}

// Check if URL is Tixcraft family (tixcraft.com, teamear.com, indievox.com)
function isTixcraftFamily(url) {
    if (!url) return false;
    const tixcraftDomains = ['tixcraft.com', 'teamear.com', 'indievox.com'];
    return tixcraftDomains.some(domain => url.includes(domain));
}

// Toggle Tixcraft refresh rate warning visibility
function updateTixcraftRefreshWarning() {
    const warningElement = document.getElementById('tixcraft-refresh-warning');
    if (!warningElement) return;

    const url = homepage.value;
    const interval = parseFloat(auto_reload_page_interval.value);

    // Show warning if: Tixcraft family site AND refresh interval < 8 seconds
    const shouldShowWarning = isTixcraftFamily(url) && !isNaN(interval) && interval > 0 && interval < 8;

    if (shouldShowWarning) {
        warningElement.style.display = 'block';
        setTimeout(() => {
            warningElement.classList.add('show');
        }, 10);
    } else {
        if (warningElement.classList.contains('show')) {
            warningElement.classList.remove('show');
            setTimeout(() => {
                warningElement.style.display = 'none';
            }, 150);
        }
    }
}

function load_settins_to_form(settings)
{
    if (settings)
    {
        //console.log("ticket_number:"+ settings.ticket_number);
        // preference
        homepage.value = settings.homepage;
        ticket_number.value = settings.ticket_number;
        refresh_datetime.value = settings.refresh_datetime;
        date_select_mode.value = settings.date_auto_select.mode;
        date_keyword.value = format_keyword_for_display(settings.date_auto_select.date_keyword);
        date_auto_fallback.checked = settings.date_auto_fallback || false;

        area_select_mode.value = settings.area_auto_select.mode;
        area_keyword.value = format_keyword_for_display(settings.area_auto_select.area_keyword);
        area_auto_fallback.checked = settings.area_auto_fallback || false;

        keyword_exclude.value = format_keyword_for_display(settings.keyword_exclude);
        
        // advanced
        browser.value = settings.browser;
        webdriver_type.value = settings.webdriver_type;
        
        play_ticket_sound.checked = settings.advanced.play_sound.ticket;
        play_order_sound.checked = settings.advanced.play_sound.order;
        play_sound_filename.value = settings.advanced.play_sound.filename;
        discord_webhook_url.value = settings.advanced.discord_webhook_url || '';

        auto_press_next_step_button.checked = settings.kktix.auto_press_next_step_button;
        max_dwell_time.value = settings.kktix.max_dwell_time;

        auto_reload_page_interval.value = settings.advanced.auto_reload_page_interval;
        reset_browser_interval.value = settings.advanced.reset_browser_interval;
        server_port.value = settings.advanced.server_port || 16888;
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

        // custom OCR model path
        if(settings.ocr_captcha.path) {
            ocr_model_path.value = settings.ocr_captcha.path;
        } else {
            ocr_model_path.value = "";
        }

        // dictionary
        user_guess_string.value = format_keyword_for_display(settings.advanced.user_guess_string);
        auto_guess_options.checked = settings.advanced.auto_guess_options;

        // contact info
        if (settings.contact) {
            real_name.value = settings.contact.real_name || '';
            phone.value = settings.contact.phone || '';
            credit_card_prefix.value = settings.contact.credit_card_prefix || '';
        }

        // auto fill (accounts section)
        tixcraft_sid.value = settings.accounts.tixcraft_sid;
        ibonqware.value = settings.accounts.ibonqware;
        funone_session_cookie.value = settings.accounts.funone_session_cookie || '';
        fansigo_cookie.value = settings.accounts.fansigo_cookie || '';
        facebook_account.value = settings.accounts.facebook_account;
        kktix_account.value = settings.accounts.kktix_account;
        fami_account.value = settings.accounts.fami_account;
        kham_account.value = settings.accounts.kham_account;
        ticket_account.value = settings.accounts.ticket_account;
        udn_account.value = settings.accounts.udn_account;
        ticketplus_account.value = settings.accounts.ticketplus_account;
        cityline_account.value = settings.accounts.cityline_account;
        urbtix_account.value = settings.accounts.urbtix_account;
        hkticketing_account.value = settings.accounts.hkticketing_account;

        facebook_password.value = settings.accounts.facebook_password;
        kktix_password.value = settings.accounts.kktix_password;
        fami_password.value = settings.accounts.fami_password;
        kham_password.value = settings.accounts.kham_password;
        ticket_password.value = settings.accounts.ticket_password;
        udn_password.value = settings.accounts.udn_password;
        ticketplus_password.value = settings.accounts.ticketplus_password;
        discount_code.value = settings.advanced.discount_code || '';
        urbtix_password.value = settings.accounts.urbtix_password;
        hkticketing_password.value = settings.accounts.hkticketing_password;

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
        } else if(idle_keyword_second.value && idle_keyword_second.value.includes('","')) {
            // 新增：簡化顯示格式 "00","30","50" → 00,30,50
            idle_keyword_second.value = idle_keyword_second.value.replace(/"/g, '');
        }
        resume_keyword_second.value = settings.advanced.resume_keyword_second;
        if(resume_keyword_second.value=='""') {
            resume_keyword_second.value='';
        } else if(resume_keyword_second.value && resume_keyword_second.value.includes('","')) {
            // 新增：簡化顯示格式
            resume_keyword_second.value = resume_keyword_second.value.replace(/"/g, '');
        }

        // Update Cityline hint visibility after loading settings
        updateCitylineHintVisibility();

        // Update Tixcraft refresh warning after loading settings
        updateTixcraftRefreshWarning();
    } else {
        console.log('no settings found');
    }
}

function maxbot_load_api()
{
    let api_url = "/load";
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
    let api_url = "/reset";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        //console.log(data);
        settings = data;
        load_settins_to_form(data);
        check_unsaved_fields();
        run_message("已重設為預設值");
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
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
    run_message("啟動 MaxBot 主程式中...");
    save_changes_to_dict(true);
    maxbot_save_api(maxbot_run_api);
}

function maxbot_run_api()
{
    let api_url = "/run";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        run_message("啟動指令已發送，請稍候瀏覽器視窗開啟...");
        console.log("[MaxBot] Launch API response:", data);
    })
    .fail(function(xhr, status, error) {
        run_message("啟動失敗：無法連線到後端服務 (" + status + ")");
        console.error("[MaxBot] Launch API error:", status, error);
        console.error("[MaxBot] Response content:", xhr.responseText);
    })
    .always(function() {
        //alert( "finished" );
    });
}

function maxbot_shutdown_api()
{
    let api_url = "/shutdown";
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
            settings.refresh_datetime = refresh_datetime.value;
            settings.date_auto_select.mode = date_select_mode.value;
            settings.date_auto_select.date_keyword = format_config_keyword_for_json(date_keyword.value);
            settings.date_auto_fallback = date_auto_fallback.checked;

            settings.area_auto_select.mode = area_select_mode.value;
            settings.area_auto_select.area_keyword = format_config_keyword_for_json(area_keyword.value);
            settings.area_auto_fallback = area_auto_fallback.checked;

            settings.keyword_exclude = format_config_keyword_for_json(keyword_exclude.value);

            // advanced
            settings.browser = browser.value;
            settings.webdriver_type = webdriver_type.value;
        
            settings.advanced.play_sound.ticket = play_ticket_sound.checked;
            settings.advanced.play_sound.order = play_order_sound.checked;
            settings.advanced.play_sound.filename = play_sound_filename.value;
            settings.advanced.discord_webhook_url = discord_webhook_url.value;

            settings.kktix.auto_press_next_step_button = auto_press_next_step_button.checked;
            settings.kktix.max_dwell_time = parseInt(max_dwell_time.value);

            settings.advanced.auto_reload_page_interval = Number(auto_reload_page_interval.value);
            settings.advanced.reset_browser_interval = parseInt(reset_browser_interval.value);
            settings.advanced.server_port = parseInt(server_port.value) || 16888;
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

            // custom OCR model path (migrated from advanced.ocr_model_path)
            settings.ocr_captcha.path = ocr_model_path.value;
            // Remove deprecated field if exists
            if (settings.advanced && settings.advanced.ocr_model_path !== undefined) {
                delete settings.advanced.ocr_model_path;
            }

            // dictionary
            settings.advanced.user_guess_string = format_config_keyword_for_json(user_guess_string.value);

            settings.advanced.auto_guess_options = auto_guess_options.checked;

            // contact info
            if (!settings.contact) settings.contact = {};
            settings.contact.real_name = real_name.value;
            settings.contact.phone = phone.value;
            settings.contact.credit_card_prefix = credit_card_prefix.value;

            // auto fill (accounts section)
            settings.accounts.tixcraft_sid = tixcraft_sid.value;
            settings.accounts.ibonqware = ibonqware.value;
            settings.accounts.funone_session_cookie = funone_session_cookie.value;
            settings.accounts.fansigo_cookie = fansigo_cookie.value;
            settings.accounts.facebook_account = facebook_account.value;
            settings.accounts.kktix_account = kktix_account.value;
            settings.accounts.fami_account = fami_account.value;
            settings.accounts.kham_account = kham_account.value;
            settings.accounts.ticket_account = ticket_account.value;
            settings.accounts.udn_account = udn_account.value;
            settings.accounts.ticketplus_account = ticketplus_account.value;
            settings.accounts.cityline_account = cityline_account.value;
            settings.accounts.urbtix_account = urbtix_account.value;
            settings.accounts.hkticketing_account = hkticketing_account.value;

            settings.accounts.facebook_password = facebook_password.value;
            settings.accounts.kktix_password = kktix_password.value;
            settings.accounts.fami_password = fami_password.value;
            settings.accounts.kham_password = kham_password.value;
            settings.accounts.ticket_password = ticket_password.value;
            settings.accounts.udn_password = udn_password.value;
            settings.accounts.ticketplus_password = ticketplus_password.value;
            settings.advanced.discount_code = discount_code.value;
            settings.accounts.urbtix_password = urbtix_password.value;
            settings.accounts.hkticketing_password = hkticketing_password.value;

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
    let api_url = "/save";
    if(settings) {
        $.post( api_url, JSON.stringify(settings), function() {
            //alert( "success" );
        })
        .done(function(data) {
            console.log("[MaxBot] 設定儲存成功");
            check_unsaved_fields();
            if(callback) callback();
        })
        .fail(function(xhr, status, error) {
            console.error("[MaxBot] Save API error:", status, error);
            console.error("[MaxBot] Response content:", xhr.responseText);
            run_message("儲存失敗：" + status);
        })
        .always(function() {
            //alert( "finished" );
        });
    }
}

function maxbot_pause_api()
{
    let api_url = "/pause";
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
    let api_url = "/resume";
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
    run_message("儲存中...");
    save_changes_to_dict(true);  // silent mode - don't show modal
    maxbot_save_api(function() {
        run_message("已存檔");
    });
}

function check_unsaved_fields()
{
    if(settings) {
        const field_list_basic = ["homepage","ticket_number","refresh_datetime","browser","webdriver_type"];
        field_list_basic.forEach(f => {
            const field = document.querySelector('#'+f);
            if(field.value != settings[f]) {
                $("#"+f).addClass("is-invalid");
            } else {
                $("#"+f).removeClass("is-invalid");
            }
        });
        const field_list_accounts = [
            "tixcraft_sid",
            "ibonqware",
            "funone_session_cookie",
            "fansigo_cookie",
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
            "ticketplus_password"
        ];
        field_list_accounts.forEach(f => {
            const field = document.querySelector('#'+f);
            let formated_input = field.value;
            let formated_saved_value = settings["accounts"][f];
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
                $("#"+f).addClass("is-invalid");
            } else {
                $("#"+f).removeClass("is-invalid");
            }
        });
        const field_list_advance = [
            "user_guess_string",
            "remote_url",
            "auto_reload_page_interval",
            "reset_browser_interval",
            "proxy_server_port",
            "window_size",
            "idle_keyword",
            "resume_keyword",
            "idle_keyword_second",
            "resume_keyword_second",
            "discount_code"
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
            // for cityline.
            if(homepage.value.indexOf("cityline.com") > 0) {
                $("#webdriver_type").val("nodriver");
            }
        }
    }
}

function maxbot_status_api()
{
    let api_url = "/status";
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
        $("#last_url").text(data.last_url);
        $("#maxbot_status").html(status_text).prop( "class", status_class);
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

function maxbot_version_api()
{
    let api_url = "/version";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        $("#maxbot_version").html(data.version);
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

maxbot_version_api();

run_button.addEventListener('click', maxbot_launch);
save_button.addEventListener('click', maxbot_save);
reset_button.addEventListener('click', maxbot_reset_api);
exit_button.addEventListener('click', maxbot_shutdown_api);
pause_button.addEventListener('click', maxbot_pause_api);
resume_button.addEventListener('click', maxbot_resume_api);

const onchange_tag_list = ["input","select","textarea"];
onchange_tag_list.forEach((tag) => {
    const input_items = document.querySelectorAll(tag);
    input_items.forEach((userItem) => {
        userItem.addEventListener('change', check_unsaved_fields);
    });
});

homepage.addEventListener('keyup', check_unsaved_fields);

let runMessageClearTimer;

function run_message(msg)
{
    clearTimeout(runMessageClearTimer);
    const message = document.querySelector('#run_btn_pressed_message');
    message.innerText = msg;
    runMessageClearTimer = setTimeout(function ()
        {
            message.innerText = '';
        }, 3000);
}

function home_tab_clicked() {
    document.getElementById("homepage").focus();
}

// Dark Mode Functions
function initTheme() {
    // Check if user has a saved preference
    const savedTheme = localStorage.getItem('theme');

    // If no saved preference, check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');

    // Apply theme
    applyTheme(theme);

    // Update toggle state
    dark_mode_toggle.checked = (theme === 'dark');
    updateThemeStatus(theme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
}

function updateThemeStatus(theme) {
    // Update status badge if it exists (optional display element)
    if (theme_status) {
        if (theme === 'dark') {
            theme_status.textContent = '已啟用';
            theme_status.className = 'badge bg-success ms-2';
        } else {
            theme_status.textContent = '已關閉';
            theme_status.className = 'badge bg-secondary ms-2';
        }
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    applyTheme(newTheme);
    updateThemeStatus(newTheme);
}

// Initialize theme on page load
initTheme();

// Add event listener for theme toggle
dark_mode_toggle.addEventListener('change', toggleTheme);

// ========================================
// Question Detection Feature
// ========================================

let questionCheckInterval = null;
let lastDetectedQuestion = '';

/**
 * Check if MAXBOT_QUESTION.txt exists and display the question
 */
async function checkDetectedQuestion() {
    try {
        const response = await fetch('/question');
        const data = await response.json();

        const alertElement = document.getElementById('detected-question-alert');
        const questionTextElement = document.getElementById('detected-question-text');

        if (data.exists && data.question) {
            // Only update if question content changed
            if (data.question !== lastDetectedQuestion) {
                lastDetectedQuestion = data.question;

                // Update question text
                questionTextElement.textContent = data.question;

                // Show alert with fade-in effect
                alertElement.style.display = 'block';
                setTimeout(() => {
                    alertElement.classList.add('show');
                }, 10);

                // Auto-scroll to the alert if verification tab is active
                const verificationTab = document.getElementById('verification-tab');
                if (verificationTab.classList.contains('active')) {
                    alertElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }

                console.log('[QUESTION DETECTED]', data.question);
            }
        } else {
            // Hide alert if no question or file doesn't exist
            if (alertElement.classList.contains('show')) {
                alertElement.classList.remove('show');
                setTimeout(() => {
                    alertElement.style.display = 'none';
                }, 150);
                lastDetectedQuestion = '';
            }
        }
    } catch (error) {
        console.error('[QUESTION CHECK] Error:', error);
    }
}

/**
 * Start polling for question detection
 */
function startQuestionPolling() {
    // Check immediately
    checkDetectedQuestion();

    // Then check every 0.5 seconds
    if (!questionCheckInterval) {
        questionCheckInterval = setInterval(checkDetectedQuestion, 500);
        console.log('[QUESTION POLLING] Started (every 0.5 seconds)');
    }
}

/**
 * Stop polling
 */
function stopQuestionPolling() {
    if (questionCheckInterval) {
        clearInterval(questionCheckInterval);
        questionCheckInterval = null;
        console.log('[QUESTION POLLING] Stopped');
    }
}

// Start polling when page loads
startQuestionPolling();

// Cityline login hint visibility control
if (cityline_account) {
    cityline_account.addEventListener('input', updateCitylineHintVisibility);
}

// Tixcraft refresh warning visibility control
if (homepage) {
    homepage.addEventListener('input', updateTixcraftRefreshWarning);
    homepage.addEventListener('change', updateTixcraftRefreshWarning);
}
if (auto_reload_page_interval) {
    auto_reload_page_interval.addEventListener('input', updateTixcraftRefreshWarning);
    auto_reload_page_interval.addEventListener('change', updateTixcraftRefreshWarning);
}

// Also check when verification tab is clicked
const verificationTab = document.getElementById('verification-tab');
if (verificationTab) {
    verificationTab.addEventListener('click', () => {
        // Force check immediately when tab is clicked
        checkDetectedQuestion();
    });
}

// Search button handlers
async function searchQuestion(engine, event) {
    const questionText = document.getElementById('detected-question-text').textContent.trim();
    if (!questionText) {
        console.warn('[SEARCH] No question text available');
        return;
    }

    // AI prompt for direct answers
    const aiPrompt = "Answer this question directly in the same language as the question, provide only the answer without explanation:\n\n";

    // Determine if this is an AI service (needs prompt) or search engine (no prompt)
    const isAI = ['perplexity', 'chatgpt', 'grok', 'claude'].includes(engine);
    const fullQuestion = isAI ? aiPrompt + questionText : questionText;
    const encodedQuestion = encodeURIComponent(fullQuestion);

    let searchUrl = '';
    let needsCopy = false;

    switch (engine) {
        case 'google':
            searchUrl = `https://www.google.com/search?q=${encodeURIComponent(questionText)}`;
            break;
        case 'bing':
            searchUrl = `https://www.bing.com/search?q=${encodeURIComponent(questionText)}`;
            break;
        case 'perplexity':
            searchUrl = `https://www.perplexity.ai/?q=${encodedQuestion}`;
            break;
        case 'chatgpt':
            searchUrl = `https://chatgpt.com?q=${encodedQuestion}`;
            break;
        case 'claude':
            searchUrl = 'https://claude.ai/new';
            needsCopy = true;
            break;
        case 'grok':
            searchUrl = `https://grok.com?q=${encodedQuestion}`;
            break;
        default:
            console.error('[SEARCH] Unknown search engine:', engine);
            return;
    }

    // Check if Ctrl/Cmd/Middle-click (should open in background)
    const openInBackground = event && (event.ctrlKey || event.metaKey || event.button === 1);

    // For AI services, copy question to clipboard
    if (needsCopy) {
        try {
            await navigator.clipboard.writeText(fullQuestion);
            console.log(`[SEARCH] Question copied to clipboard for ${engine}`);

            // Only show notification if not opening in background
            if (!openInBackground) {
                const alertElement = document.getElementById('detected-question-alert');
                const originalText = alertElement.querySelector('h5').innerHTML;
                alertElement.querySelector('h5').innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-check-circle-fill me-2" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg>問題已複製！請貼上到 ${engine.toUpperCase()}`;

                // Restore original text after 2 seconds
                setTimeout(() => {
                    alertElement.querySelector('h5').innerHTML = originalText;
                }, 2000);
            }
        } catch (err) {
            console.error('[SEARCH] Failed to copy to clipboard:', err);
            if (!openInBackground) {
                alert(`無法自動複製問題。請手動複製：\n\n${fullQuestion}`);
            }
        }
    }

    console.log(`[SEARCH] Opening ${engine}:`, searchUrl, openInBackground ? '(background)' : '(foreground)');

    // Open the URL
    // Note: window.open() behavior with Ctrl/Cmd is browser-dependent
    // Most modern browsers will open in background automatically when Ctrl/Cmd is pressed
    window.open(searchUrl, '_blank', 'noopener,noreferrer');
}

// Attach search button event listeners (pass event object)
document.getElementById('search-google-btn')?.addEventListener('click', (e) => searchQuestion('google', e));
document.getElementById('search-bing-btn')?.addEventListener('click', (e) => searchQuestion('bing', e));
document.getElementById('search-perplexity-btn')?.addEventListener('click', (e) => searchQuestion('perplexity', e));
document.getElementById('search-chatgpt-btn')?.addEventListener('click', (e) => searchQuestion('chatgpt', e));
document.getElementById('search-claude-btn')?.addEventListener('click', (e) => searchQuestion('claude', e));
document.getElementById('search-grok-btn')?.addEventListener('click', (e) => searchQuestion('grok', e));

// Also handle middle-click (button 1) for all search buttons
const searchButtons = [
    'search-google-btn', 'search-bing-btn', 'search-perplexity-btn',
    'search-chatgpt-btn', 'search-claude-btn', 'search-grok-btn'
];
searchButtons.forEach(btnId => {
    const btn = document.getElementById(btnId);
    const engine = btnId.replace('search-', '').replace('-btn', '');
    btn?.addEventListener('mousedown', (e) => {
        if (e.button === 1) { // Middle mouse button
            e.preventDefault();
            searchQuestion(engine, e);
        }
    });
});

// TixCraft SID validation
if (tixcraft_sid) {
    tixcraft_sid.addEventListener('input', () => {
        const warningElement = document.getElementById('tixcraft-sid-warning');
        const value = tixcraft_sid.value.trim();

        if (value.startsWith('g.')) {
            // Show warning with fade-in effect
            warningElement.style.display = 'block';
            setTimeout(() => {
                warningElement.classList.add('show');
            }, 10);
        } else {
            // Hide warning with fade-out effect
            if (warningElement.classList.contains('show')) {
                warningElement.classList.remove('show');
                setTimeout(() => {
                    warningElement.style.display = 'none';
                }, 150);
            }
        }
    });
}

// Clean up when page unloads
window.addEventListener('beforeunload', () => {
    stopQuestionPolling();
});