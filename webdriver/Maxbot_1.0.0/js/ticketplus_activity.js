'use strict';

import { decrypt } from "./vendor/crypto";

console.log('hello');
setTimeout(function () {
	$("#banner").remove();
	$("footer").remove();
	$("#activityInfo").remove();
}, 400);
