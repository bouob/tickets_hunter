const storage = chrome.storage.local;
var eventDataCache = null;
var performanceDataCache = null;
var selectedPerfId = null;
var perfPriceListMap = null;
var pageLoaded = false;
var eventImageUrl = null;
var perfDisplayStyle = null;
var allPerformanceDataCache = null;
var contextPath = "/utsvInternet";

var showEnlargedImage = function(image){
  if(image === 'event'){
    $('.image').attr('src', eventImageUrl);
  }
  $("#commonImageModal").modal('show');
}

var addToCalendar = function() {
  if(eventDataCache && eventDataCache.eventDate){
    let addToCalButton= document.querySelector('add-to-calendar-button')

    localStorage.getItem('theme-color') == 'black'? addToCalButton.setAttribute('lightMode','dark') : addToCalButton.removeAttribute('lightMode')

    let options = [];
	  options.push('Google|'+ $.i18n("calendar-google"))
	  options.push('iCal|'+ $.i18n("calendar-ical"))
	  options.push('Outlook.com|'+ $.i18n("calendar-outlook"))	
    addToCalButton.setAttribute('options',JSON.stringify(options))
    
    let customLabels = {
      'close': $.i18n("calendar-close"),
      'label.addtocalendar':  $.i18n("calendar-label-addtocalendar")
    };
    addToCalButton.setAttribute('customLabels',JSON.stringify(customLabels))

    let venueNameField = getDataFieldByLang("venueName")
    addToCalButton.setAttribute('location',eventDataCache.venue[venueNameField])

    $("#addToCal").show();

    if(performanceDataCache){
      if(performanceDataCache.performances && performanceDataCache.performances.length > 0) {
      let dates = []
      performanceDataCache.performances.forEach(perf =>{
        let performanceNameField = getDataFieldByLang("performanceName");
        let performanceName = perf[performanceNameField];
  
        if(performanceDataCache.performances.length == 1){
          addToCalButton.setAttribute('name', performanceName)
          addToCalButton.setAttribute('startDate', moment(perf.performanceDate).format("YYYY-MM-DD"))
        }else{
          let prefDate = {
            name: performanceName,
            startDate: moment(perf.performanceDate).format("YYYY-MM-DD")
          }
          dates.push(prefDate)
        }
      })
  
      if(performanceDataCache.performances.length > 1)  addToCalButton.setAttribute('dates',JSON.stringify(dates))
    
      }
    }
  }
}

var fillEventData = function(data) {
  console.log("eventData:", data);
  eventDataCache = data;
  eventImageUrl =  data.eventLargeCoverUrl

  let eventStatues = {"TOBESOLD" : "event-status-tobesold", "SALE" : "event-status-sale", "SOLDOUT" : "event-status-soldout", "EXPIRED" : "event-status-expired"};
  if(data.status=="TOBESOLD") location.reload();
  if(data.status=="SOLDOUT") location.reload();
}

var openWindow = function(url) {
  let citylineWindow = window.open(url,"_blank ","width=1020,height=600,top=0,left=20,resizable=yes,menubar=no,scrollbars=yes,status=yes");
  citylineWindow.focus();
}

var fillPerformanceData = function(data) {
  console.log("eventPerfData:", data);
  performanceDataCache = data;
  perfPriceListMap = new Map();
  //selectedPerfId = null;
  let perfHtml = "";
  if(data.performances && data.performances.length > 0) {

    let fillerPerId = [];
    data.performances.forEach(i => fillerPerId.push(i.performanceId))

    data.performances.forEach(function(perf, i) {      
        perfHtml += getPerfHtml(perf)
      perfPriceListMap.set(perf.performanceId, perf.pricelist);

      if(perfDisplayStyle === 'DEFAULT'){
        if(!selectedPerfId && perf.status != 'SOLDOUT') selectedPerfId = perf.performanceId;
      }else if(perfDisplayStyle === 'CALENDAR'){
        if(!selectedPerfId && perf.status != 'SOLDOUT') selectedPerfId = perf.performanceId;

          if(!fillerPerId.includes(+selectedPerfId)){
            if(perf.status != 'SOLDOUT') selectedPerfId = perf.performanceId;
          }

      }

      /* Google Analytics */
      var formatDate = new Date(perf.performanceDate);
      var item = {
	      id : "[" + eventSynonym + "] " + formatForGoogleAnalytics(formatDate), // 2021/08/14 23:59 (Sat)
	      name : event_en,
	      category : "[" + eventSynonym + "] " + formatForGoogleAnalytics(formatDate),
	      list_position : i
      };
      viewItems.push(item);
      
      if (i == 0) {
      	googleAnalyticViewItem(perf.performanceId, formatForGoogleAnalytics(perf.performanceDate));
      }
    });
    
    googleAnalyticViewItemList();
    
    $(".date-box").html(perfHtml);
    selectPerf();

  }
  else {
    $(".date-title").addClass("d-none");
  }
}

var getPerfById = function(perfId) {
	var perfList = performanceDataCache.performances;
	if(perfList && perfList.length > 0) {
		return perfList.find(perf => perf.performanceId == perfId)
	} else {
		return null;
	}
}

var fillPriceList = function(perfId) {
  let priceList = perfPriceListMap.get(perfId);
  let ticketPriceHtml = getTicketPriceHtml(priceList);
  $(".puchase-bottom").html(ticketPriceHtml);
}

