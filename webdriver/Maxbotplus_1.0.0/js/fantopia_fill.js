const storage = chrome.storage.local;
var settings = null;
var inputInterval = null;

function fantopia_fill_main(settings) {
    if(settings.ticket_number) {
        let current_ticket_number = parseInt($("input.border-0").val());
        for(let i=0; i<settings.ticket_number; i++) {
            current_ticket_number = parseInt($("input.border-0").val());
            if(current_ticket_number >= settings.ticket_number) break;
            $('button > img[src="https://p-st.fantopia.io/icon/add.svg"]').click(); 
        }
        // check overflow
        current_ticket_number = parseInt($("input.border-0").val());
        if(current_ticket_number > settings.ticket_number) {
            $('button > img[src="https://p-st.fantopia.io/icon/reduce.svg"]').click(); 
        } else {
            if(current_ticket_number == settings.ticket_number) {
                $('div.border-t > div.text-right > button.relative > div.flex.items-center.justify-center').click();
            }
        }
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
        inputInterval= setInterval(() => {
            fantopia_fill_main(settings);
        }, 200);
    } else {
        //console.log('maxbot status is not ON');
    }
});
