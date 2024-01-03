/*
 * extension process crashes or your extension is manually stopped at
 * chrome://serviceworker-internals
 */
'use strict';

const storage = chrome.storage.local;

chrome.declarativeNetRequest.onRuleMatchedDebug.addListener((e) => {
  const msg = `Navigation blocked to ${e.request.url} on tab ${e.request.tabId}.`;
  //console.log(msg);
});

chrome.runtime.onInstalled.addListener(function(){
    fetch("data/settings.json")
    .then((resp) => resp.json())
    .then((settings) =>
    {
        chrome.storage.local.set(
        {
            settings: settings
        }
        );
    }
    );

    let default_status='ON';
    chrome.action.setBadgeText({
        text: default_status
    });
    storage.set({status: default_status});
});

chrome.action.onClicked.addListener(async (tab) => {
    const prevState = await chrome.action.getBadgeText({ tabId: tab.id });
    // Next state will always be the opposite
    const nextState = prevState === 'ON' ? 'OFF' : 'ON';
    storage.set({status: nextState});

    // Set the action badge to the next state
    await chrome.action.setBadgeText({
      tabId: tab.id,
      text: nextState
    });
});
