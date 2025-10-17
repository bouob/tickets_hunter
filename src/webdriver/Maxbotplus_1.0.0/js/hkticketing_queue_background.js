const storage = chrome.storage.local;
var settings = null;

function hkticketing_msg_start(status)
{
    if(settings) {
        let settings_div="<div style='display:none' id='settings'>" + JSON.stringify(settings) + "</div>";
        $("body").append(settings_div);
        let status_div="<div style='display:none' id='status'>" + status + "</div>";
        $("body").append(status_div);
        console.log("dom append");
    }
}

storage.get('settings', function (items)
{
    if (items.settings)
    {
        settings = items.settings;
    }
});

storage.get('status', function (items)
{
    if (items.status && items.status=='ON')
    {
        hkticketing_msg_start(items.status);
    } else {
        console.log('no status found');
    }
});

