$("#eventLargeCoverUrl").remove();
$("#s_footer").remove();
$("footer").remove();

function dom_ready() {
  let eventId = getUrlParameter('event');
  //let selectedPerfId = 71202;
  var url = contextPath + "/[activityCode]/performance?event=[eventId]&perfId=[perfId]";
  url = url.replace("[activityCode]",activityCode)
      .replace("[eventId]", eventId)
      .replace("[perfId]",selectedPerfId)
  //console.log(url);
  //location.href = url;
}

// not able to redirt, must click reCAPTCAH button.
// dom_ready();

