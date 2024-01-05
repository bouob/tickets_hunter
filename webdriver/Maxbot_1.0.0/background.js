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

chrome.action.onClicked.addListener(async (tab) => {
    const prevState = await chrome.action.getBadgeText({ tabId: tab.id });
    // Next state will always be the opposite
    const nextState = prevState === 'ON' ? 'OFF' : 'ON';
    chrome.storage.local.set(
    {
        status: nextState
    }
    );

    // Set the action badge to the next state
    await chrome.action.setBadgeText({
      tabId: tab.id,
      text: nextState
    });
});

import heartbeatconnect from './modules/heartbeatconnect.js';

let heartbeatInterval;

async function runHeartbeat()
{
    //console.log("runHeartbeat");
    chrome.storage.local.get('status', function (items)
    {
        console.log(items);
        if (items.status && items.status=='ON')
        {
            heartbeatconnect.start();
        } else {
            console.log('no status found');
        }
    });
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
