$('input[type=checkbox]').each(function ()
{
    $(this).prop('checked', true);
}
);
$("img[style='width: 100%; padding: 0;']").hide();
$("footer").hide();

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

function initSettings()
{
    fetch(chrome.extension.getURL("/data/settings.json"))
    .then((resp) => resp.json())
    .then((settings) =>
    {
        assign_ticket_number(settings.ticket_number);
    }
    );
}
initSettings();
