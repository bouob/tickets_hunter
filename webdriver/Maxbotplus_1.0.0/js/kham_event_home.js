$a_btn=$("#content").find("p > a > button[onclick]");
if($a_btn.length>0) {
	$click_event=$a_btn.attr("onclick");
	$a_btn.click();
}
