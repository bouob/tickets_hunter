'use strict';
var settings = null;
var maxbot_status = null;

var retry_count =0;

function get_event_status_entry(real_event_id, real_session_id) {
    //console.log("start to get_event_status");

    if (maxbot_status =='ON')
    {
        get_event_status_core(real_event_id, real_session_id);
    } else {
        console.log('no status found');
    }
}

function ajax_return_done(data, real_event_id, real_session_id) {
    //console.log("ajax return done")
    let reload=false;
    //console.log(data.result);
    if(data.result.session[0].status=="pending" || data.result.session[0].status=="soldout" || data.result.session[0].status=="unavailable") {
        reload=true;
    }

    //console.log("is_match_reload_status:"+is_match_reload_status);
    if(reload) {
        let auto_reload_page_interval = 0.0;
        if(settings) {
            auto_reload_page_interval = settings.advanced.auto_reload_page_interval;
        }
        // PS: ticketplus not able to release memory soon.
        if (auto_reload_page_interval < 0.7) {
            auto_reload_page_interval = 0.7;
        }

        if(auto_reload_page_interval == 0) {
            //console.log('Start to reload now.');
            location.reload();
        } else {
            console.log('We are going to reload after few seconeds.');
            setTimeout(function () {
                //location.reload();
                location.href=location.href;
            }, auto_reload_page_interval * 1000);
        }
    } else {
        if(data.result.session[0].status=="onsale") {
            //console.log("bingo ^_^, onsale")
            //$(function() {
                // console.log("hello ^_^, onsale");
                //let $captcha = $("input[required='required']");
                //console.log($captcha.length);
            //});
        }
    }

}

function get_event_status_core(real_event_id, real_session_id) {
    let timestamp = new Date().getTime();
    timestamp = (timestamp/1000).toFixed()*1000;
    //console.log(timestamp);

    let api_url = "https://apis.ticketplus.com.tw/config/api/v1/get?eventId="+ real_event_id +"&sessionId="+real_session_id+"&_="+timestamp;
    //console.log("calling api:" + api_url);
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        if(data) {
            ajax_return_done(data, real_event_id, real_session_id);
        }
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

async function decrypt_text(event_id, session_id) {
    //console.log("start to decrypt_text");
    let KEY = 'ILOVEFETIXFETIX!';
    const IV = '!@#$FETIXEVENTiv';

    let bundle = {
      action: 'decrypt',
      data: {
        'key': KEY,
        'iv': IV,
        'text': event_id
      }
    };
    let bundle_string = JSON.stringify(bundle);
    const event_answer = await chrome.runtime.sendMessage(bundle);
    //console.log(event_answer);
    if(event_answer) {
        const real_event_id = event_answer.answer;
        //console.log(real_event_id);
        bundle = {
          action: 'decrypt',
          data: {
            'key': KEY,
            'iv': IV,
            'text': session_id
          }
        };
        let session_answer = await chrome.runtime.sendMessage(bundle);
        let real_session_id = session_answer.answer;
        //console.log(real_session_id);
        get_event_status_entry(real_event_id, real_session_id);
    } else {
        console.log("decrypt fail");
    }
}

async function wait_function_ready() {
    const currentUrl = window.location.href;
    const event_id = currentUrl.split('/')[4];
    const session_id = currentUrl.split('/')[5];
    //console.log(event_id);
    //console.log(session_id);
    if(event_id && session_id){
          decrypt_text(event_id, session_id)
    }
}

chrome.storage.local.get('settings', function (items)
{
    if (items.settings)
    {
        settings = items.settings;
    } else {
        console.log('no status found');
    }
});

chrome.storage.local.get('status', function (items)
{
    if (items.status)
    {
        maxbot_status = items.status;
        //console.log("maxbot_status:" + maxbot_status)
        if(maxbot_status =='ON') wait_function_ready();
    } else {
        console.log('no status found');
    }
});
