const storage = chrome.storage.local;

const submitButton = document.querySelector('#save_btn');
const addButton = document.querySelector('#add_btn');
const clearAllButton = document.querySelector('#clear_all_btn');
const new_domain = document.querySelector('#new_domain');

var settings = null;

loadChanges();

submitButton.addEventListener('click', saveChanges);
addButton.addEventListener('click', addDomainClick);
clearAllButton.addEventListener('click', clearAllClick);

async function saveChanges()
{
    if(settings) {
        let domain_filter =[];
        $("#block_domain_list a").each(function ()
        {
            domain_filter.push($(this).attr('data-domain'));
        });
        //console.log(domain_filter);
        settings.domain_filter = domain_filter;

        let bundle = {
          action: 'update_role',
          data: {
            'settings': settings
          }
        };
        const return_answer = await chrome.runtime.sendMessage(bundle);
        console.log(return_answer);

        await storage.set(
        {
            settings: settings
        }
        );
    }
    message('Settings saved');
}

function loadChanges()
{
    storage.get('settings', function (items)
    {
        //console.log(items);
        if (items.settings)
        {
            settings = items.settings
            //message('Loaded saved settings.');
            if(!settings.hasOwnProperty("domain_filter")) {
                settings.domain_filter = [];
            }

            for (let i = 0; i < settings.domain_filter.length; i++) {
                addDomainRow(settings.domain_filter[i]);
            }

            bind_remove_onclick_event();
        } else {
            console.log('no settings found');
            settings = {};
            settings.domain_filter = [];
        }

    }
    );
}

function format_domain_to_tr(user_input_domain) 
{
    let domain_item = "";
    domain_item += '<tr><td>';
    domain_item += '<a href="#" data-domain="'+ user_input_domain +'" data-action="remove">';
    domain_item += '<span class="glyphicon glyphicon-remove add" aria-hidden="true"></span>';
    domain_item += '</a>';
    domain_item += '</td>';
    //domain_item += '<td>';
    //domain_item += '</td>';
    domain_item += '<td>';
    domain_item += user_input_domain;
    domain_item += '</td>';
    domain_item += '</tr>';
    return domain_item;
}

function addDomainRow(user_input_domain)
{
    if(user_input_domain.length > 0) {
        let domain_item = format_domain_to_tr(user_input_domain);
        $(domain_item).appendTo($("#block_domain_list"));
    }
}

function clearAllClick()
{
    $("#block_domain_list").html("");
}

function bind_remove_onclick_event()
{
    $("#block_domain_list a").click(function(event)
    {
       //console.log($(this).html());
        $(this).parent().parent().remove();
    });
}

function addDomainClick()
{
    let text = new_domain.value;
    if(text.length > 0) {
        let eachLine = text.split('\n');
        for(let i = 0, l = eachLine.length; i < l; i++) {
            addDomainRow(eachLine[i]);
        }
        
        // reset
        new_domain.value = "";
    } else {
        new_domain.focus();
    }

    bind_remove_onclick_event();
}

let messageClearTimer;
function message(msg)
{
    clearTimeout(messageClearTimer);
    const message = document.querySelector('#message');
    message.innerText = msg;
    messageClearTimer = setTimeout(function ()
        {
            message.innerText = '';
        }, 3000);
}
