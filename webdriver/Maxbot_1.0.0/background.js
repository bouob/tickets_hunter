'use strict';

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
});
