var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
    return false;
};

var getI18nMonthYear = function(date) {
  let year = date.year;
  let month = date.month - 1;
  let monthTitles = ['month-title-jan', 'month-title-feb', 'month-title-mar', 'month-title-apr', 'month-title-may', 'month-title-jun', 'month-title-jul', 'month-title-aug', 'month-title-sep', 'month-title-oct', 'month-title-Nov', 'month-title-Dec'];
  let monthTitle = monthTitles[month];
  let comma = $.i18n().locale == 'en' ? "," : "，";
  return $.i18n(monthTitle) + comma + " " + year;
}

var getI18nWeek = function(date) {
  let weekDayTitles = ['week-title-sun', 'week-title-mon', 'week-title-tue', 'week-title-wed', 'week-title-thu', 'week-title-fri', 'week-title-sat'];
  let day = date.weekday%7;
  let weekDayTitle = weekDayTitles[day];
  return $.i18n(weekDayTitle);
}

var getI18nTime = function(date) {
  let i18nWeek = getI18nWeek(date);
  let hour = date.hour;
  let hourTitle = (hour < 10) ? "0" + hour : hour;
  let minute = date.minute;
  let minuteTitle = (minute < 10) ? "0" + minute : minute;
  let comma = $.i18n().locale == 'en' ? "," : "，";
  return i18nWeek + comma + " " + hourTitle + ":" + minuteTitle;
}

var getI18nSrDate = function(date) {
	let day = date.day;
	let month = date.month - 1;
	let year = date.year;
	let monthTitles = ['month-title-jan', 'month-title-feb', 'month-title-mar', 'month-title-apr', 'month-title-may', 'month-title-jun', 'month-title-jul', 'month-title-aug', 'month-title-sep', 'month-title-oct', 'month-title-Nov', 'month-title-Dec'];
	let monthTitle = $.i18n().locale == 'en' ? $.i18n(monthTitles[month]) : month + 1;
	return $.i18n('sr-date-format', day, monthTitle, year); // $1=Day, $2=Month, $3=Year
}

var getPerfHtml = function(perf) {
  let status = perf.status;
  let statusTitles = {"AVAILABLE" : null, "LIMIT" : "status-title-limit", "SOLDOUT" : "status-title-soldout"};
  let statusTitle = statusTitles[status];
  let statusValue = statusTitle ? $.i18n(statusTitle) : "";
  let statusHtml = '';
  if(statusValue) {
    statusHtml =  ' <span class="limited">' +
        '			<img class="limited-img" src="./revamp/images/limited1.svg" alt="">' + statusValue + '</span>';
  }

  let innerButtonHtml = '';
  let performanceNameField = getDataFieldByLang("performanceName");
  let performanceName = perf[performanceNameField];
  let performanceNameHtml = ' <span class="concert-title">' + performanceName + '</span>';

  if(perf.performanceDate){
		let performanceDateTz = DateTime.fromMillis(perf.performanceDate).setZone("UTC+8");
    let performanceDateDisplayFormat = perf.performanceDateDisplayFormat;
    let monthYear = getI18nMonthYear(performanceDateTz);
    let date = performanceDateTz.day;
    let time = (performanceDateDisplayFormat == "DISPLAY_FORMAT_NAME_DATE_TIME") ? getI18nTime(performanceDateTz) : getI18nWeek(performanceDateTz);
    let srDate = getI18nSrDate(performanceDateTz);
    let monthYearHtml = 
    	'	<div class="date-left" aria-label="' + srDate + ' ">' +
        '		<span class="month-year"> '  + monthYear + '</span> <span class="day">' + date + '</span>' +
        '	</div>';
    innerButtonHtml += monthYearHtml +
        '	<div class="date-right">' +
        '		<span class="time">' + time +'</span>' + performanceNameHtml + statusHtml +
        '	</div>';
  }
  else {
    innerButtonHtml += ' <span class="concert-title only-title">' + performanceName + '</span>'+ statusHtml;
  }

  let perfId = perf.performanceId;
  let isPurchasable = perf.isPurchasable;
  let disabledHtml = !isPurchasable || perf.status == 'SOLDOUT' ?  'disabled="disabled"' : '';
  let perfHtml = '<button type="button" class="btn btn-outline-primary date-time-position" data-perf-id="' + perfId  + '" ' + disabledHtml + ' aria-pressed="false"> ' + innerButtonHtml + '</button>';

  return perfHtml;
}

