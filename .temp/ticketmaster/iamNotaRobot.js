function pxLang(a) {
    if (a) a = a.toLowerCase();
    const m = { en: "en", "en-us": "en", it: "it", "it-it": "it", "it-ch": "it", fr: "fr", "fr-ca": "fr-ch", "fr-fr": "fr", "es-mx": "es" };
    var b = m[a];
    if (!b) b = "en";
    return b;
}

function getBaseUrl() {
    return Array.from(document.querySelectorAll("script"))
        .filter((script) => script.hasAttribute("src") && script.getAttribute("src").includes("eps-mgr"))
        .map((script) => {
            const elements = script.getAttribute("src").split("/");
            if (elements.length < 3) {
                return window.location.origin + "/" + "epsf";
            }
            return elements[0] + "//" + elements[2];
        })[0];
}

function iamNotaRobotPX(lang, brand = "api", action = "captcha", epsCaptcha, baseUrl) {
    if (typeof _isPxMobile === "undefined" || _isPxMobile === null) {
        _isPxMobile = 0;
    }
    epsCaptcha.innerHTML =
        "<div class='box'><div class='c1' id='t1'></div><div class='c2' id='t2'></div><ul class='c3' id='t3'></ul><div class='c4' id='t4'></div></div><div class='be'></div><section class='container'><div class='content-wrapper'><div class='content'><div id='captcha-box'></div></div></div><div class='page-footer-wrapper'></div></section><div class='box2'><div class='c5' id='t5'></div><div data-cs-mask class='c6' id='t6'></div></div>";
    const captchaDiv = epsCaptcha.querySelector("#captcha-box");
    captchaDiv.innerHTML =
        '<div id="px-captcha-container"><div class="px-captcha-header"></div><div class="px-captcha-background"></div><div id="px-captcha"></div><div class="px-captcha-message"></div><span class="px-captcha-report"></span></div>';
    window._pxSelectedLocale = pxLang(lang);
    window._pxAppId = _pxAppId;
    window._pxHostUrl = `https://collector-${_pxAppId}.perimeterx.net`;
    window._pxJsClientSrc = `//client.perimeterx.net/${_pxAppId}/main.min.js`;
    window._pxFirstPartyEnabled = "true";
    window._pxTranslation = {
        fr: [
            { selector: ".px-captcha-header", text: "Veuillez vérifier que vous êtes un humain" },
            { selector: ".px-captcha-message", text: "Appuyez et maintenez enfoncé pour confirmer que vous êtes un humain (et non un bot)." },
        ],
        it: [
            { selector: ".px-captcha-header", text: "Per favore verifica di essere un essere umano" },
            { selector: ".px-captcha-message", text: "Tieni premuto per confermare che sei un essere umano (e non un bot)." },
        ],
        es: [
            { selector: ".px-captcha-header", text: "Por favor, compruebe que es un ser humano." },
            { selector: ".px-captcha-message", text: "Mantén presionado para confirmar que eres un humano (y no un bot)." },
        ],
        en: [
            { selector: ".px-captcha-header", text: "Please Verify You Are A Human" },
            { selector: ".px-captcha-message", text: "Press & Hold to confirm you are a human (and not a bot)." },
        ],
    };
    var pc = document.createElement("script");
    const captchaHost = "https://captcha.px-cdn.net";
    const altCaptchaHost = "https://captcha.px-cloud.net";
    pc.src = `${captchaHost}/${_pxAppId}/captcha.js?a=c&m=${_isPxMobile}`;
    document.head.appendChild(pc);
    pc.onerror = function () {
        pc = document.createElement("script");
        pc.src = `${altCaptchaHost}/${_pxAppId}/captcha.js?a=c&m=${_isPxMobile}`;
        document.head.appendChild(pc);
    };
    document.head.appendChild(pc);
    loadCommonResources(baseUrl, "captcha");
}

function setGlobalVariables(vars) {
    const globalVariabes = document.createElement("script");
    globalVariabes.setAttribute("type", "text/javascript");
    globalVariabes.textContent = vars;
    document.head.appendChild(globalVariabes);
}

function loadCommonResources(baseUrl, action) {
    const actionScript = document.createElement("script");
    actionScript.setAttribute("type", "text/javascript");
    actionScript.setAttribute("src", `${baseUrl}/asset/${action}.js`);
    actionScript.onload = () => eval("load()");
    document.head.appendChild(actionScript);
    actionScript.remove();
    const actionCss = document.createElement("link");
    actionCss.setAttribute("type", "text/css");
    actionCss.setAttribute("href", `${baseUrl}/asset/eps.css`);
    actionCss.setAttribute("rel", "stylesheet");
    document.head.appendChild(actionCss);
    const viewport = document.createElement("meta");
    viewport.setAttribute("name", "viewport");
    viewport.setAttribute("content", "width=device-width, initial-scale=1");
    document.head.appendChild(viewport);
}

function iamNotaRobotD(lang, brand = "api", action = "captcha", epsCaptcha, baseUrl) {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", baseUrl + "/amigood");
    xhr.setRequestHeader("x-lang", lang);
    xhr.setRequestHeader("brand", brand);
    xhr.setRequestHeader("requesting-host", window.location.host);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            const parser = new DOMParser();
            const epsContent = parser.parseFromString(xhr.responseText, "text/html");
            const scripts = Array.from(epsContent.querySelectorAll("script"));
            scripts
                .filter((script) => script.hasAttribute("src") && script.getAttribute("src").includes("geetest"))
                .map((script) => {
                    const scriptEL = document.createElement("script");
                    scriptEL.setAttribute("src", script.getAttribute("src"));
                    document.head.appendChild(scriptEL);
                    script.remove();
                    epsCaptcha.innerHTML = epsContent.body.innerHTML;
                    scriptEL.onload = () => {
                        scripts
                            .filter((script) => script.textContent.includes("#captcha-box") || script.textContent.includes("function solvedCaptcha(payload)"))
                            .forEach((element) => {
                                const scriptEL = document.createElement("script");
                                scriptEL.textContent = element.textContent;
                                scriptEL.setAttribute("type", "text/javascript");
                                document.head.appendChild(scriptEL);
                                element.remove();
                            });
                    };
                });
            loadCommonResources(baseUrl, "captcha");
        }
    };
    xhr.send();
}

function iamNotaRobot(lang, brand = "api", action = "captcha") {
    const realBrand = brand === "api" ? "tm" : brand;
    const epsCaptcha = document.querySelector("#eps-captcha");
    epsCaptcha.style = "background: rgb(255, 255, 255);";
    const baseUrl = getBaseUrl();
    if (action == "block") {
        setGlobalVariables(`var rid="${dt}"; var ip="${client_ip}";var al="${lang}";`);
        epsCaptcha.innerHTML =
            "<div class='container content-wrapper'><div class='box'><div class='c1' id='t1'></div><div class='c2' id='t2'></div> <ul class='c3' id='t3'></ul><div class='c4' id='t4'></div></div><div class='box2'><div class='c5' id='t5'></div><div data-cs-mask class='c6' id='t6'></div></div></div></div>";
        loadCommonResources(baseUrl, "block");
        return;
    }

    setGlobalVariables(`var tc="";var rid="${dt}";var rr="";var host="${window.location.host}";var ip="${client_ip}";var action="${action}";var al="${lang}";var ss="${realBrand}.css";`);

    if (eps_dg == "p") {
        iamNotaRobotPX(lang, brand, action, epsCaptcha, baseUrl);
    } else {
        iamNotaRobotD(lang, brand, action, epsCaptcha, baseUrl);
    }
}
