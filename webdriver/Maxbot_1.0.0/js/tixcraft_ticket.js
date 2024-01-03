const storage = chrome.storage.local;
var settings = null;

$('input[type=checkbox]').each(function ()
{
    $(this).prop('checked', true);
}
);
$("img[style='width: 100%; padding: 0;']").remove();
$("footer").remove();

function assign_ticket_number(ticket_number)
{
    if ($("#ticketPriceList select").length > 0)
    {
        let $ticket_options = $("#ticketPriceList select:first option");
        if ($ticket_options.length)
        {
            let is_ticket_number_assign = false;
            if (ticket_number > 0)
            {
                $ticket_options.each(function ()
                {
                    if ($(this).val() == ticket_number)
                    {
                        $(this).prop('selected', true);
                        is_ticket_number_assign = true;
                        return false;
                    }
                }
                );
            }
            if (!is_ticket_number_assign)
            {
                $ticket_options.last().prop('selected', true);
            }
        }
    }
}

storage.get('settings', function (items)
{
    if (items.settings)
    {
        settings = items.settings;
        //console.log("ticket_number:"+ settings.ticket_number);
        assign_ticket_number(settings.ticket_number);
    } else {
        console.log('no settings found');
    }
});
