function get_target_area_with_order(settings, matched_block)
{
    //console.log(settings);
    let target_area = [];

    if(settings.area_auto_select.mode=="from top to bottom")
        target_area = matched_block.first();
    if(settings.area_auto_select.mode=="from bottom to top")
        target_area = matched_block.last();
    if(settings.area_auto_select.mode=="center")
        target_area = matched_block.first();
    if(settings.area_auto_select.mode=="random")
        target_area = matched_block.first();
    return target_area;
}

function get_target_date_with_order(settings, matched_block)
{
    //console.log(settings);
    let target_area = [];

   if(settings.date_auto_select.mode=="from top to bottom")
       target_date = matched_block.first();
   if(settings.date_auto_select.mode=="from bottom to top")
       target_date = matched_block.last();
   if(settings.date_auto_select.mode=="center")
       target_date = matched_block.first();
   if(settings.date_auto_select.mode=="random")
       target_date = matched_block.first();

    return target_area;
}