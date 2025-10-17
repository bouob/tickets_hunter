function begin()
{
    const settings_div = document.querySelector('#settings');
    const status_div = document.querySelector('#status');
    let settings = JSON.parse(settings_div.innerHTML);
    let status = status_div.innerHTML;
    //console.log("msg");
    //console.log(settings);
    //console.log(status);

    let auto_reload_page_interval = 0.0;
    if(settings) {
        auto_reload_page_interval = settings.advanced.auto_reload_page_interval;
    }

    // too short to cause error.
    if(auto_reload_page_interval < 0.5) {
        auto_reload_page_interval = 0.5;
    }

    if(status=='ON') {
        setInterval(() => {
            //var busyFor = 0;
            reload();
        }, auto_reload_page_interval * 1000);
    }
}

function dom_ready()
{
    //console.log("checking...");
    const settings_div = document.querySelector('#settings');
    if(settings_div) {
        clearInterval(myInterval);
        begin();
    }
}

myInterval = setInterval(() => {
    dom_ready();
}, 100);
