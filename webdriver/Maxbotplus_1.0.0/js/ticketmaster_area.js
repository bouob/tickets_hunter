const storage = chrome.storage.local;
var settings = null;

$("footer").remove();

function ticketmaster_assign_ticket_number(settings)
{
    let ticket_options = $("#ticketPriceList select:first option");
    if (ticket_options.length)
    {
        let is_ticket_number_assign = false;
        if (settings.ticket_number > 0)
        {
            ticket_options.each(function ()
            {
                if ($(this).val() == settings.ticket_number)
                {
                    $(this).prop('selected', true);
                    is_ticket_number_assign = true;
                    return false;
                }
            });
        }
        if (!is_ticket_number_assign)
        {
            ticket_options.last().prop('selected', true);
        }
        $("#autoMode").click();
    }
}

var myInterval = null;

function ticketmaster_select_box_ready(settings)
{
    let ret = false;
    let form_select = $("table#ticketPriceList tbody tr td select.form-select");
    if (form_select.length > 0)
    {
        ret = true;
        if (myInterval)
            clearInterval(myInterval);
        ticketmaster_assign_ticket_number(settings);
    }
    //console.log("select_box_ready:"+ret);
    return ret;
}

storage.get('settings', function (items)
{
    if (items.settings)
    {
        settings = items.settings;
    }
    else
    {
        console.log('no settings found');
    }
}
);

storage.get('status', function (items)
{
    if (items.status && items.status == 'ON')
    {
        //console.log("ticket_number:"+ settings.ticket_number);
        if (settings.ticket_number > 0)
        {
            if (!ticketmaster_select_box_ready(settings))
            {
                myInterval = setInterval(() =>
                    {
                        ticketmaster_select_box_ready(settings);
                    }, 100);
            }
        }

    }
    else
    {
        console.log('no status found');
    }
}
);
