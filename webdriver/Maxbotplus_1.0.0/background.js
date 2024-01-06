/*
 * extension process crashes or your extension is manually stopped at
 * chrome://serviceworker-internals
 */
'use strict';

chrome.runtime.onInstalled.addListener(function(){
    console.log("onInstalled");

    let default_status='ON';
    chrome.action.setBadgeText({
        text: default_status
    });

    fetch("data/settings.json")
    .then((resp) => resp.json())
    .then((settings) =>
    {
        chrome.storage.local.set(
        {
            settings: settings,
            status: default_status
        }
        );
        console.log("dump settings.json to storage");
    }
    );
});

chrome.declarativeNetRequest.onRuleMatchedDebug.addListener((e) => {
  const msg = `Navigation blocked to ${e.request.url} on tab ${e.request.tabId}.`;
  //console.log(msg);
});

function set_status_to(flag)
{
    let nextState = 'ON';
    if(!flag) nextState = 'OFF';

    chrome.storage.local.set(
    {
        status: nextState
    }
    );

    chrome.action.setBadgeText({
        text: nextState
    });
}

chrome.action.onClicked.addListener(async (tab) => {
    chrome.storage.local.get('status', function (items)
    {
        let next_flag = true;
        if (items.status && items.status=='ON')
        {
            next_flag = false;
        }
        console.log("next_flag:"+next_flag);
        set_status_to(next_flag);
    });
});

import heartbeatconnect from './modules/heartbeatconnect.js';

let heartbeatInterval;

async function runHeartbeat()
{
    //console.log("runHeartbeat");
    heartbeatconnect.start();
}

async function startHeartbeat()
{
    runHeartbeat().then(() =>
    {
        heartbeatInterval = setInterval(runHeartbeat, 1 * 1000);
    }
    );
}

async function stopHeartbeat()
{
    clearInterval(heartbeatInterval);
}

startHeartbeat();
