function get_target_area_with_order(settings, matched_block)
{
    //console.log(settings);
    let target_area = null;

    if(matched_block.length) {
        let last_index = matched_block.length-1
        let center_index = 0;
        let random_index = 0;
        if(matched_block.length>1) {
            center_index = parseInt(last_index/2);
            random_index = getRandom(0,last_index)
        }
        if(settings.area_auto_select.mode=="from top to bottom")
            target_area = matched_block[0];
        if(settings.area_auto_select.mode=="from bottom to top")
            target_area = matched_block[last_index];
        if(settings.area_auto_select.mode=="center")
            target_area = matched_block[center_index];
        if(settings.area_auto_select.mode=="random")
            target_area = matched_block[random_index];
    }
    return target_area;
}

function get_target_date_with_order(settings, matched_block)
{
    //console.log(settings);
    let target_area = null;

    if(matched_block.length) {
        let last_index = matched_block.length-1
        let center_index = 0;
        let random_index = 0;
        if(matched_block.length>1) {
            center_index = parseInt(last_index/2);
            random_index = getRandom(0,last_index)
        }
        if(settings.date_auto_select.mode=="from top to bottom")
            target_area = matched_block[0];
        if(settings.date_auto_select.mode=="from bottom to top")
            target_area = matched_block[last_index];
        if(settings.date_auto_select.mode=="center")
            target_area = matched_block[center_index];
        if(settings.date_auto_select.mode=="random")
            target_area = matched_block[random_index];
    }

    return target_area;
}

function getRandom(min,max){
    return Math.floor(Math.random()*(max-min+1))+min;
};