var selectPerf = function() {
  if(selectedPerfId){
	$('button.date-time-position').attr("aria-pressed", false);
    let selectedElement = $("*[data-perf-id='" + selectedPerfId + "']");
    selectedElement.addClass("item-onclick");
    selectedElement.attr("aria-pressed", true);
    fillPriceList(selectedPerfId);
    
    var perf = getPerfById(selectedPerfId);
    if (perf) {    	
    	var perfDate = new Date(perf.performanceDate);
    	googleAnalyticViewItem(selectedPerfId, formatForGoogleAnalytics(perfDate));
    }
  }
}

var getTicketPriceHtml = function(priceList){
  let ticketPriceHtml = "";
  if(priceList){
	priceList.sort((a, b) => (a.price > b.price) ? -1 : 1);
    priceList.forEach(function(pl) {
      let statusHtml = "";
      if(pl.status == 'LIMIT' || pl.status == 'SOLDOUT'){
        statusHtml = '<img class="limited-img" src="./revamp/images/limited2.svg" alt="">';
      }
      ticketPriceHtml += '<button type="button" class="btn btn-outline-primary price-btn" ><div><span>' + getFormattedPrice(pl.price) +'</span>' +statusHtml +  '</div>'+'</button> ';
    });
  }

  ticketPriceHtml = '<div class="price-box">' +
  '	<div class="date-title price-title1" data-i18n="price-title">' + $.i18n("price-title" ) + '</div>' +
  '	<div>'+ ticketPriceHtml + '</div>' +
  '</div>' +
  '<div class="ticketCard"> ' +
  '	<button type="button" class="btn btn-outline-primary purchase-btn" data-i18n="purchase-title">' + $.i18n("purchase-title" ) + '</button>' +
  '</div>';

  return ticketPriceHtml;

}

var postConstruct = function(){
  $(".date-time-position").click(function(){
	$('button.date-time-position').attr("aria-pressed", false);
    $(".item-onclick").removeClass("item-onclick");
    $(this).addClass("item-onclick");
    $(this).attr("aria-pressed", true);
    let perfId = $(this).data("perf-id");
    selectedPerfId = perfId;
    fillPriceList(perfId);
    setPurchaseBtnClick();
  });
  
  $('#likeButton').on('click', function() {
	  var eventId = getUrlParameter('event');
	  if(doLikeThisEvent(eventId))
		  $('.likeIcon').addClass('liked');
  })
  
  setPurchaseBtnClick();  
  if (needToPurchase) {
	  $(".purchase-btn").click();
  }

  // hide presenter if repeated
  if($("[data-i18n=event-presenter]").text() == $("#firstDesc div p:first-child").text()) {
    $("[data-i18n=event-presenter]").parent().hide();
  }
}


var purchaseBtnClick = function() {
	$.LoadingOverlay("show");
	var eventId = getUrlParameter('event');
	var url = contextPath + "/internet/performance?event=[eventId]&perfId=[perfId]";
	url = url.replace("[eventId]", eventId)
			.replace("[perfId]",selectedPerfId)			
	location.href = url;
	$.LoadingOverlay("close");
}

var setPurchaseBtnClick = function() {
  $(".purchase-btn").click(function () {
    if(hasLoggedIn){
    	purchaseBtnClick();
    }
    else {
    	var addParams = [];
    	if(selectedPerfId)
    		addParams.push('perfId=' + selectedPerfId);
    	//console.log('addParams', addParams)
    	loginCallback = purchaseBtnClick;
    	login(true, addParams);
    }
  });
}

var reloadFromCache = function() {
  fillEventData(eventDataCache);
  if(perfDisplayStyle === 'DEFAULT'){
    fillPerformanceData(performanceDataCache);
  }else if(perfDisplayStyle === 'CALENDAR'){
    fillCalendar(allPerformanceDataCache)
  }
  postConstruct();
}

var loadArchiveUrl = function(archiveUrl) {
  $.ajax({
    type : "GET",
    dataType: "json",
    url: archiveUrl,
    async: false,
    global: false,
    cache: true,
    success: function(data) {
      fillEventData(data);
    },
    statusCode: {
      403: function() {
        handleEventNotAvail();
      }
    },
  });
}

var loadData = function() {
  let eventId = getUrlParameter('event');
  if(eventId){
    let eventRequestUrl = contextPath + "/internet/api/event/" + eventId;
    let eventPerfRequestUrl = contextPath + "/internet/api/event/" + eventId + "/performances";
    return $.when($.getJSON(eventRequestUrl)).then(function(data){
      if(data.eventId) fillEventData(data);
      else if (data.archiveUrl){
        //$(".date-title").addClass("d-none");
        loadArchiveUrl(data.archiveUrl);
      }
      else handleEventNotAvail();

      perfDisplayStyle = data.performancesDisplayStyle;
      return $.getJSON(eventPerfRequestUrl);
    }).then(function(data){
      allPerformanceDataCache = data;
    });
  }
  else {
    console.log("no event specified");
  }
}

function cityline_event_status_check()
{
  selectedPerfId = getUrlParameter('perfId');
  if(pageLoaded) {
      reloadFromCache();
  }else{
      pageLoaded = true;
      loadData();
  }
}

storage.get('status', function (items)
{
    if (items.status && items.status=='ON')
    {
        cityline_event_status_check();
    } else {
        console.log('no status found');
    }
});
