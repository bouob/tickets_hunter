const storage = chrome.storage.local;
var settings = null;

$("footer").remove();

function assign_ticket_number(ticket_number)
{
    let $main_table = $("table.table");
    if ($main_table.length > 0)
    {
        console.log("found main table");
        let $ticket_options = $main_table.find("select:first option");
        if ($ticket_options.length)
        {
            let is_ticket_number_assign = false;
            if (ticket_number > 0)
            {
                console.log("target ticket_number:"+ticket_number);
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
            console.log("is_ticket_number_assign:"+is_ticket_number_assign);
            if (!is_ticket_number_assign)
            {
                $ticket_options.last().prop('selected', true);
            }
        }
    }
}

function assign_adjacent_seat(flag) {
    //console.log("disable_adjacent_seat flag:"+flag);
    if(flag) {
        $('input[type=checkbox]').each(function() {
           $(this).prop('checked', true);
        });
    }
}

function focus_on_captcha()
{
    $("div.editor-box > div > input[type='text']").focus();
}

storage.get('settings', function (items)
{
    if (items.settings)
    {
        settings = items.settings;
        //console.log("ticket_number:"+ settings.ticket_number);
        assign_ticket_number(settings.ticket_number);
        assign_adjacent_seat(settings.advanced.disable_adjacent_seat);
        focus_on_captcha();
    } else {
        console.log('no settings found');
    }
});