let myCalendar = null;
let selDate = null;
var fillCalendar = function(perfData){
	let formattedDatePrefData = perfData.performances.map((item)=>{
		return{
			...item,
			performanceDate: moment(item.performanceDate).format("DD/MM/YYYY")
		}
	})

	let formattedDateArr = perfData.performances.map((item)=>{
		if(item.performanceDate){
			return moment(item.performanceDate).format("DD/MM/YYYY")
		}
	})

	let min = formattedDatePrefData.find(item =>item.status !== "SOLDOUT").performanceDate;
	let max = formattedDatePrefData[formattedDatePrefData.length-1].performanceDate;

	let calendarBox = isMobileFun() ? $('.calendar-box')[0] : $('.calendar-box')[$('.calendar-box').length -1]
	let dateBox = isMobileFun() ? $('.date-box')[0] : $('.date-box')[$('.date-box').length -1];

	$(calendarBox).empty();
	myCalendar = jsCalendar.new(calendarBox, min, {
		"monthFormat": "YYYY/##",
		"dayFormat": "DDD",
	});

	myCalendar.min(min);
	myCalendar.max(max);

	$('.jsCalendar table td').mouseover(function(){
		if(!$(this).hasClass('jsCalendar-previous') && !$(this).hasClass('jsCalendar-next') && !$(this).hasClass('jsCalendar-noPerfDate')){
			let day = $(this)[0].innerText < 10 ? '0'+$(this)[0].innerText : $(this)[0].innerText;
			let date = $('.jsCalendar-title-name')[0].innerText + '/' + day;
			let formatDate = date.split('/').reverse().join('/')
  
			let sameDatePref = fillterCurrentDatePrefList(perfData,formattedDatePrefData,formatDate);
			let sameDatePrefTimes = []
			sameDatePref.performances.forEach(function(perf) {    
			  if(perf.performanceDate){
				  let performanceDateTz = DateTime.fromMillis(perf.performanceDate).setZone("UTC+8");
				  let time = (perf.performanceDateDisplayFormat == "DISPLAY_FORMAT_NAME_DATE_TIME") ? getI18nTime(performanceDateTz) : getI18nWeek(performanceDateTz);
				  let getTime = time.split('， ')[1] ? time.split('， ')[1] : time.split(', ')[1];
				  let getEventName = $('#eventName').text() ? $('#eventName').text() : $('.item-title:visible').text();
				  sameDatePrefTimes.push( getTime + ' ' + getEventName + '<br>');
			  }
			}) 
			let title = sameDatePrefTimes.join('')
			$(this).attr('title', title);
			$(this).attr('data-toggle', 'tooltip');
			$(this).attr('data-placement', 'top');
			$(this).attr('data-html', true);
			$(this).tooltip('show');
		}
	});

	myCalendar.onDateClick(function(event,date){
	  const formatDate = jsCalendar.tools.dateToString(date, "DD/MM/yyyy");

	  let curClickMonth = formatDate.split('/')[1];
	  let curDisplayMonth = $('.jsCalendar-title-name')[0].innerText.split('/')[1];
	  let isCurMonth = curClickMonth == curDisplayMonth ? true : false;

	  selDate = formatDate;
	  if(formattedDateArr.indexOf(formatDate)!== -1 && isCurMonth){
		  myCalendar.clearselect();

		  if($('.jsCalendar-selected').length){
			toSelDate = null;
			$('.jsCalendar-selected')[0].classList.remove('jsCalendar-selected')
		  }
		  myCalendar.select(formatDate);
		  fillterCurrentDatePrefList(perfData,formattedDatePrefData,formatDate)
		  dateBox.classList.remove("d-none")

	  }
	})

	let toSelDate = null;
	if (selectedPerfId) {
		toSelDate = formattedDatePrefData.find(i => i.performanceId == selectedPerfId).performanceDate;
		myCalendar.goto(toSelDate)		
		myCalendar.select(toSelDate)	
    }else{
		myCalendar.goto(selDate);
		selDate ? myCalendar.select(selDate) : myCalendar.select(min);
	}

	myCalendar.onDateRender(function(date, element, info) {
		const formatDate = jsCalendar.tools.dateToString(date, "DD/MM/yyyy");
  
		element.classList.remove('jsCalendar-soldout')
  
		if(formattedDateArr.indexOf(formatDate) === -1){
		  element.classList.add('jsCalendar-noPerfDate')
		}

          let obj = {};
          let newArr = [];
          formattedDatePrefData.forEach(item => {
            if (!obj[item.performanceDate]) {
              var arr = [];
              arr.push(item);
              newArr.push(arr);
              obj[item.performanceDate] = item;
            } else {
              newArr.forEach(function (value, index) {
                if (value[0].performanceDate == item.performanceDate) {
                  value.push(item)
                }
              })
            }
          })

          let soldoutDateArr = []
          newArr.forEach(item =>{
            if(item.every(i => i.status == "SOLDOUT")){
              item.forEach(i => {
                if(soldoutDateArr.indexOf(i.performanceDate) == -1){
                  soldoutDateArr.push(i.performanceDate)
                }
              })
            }
          })

		if(soldoutDateArr.indexOf(formatDate) !== -1){
          element.classList.add('jsCalendar-soldout')
        }
	
        if(document.querySelector('.jsCalendar-selected')!== null && document.querySelector('.jsCalendar-current')!== null){
        	document.querySelector('.jsCalendar-current').classList.remove('jsCalendar-current')
        }

	  	if(element.classList.contains('jsCalendar-selected')){
	  		let sameDatePref = fillterCurrentDatePrefList(perfData,formattedDatePrefData,formatDate)
	  		fillPerformanceData(sameDatePref)
	  		postConstruct()
	  	}

	});
	myCalendar.refresh();   

	changePerfCalendarTheme();
	changePerfCalendarLang();
}

