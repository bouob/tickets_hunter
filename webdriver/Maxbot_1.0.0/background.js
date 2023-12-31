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