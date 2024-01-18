const https_url = "https://";
const http_url = "https://";

class HeartBeatConnector
{
    constructor() {}

    start()
    {
        sync_status_from_parent();
    }
}

function set_status_to(flag)
{
    let nextState = 'ON';
    if (!flag)
    {
        nextState = 'OFF';
    }

    //console.log(nextState);
    chrome.action.setBadgeText(
    {
        text: nextState
    }
    );

    chrome.storage.local.set(
    {
        status: nextState
    }
    );
}

function set_webserver_runing_to(flag)
{
    chrome.storage.local.set(
    {
        webserver_runing: flag
    }
    );
}

function sync_status_from_parent()
{
    //console.log("sync_status_from_parent");

    let data_url = chrome.runtime.getURL("data/status.json");
    fetch(data_url)
    .then(response =>
    {
        if (response.ok)
        {
            set_webserver_runing_to(true);
            return response.json()
        }
        else if (response.status === 404)
        {
            set_webserver_runing_to(false);
            return Promise.reject('error 404')
        }
        else
        {
            set_webserver_runing_to(false);
            return Promise.reject('some other error: ' + response.status)
        }
    }
    )
    .then((data) =>
    {
        //console.log(data);
        if (data)
        {
            set_status_to(data.status);
        }
    }
    )
    .catch(error =>
    {
        //console.log('error is', error)
        set_webserver_runing_to(false);
    }
    );
}

function ack()
{
    //console.log("act");
}

export default new HeartBeatConnector();
