$("div#DIV_REMARK").remove();
$("div.footer").remove();

$a_btn=$("#content").find("table.eventTABLE > tbody > tr > td > a > button[onclick]");
if($a_btn.length==1) {
	$a_btn.click();
}
