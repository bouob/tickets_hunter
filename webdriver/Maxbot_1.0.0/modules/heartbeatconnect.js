const storage = chrome.storage.local;
var settings=null;
const https_url="https://";
const http_url="https://";

class HeartBeatConnector
{
    constructor() {}

    start() {
        //console.log("start heart beat connector");
        //load_font.loadFont();

        // Query the active tab before injecting the content script
        chrome.tabs.query(
        {
            active: true,
            status: "complete",
            currentWindow: true
        }, (tabs) =>
        {
            if(tabs && tabs.length) {
                //console.log(tabs);
                //console.log(tabs[0]);
                if (tabs[0].url.startsWith(https_url) || tabs[0].url.startsWith(http_url)) {
                    // Use the Scripting API to execute a script
                    chrome.scripting.executeScript(
                    {
                        target:
                        {
                            tabId: tabs[0].id
                        },
                        func: ack
                    }
                    );
                }
            }
        });
    }
}

function ack() {
    //console.log("act");
}

export default new HeartBeatConnector();
