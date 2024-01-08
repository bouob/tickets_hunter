(function () {
    const currentUrl = window.location.href; 
    const event_code = currentUrl.split('/')[5];
    //console.log(currentUrl);
    //console.log(event_code);
    if(event_code){
        let domain = currentUrl.split('/')[2];
        let new_url = "https://"+ domain +"/activity/game/"+ event_code;
        location.href=new_url;
    }
})();
