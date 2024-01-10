const https_url="https://";
const http_url="https://";

class HeartBeatConnector
{
    constructor() {
    }

    start() {
        //console.log("start heart beat connector");
        //load_font.loadFont();

        sync_status_from_parent();

        // Query the active tab before injecting the content script
        /*
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
        */
    }
}

function set_status_to(flag)
{
    let nextState = 'ON';
    if(!flag) {
        nextState = 'OFF';
    }

    //console.log(nextState);
    chrome.action.setBadgeText({
        text: nextState
    });

    chrome.storage.local.set(
    {
        status: nextState
    }
    );
}

function sync_status_from_parent()
{
    //console.log("sync_status_from_parent");

    let data_url = chrome.runtime.getURL("data/status.json");
    fetch(data_url)
    .then(response => {
        if (response.ok) {
          return response.json()
        } else if(response.status === 404) {
          return Promise.reject('error 404')
        } else {
          return Promise.reject('some other error: ' + response.status)
        }
        })
    .then((data) =>
    {
    console.log(data);
        if(data) {
            set_status_to(data.status);
        }
    })
    .catch(error => {
        //console.log('error is', error)
    });
}

function ack() {
    //console.log("act");
}

export default new HeartBeatConnector();