var fillterCurrentDatePrefList = function(perfData,formattedDatePrefData,curDate){
	let sameDatePerfIdArr = []
	formattedDatePrefData.forEach(i =>{
		if(i.performanceDate === curDate){
			return sameDatePerfIdArr.push(i.performanceId)
		}
	})

	let sameDatePref = {}
	sameDatePref.performances = []
	perfData.performances.forEach(pref =>{
		sameDatePerfIdArr.forEach(id =>{
			if(pref.performanceId === id){
				sameDatePref.performances.push(pref)
			}
		})
	})
	return sameDatePref;
}

var changePerfCalendarTheme = function(){
	if(Cookies.get('cl-theme-color') == 'black'){
		document.querySelector('.jsCalendar').classList.remove('grey-theme')
		document.querySelector('.jsCalendar').classList.add('black-theme')
	}else if(Cookies.get('cl-theme-color') == 'night'){
		document.querySelector('.jsCalendar').classList.remove('black-theme')
		document.querySelector('.jsCalendar').classList.add('grey-theme')
	}else{
		document.querySelector('.jsCalendar').classList.remove('black-theme')
		document.querySelector('.jsCalendar').classList.remove('grey-theme')
	}
}

var changePerfCalendarLang = function(){
	if(get_lang() !== 'en'){
		myCalendar.setLanguage("zh")
	}else{
		myCalendar.setLanguage("en")
	}
}

var handleEventNotAvail = function() {
  let html = '<div style="text-align: center" data-i18n="[html]event-not-available-msg">' + $.i18n("event-not-available-msg") +  "</div>";
  $(".main").html(html);
  $("footer").addClass("fixed-bottom");
}


