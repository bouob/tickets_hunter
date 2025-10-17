'use strict';
var settings = null;
var maxbot_status = null;

async function ajax_return_done(data, event_id)
{
    //console.log(data);
    if(settings) {
        if(data.sessions) {
            // if, only one event, auto redirect.
            if(data.sessions.length==1) {
                let session_id=data.sessions[0].sessionId;
                if(session_id) {
                    let new_url = "https://ticketplus.com.tw/order/"+ event_id +"/" + session_id;
                    location.href = new_url;
                }
            }
        }
    }
}

async function wait_function_ready() {
    const currentUrl = window.location.href;
    const event_id = currentUrl.split('/')[4];
    if(event_id){
        let api_url = "https://apis.ticketplus.com.tw/config/api/v1/getS3?path=event/"+event_id+"/sessions.json";
        //console.log("calling api:" + api_url);
        $.get( api_url, function() {
                //alert( "success" );
        })
        .done(function(data) {
            //alert( "second success" );
            if(data) {
                ajax_return_done(data, event_id);
            }
        })
        .fail(function() {
            //alert( "error" );
        })
        .always(function() {
            //alert( "finished" );
        });
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