var utsvEventListCache = null;
var eventLikeListCache = null;
var isExpired = function(expiry) {
	return (new Date(expiry) < new Date());
}
var getClUtsvEventByUtsvId = function(utsvId) {
	var result = (!utsvEventListCache) ? null :
		utsvEventListCache.filter(function(val, i) {
			return (val.utsvId == utsvId);
		});
	return (result) ? result[0]: null;
}
var getLikeCountById = function(evtId) {
	var clEvt = getClUtsvEventByUtsvId(evtId);
	var jsonCount = (clEvt) ? clEvt.likeCount : 0;
	var cookieCount = (clEvt) ? Cookies.get('cl-like-' + clEvt.id) || 0 : 0;
	return Math.max(jsonCount, cookieCount);
}
var isLikedEvent = function(evtId) {
	var clEvt = getClUtsvEventByUtsvId(evtId);
	// var cookieLike = (clEvt) ? Cookies.get('cl-like-' + clEvt.id) || 0 : 0;
	// var result = (eventLikeListCache && clEvt) ? eventLikeListCache.indexOf(clEvt.id) : null;
	// return (cookieLike || result >= 0);
	let result
	if(isCitylineLogin){
		result = (eventLikeListCache && clEvt) ? eventLikeListCache.indexOf(clEvt.id) : null;
		return result !== null && result >= 0
	}else{
		var list = JSON.parse(localStorage.getItem("not-login-like-utsvEvent"));
		result = (list && clEvt) ? list.indexOf(clEvt.id) : null;
		return result !== null && result >= 0
	}
}
var drawLikeButton = function(evtId) {
	var likeCount = getLikeCountById(evtId);
	if(likeCount || likeCount == 0)
		$('.likeCount').text(likeCount);
	
	if(isLikedEvent(evtId)) 
		$('.likeIcon').addClass('liked');
	else 
		$('.likeIcon').removeClass('liked');

	if(getClUtsvEventByUtsvId(evtId)) $('#likeButton').show();
}
var getLatestClUtsvEventList = function() {
	// var url =  citylineDomainUrl+'/api/utsvEventList.do';
	var url =  citylineDomainUrl+'/data/utsvEventList.json';
	return $.get({url: url, global: false}, function(data, status) {
		if(data && data.utsvEventList) {
			utsvEventListCache = data.utsvEventList;
			utsvEventListCache = utsvEventListCache.map(function(etv) {
			    var newEvt = {};
			    newEvt['id'] = etv.id;
			    newEvt['utsvId'] = etv.utsvId;
			    newEvt['likeCount'] = etv.likeCount;
			    newEvt['synonym'] = etv.synonym;
			    return newEvt;
			});
			var expiry = 15; // in minutes
			var localList = {
					utsvEventListCache,
					'expiry': new Date(new Date().getTime() + (expiry*60*1000)).getTime()
				}
			localStorage.setItem("like-count-utsvEvent", JSON.stringify(localList));
			
			var eventId = getUrlParameter('event');
			drawLikeButton(eventId);
		}
	}).fail(function(){
		// console.log("failed to call /api/utsvEventList.do");
		console.log("failed to call /data/utsvEventList.json");
	});
}
var getClUtsvEventList = function() {
	var deferred = $.Deferred();
	var list = JSON.parse(localStorage.getItem('like-count-utsvEvent'));
	if (!list || (list.expiry && isExpired(list.expiry))) {
		return getLatestClUtsvEventList();
	} else {
		utsvEventListCache = list.utsvEventListCache;
		var eventId = getUrlParameter('event');
		drawLikeButton(eventId);
		
		return deferred; 
	}
}
var getLatestEventLikeList = function() {
	var url = citylineDomainUrl + '/api/customer/favourite.do';
	return $.get({
		url: url,
		global: false,
		xhrFields: {  
		    withCredentials: true 
		  }
	}, function(data, status) {
		if(data && data.utsvEventIds) {
			eventLikeListCache = data.utsvEventIds;
			var expiry = 15; // in minutes
			var localList = {
					'likeList': eventLikeListCache,
					'expiry': new Date(new Date().getTime() + (expiry*60*1000)).getTime()
				}
			if(isCitylineLogin){
				localStorage.setItem("like-list-utsvEvent", JSON.stringify(localList));
			}
			var eventId = getUrlParameter('event');
			drawLikeButton(eventId);
		}
	}).fail(function(){
		console.log("failed to call /api/customer/favourite.do");
	});
}
var getEventLikeList = function() {
	var deferred = $.Deferred();
	var likeListJson = JSON.parse(localStorage.getItem('like-list-utsvEvent'));
	if (!likeListJson || (likeListJson.expiry && isExpired(likeListJson.expiry))) {
		return getLatestEventLikeList();
	} else {
		eventLikeListCache = likeListJson.likeList;
		var eventId = getUrlParameter('event');
		drawLikeButton(eventId);
		
		return deferred; 
	}
}
var setupLikeFeature = function() {
	$.when(getClUtsvEventList())
		.then(getEventLikeList());
}
var doLikeThisEvent = function(evtId) {
	var clEvt = getClUtsvEventByUtsvId(evtId);
	var isLiked =isLikedEvent(evtId); 
	if(clEvt && !isLiked) {
		var url = citylineDomainUrl + '/api/customer/favourite/utsvEvent/' + clEvt.id + '.do';
		console.log('like!', 'utsvId: ' + evtId, 'revamp id: ' + clEvt.id);
		return $.post({
			url: url,
			xhrFields: {  
			    withCredentials: true 
			  },
			global: false
		}, function(data, status, xhr){
			var clEvtId = clEvt.id
			var expiry = 60;	// in minutes
			var expires = new Date(new Date().getTime() + (expiry*60*1000));
			
			if(isCitylineLogin){

				if(Cookies.get('cl-like-' + clEvt.id)){
					var likeCount = +Cookies.get('cl-like-' + clEvt.id) + 1;
				}else{
					var likeCount = clEvt.likeCount + 1;
				}
				
				getLatestEventLikeList()
			}else{
				var likeCount = clEvt.likeCount + 1;
				var notLoginLikeList = JSON.parse(localStorage.getItem("not-login-like-utsvEvent") || "[]");
				notLoginLikeList.push(clEvtId);
				localStorage.setItem("not-login-like-utsvEvent",JSON.stringify(notLoginLikeList))
			}
			Cookies.set('cl-like-' + clEvtId, likeCount, { expires });
			drawLikeButton(evtId);
			return true;
		}).fail(function() {
			return false;
		});
	}
}