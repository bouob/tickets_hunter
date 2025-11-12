class AbuseComponent extends HTMLElement {
    constructor() {
        super();
        this.userLang = "en-US";
        this.reloadOnFinish = "false";
        this.boxClickHandler = async (event) => {
            event.preventDefault();
            event.stopPropagation();
            const captchaBox = this.querySelector("#captcha-checkbox");
            if (captchaBox instanceof HTMLButtonElement) {
                captchaBox.disabled = true;
            }
            const checkbox = this.querySelector("#captcha-checkbox");
            const spinner = checkbox.querySelector(".spinner");
            const checkmark = checkbox.querySelector(".checkmark");
            if (!checkbox.classList.contains("processing")) {
                checkbox.classList.add("processing");
                spinner.style.display = "block";
            }
            const handler = new ChallengeHandler("/epsf/pow/request", "/epsf/pow/validate");
            const result = await handler.requestPow();
            if (!result.ok) {
                const error = new Error("failed to get the challenge");
                this.dispatchEvent(new AbuseComponentFailed(error));
                console.error(error, result.error);
                if (this.onError) {
                    this.onError(error);
                }
            }
            const { challenge, difficulty, signature } = result.data;
            let nonce;
            const wasm = await ProofWorkRs.init({
                moduleUrl: "/epsf/asset/proof_work.js",
                wasmUrl: "/epsf/asset/proof_work_bg.wasm",
            });
            nonce = await wasm.solvePoW(challenge, difficulty);
            const validation = await handler.validatePow(challenge, difficulty, nonce, signature);
            if (!validation.ok) {
                const error = new Error("failed to solve the challenge");
                this.dispatchEvent(new AbuseComponentFailed(error));
                console.error(error, validation.error);
                if (this.onError) {
                    this.onError(error);
                }
            }
            spinner.style.display = "none";
            checkmark.style.display = "block";
            checkbox.style.borderColor = "#28a745";
            let epsfc = CookiesHandler.get("epsfc");
            if (epsfc && epsfc !== "") {
                this.dispatchEvent(new AbuseComponentTokenRenewed());
                if (this.onSolve) {
                    this.onSolve();
                }
                if (this.reloadOnFinish === "true") {
                    window.location.reload();
                }
            }
        };
    }
    async connectedCallback() {
        this.backwardCheck();
        this.defineProperties();
        const actions = [AbuseComponent.BLOCK, AbuseComponent.CHALLENGE, AbuseComponent.IDENTIFY];
        if (!this.action || !actions.includes(this.action)) {
            const err = new Error("Abuse component without an actionable request or invalid action");
            console.error(err);
            this.dispatchEvent(new AbuseComponentFailed(err));
            if (this.onError) {
                this.onError(err);
            }
            return;
        }
        this.detectLang();
        this.defineGecKey();
        await this.fetchCSS().catch((err) => {
            console.warn("failed to load styling or action data", err);
        });
        if (this.action === AbuseComponent.BLOCK) {
            this.initBlockState();
        }
        if (this.action === AbuseComponent.CHALLENGE) {
            this.initChallengeState();
        }
        if (this.action === AbuseComponent.IDENTIFY) {
            this.spinWhileIdentifying();
        }
    }
    disconnectedCallback() {
        const captchaBox = this.querySelector("#captcha-checkbox");
        if (captchaBox) {
            captchaBox.removeEventListener("click", this.boxClickHandler);
        }
    }
    backwardCheck() {
        document.querySelectorAll(".box").forEach((el) => el.remove());
        document.querySelectorAll(".box2").forEach((el) => el.remove());
        document.querySelectorAll(".be").forEach((el) => el.remove());
    }
    async defineProperties() {
        const properties = [
            { property: "action", attribute: "action" },
            { property: "ip", attribute: "ip" },
            { property: "rid", attribute: "rid" },
            { property: "userLang", attribute: "lang", default: "en-us" },
            { property: "reloadOnFinish", attribute: "reload", default: "false" },
        ];
        for (const item of properties) {
            this[item.property] = this.getAttribute(item.attribute) || item.default;
        }
    }
    detectLang() {
        if (!this.userLang) {
            if (typeof al == "undefined") {
                al = undefined;
            }
            this.userLang = al || CookiesHandler.get("LANGUAGE") || (navigator === null || navigator === void 0 ? void 0 : navigator.language) || (navigator === null || navigator === void 0 ? void 0 : navigator.language) || "en-US";
        }
    }
    async fetchFor(action, mapper, defaultValue) {
        try {
            return await fetch(`/epsf/asset/${action.toLowerCase()}.json`)
                .then((res) => res.json())
                .then(mapper);
        }
        catch (err) {
            console.warn(`Failed to load json data for ${this.action.toLowerCase()}`, err);
            return defaultValue;
        }
    }
    async fetchCSS() {
        try {
            let css = await fetch(`/epsf/asset/abuse-component.css`).then((res) => res.text());
            let style = document.createElement("style");
            style.appendChild(document.createTextNode(css));
            document.head.appendChild(style);
        }
        catch (err) {
            console.warn("failed to load CSS", err);
        }
    }
    async initBlockState() {
        const data = await this.fetchForBlock();
        this.createBlockElements(data);
    }
    async fetchForBlock() {
        return this.fetchFor(AbuseComponent.BLOCK, DataMappers.buildForBlock(this.userLang), { 1: "Something went wrong", 2: "Please reload this page in a few minutes" });
    }
    createBlockElements(data) {
        var _a, _b, _c, _d, _e, _f, _g;
        if (data["dir"] && data["dir"] === "rtl") {
            document.getElementsByClassName("lg")[0].classList.add("rtl");
        }
        this.innerHTML = `
        <div class="container">
            <div id="boxes_container" ${data["dir"] ? ` dir="${data["dir"]}"` : ""}>
                <div class="box">
                    <div class="c1" id="t1">
                        ${(_a = data["1"]) !== null && _a !== void 0 ? _a : ""}
                    </div>
                    <div class="c2" id="t2">
                        ${(_b = data["2"]) !== null && _b !== void 0 ? _b : ""}
                    </div>
                    <ul class="c3" id="t3">
                        ${(_d = (_c = data["3"]) === null || _c === void 0 ? void 0 : _c.map((item) => `<li>${item}</li>`).join("\n")) !== null && _d !== void 0 ? _d : ""}
                    </ul>
                    <div class="c4" id="t4">
                        ${(_e = data["4"]) !== null && _e !== void 0 ? _e : ""}
                    </div>
                </div>

                <div class="be"></div>

                <div class="box2 ${data["dir"] ? data["dir"] : ""}">
                    <div class="c5" id="t5">
                        ${(_f = this.ip) !== null && _f !== void 0 ? _f : ""}
                    </div>
                    <div data-cs-mask class="c6" id="t6">
                        ${(_g = this.rid) !== null && _g !== void 0 ? _g : ""}
                    </div>
                </div>
            </div>
        </div>
`;
    }
    defineGecKey() {
        if (typeof gecKey === "undefined") {
            window.gecKey = "6LcvL3UrAAAAAO_9u8Seiuf-I6F_tP_jSS-zndXV";
        }
    }
    async initChallengeState() {
        var _a, _b;
        const data = await this.fetchForChallenge();
        if (data["dir"] && data["dir"] === "rtl") {
            document.getElementsByClassName("lg")[0].classList.add("rtl");
        }
        this.innerHTML = `
        <div class="container">
            <div id="boxes_container" ${data["dir"] ? ` dir="${data["dir"]}"` : ""}>
                <div class="box ${data["dir"] ? data["dir"] : ""}">
                    <div id="challenge_warning_sign">
                        <img id="warning_icon" src="/epsf/asset/warningIcon.svg" />
                    </div>
                    <div id="challenge_warning_notes">
                        ${data.notes}
                    </div>

                    <div class="captcha-container ${data["dir"] ? data["dir"] : ""}">
                        <button class="checkbox-container" id="captcha-checkbox">
                            <div class="spinner"></div>
                            <span class="checkmark">✔</span>
                        </button>

                        <span class="captcha-label" id="captcha-label">
                            ${data.label}
                        </span>

                    </div>
                </div>

                <div class="box2 ${data["dir"] ? data["dir"] : ""}">
                    <div class="c5" id="t5">
                        ${(_a = this.ip) !== null && _a !== void 0 ? _a : ""}
                    </div>
                    <div data-cs-mask class="c6" id="t6">
                        ${(_b = this.rid) !== null && _b !== void 0 ? _b : ""}
                    </div>
                </div>
            </div>
        </div>
`;
        const be = document.getElementById("be");
        if (be) {
            be.remove();
        }
        const captchaBox = this.querySelector("#captcha-checkbox");
        captchaBox.addEventListener("click", this.boxClickHandler);
    }
    async fetchForChallenge() {
        return this.fetchFor(AbuseComponent.CHALLENGE, DataMappers.buildForChallenge(this.userLang), {
            notes: "We're Running Extra Protections For Fans",
            label: "Verify you are human",
        });
    }
    async fetchForIdentify() {
        return this.fetchFor(AbuseComponent.IDENTIFY, DataMappers.buildForIdentify(this.userLang), { oneMoment: "Something went wrong", almostThere: "Something went wrong" });
    }
    async spinWhileIdentifying() {
        const data = await this.fetchForIdentify();
        const FIRST_SPINNER = 3000;
        const SECOND_SPINNER = 10000 + FIRST_SPINNER;
        setTimeout(() => {
            this.innerHTML = `<div class="center-container"><div class="identify-spinner"></div><div class="identify-spinner-text">${data.oneMoment}</div></div>`;
        }, FIRST_SPINNER);
        setTimeout(() => {
            this.innerHTML = `<div class="center-container"><div class="identify-spinner"></div><div class="identify-spinner-text">${data.almostThere}</div></div>`;
        }, SECOND_SPINNER);
    }
    async initIdentify() {
        try {
            const token = await fetch("/eps-mgr?epsf-token=renew").then((res) => res.text());
            if (token && token !== "") {
                epsfToken = token;
            }
            let pageName = await PageName.get();
            await CookiesHandler.setGecV3(pageName, gecKey);
            this.dispatchEvent(new AbuseComponentTokenRenewed());
            if (this.onSolve) {
                this.onSolve();
            }
            if (this.reloadOnFinish === "true") {
                window.location.reload();
            }
        }
        catch (err) {
            const error = new Error("failed to load new token");
            this.dispatchEvent(new AbuseComponentFailed(error));
            if (this.onError) {
                this.onError(error);
            }
            console.error(error, err);
        }
    }
}
AbuseComponent.BLOCK = "block";
AbuseComponent.CHALLENGE = "challenge";
AbuseComponent.IDENTIFY = "identify";
class AbuseComponentTokenRenewed extends CustomEvent {
    constructor() {
        super("renewed");
    }
}
class AbuseComponentFailed extends CustomEvent {
    constructor(error) {
        super("failed", { detail: { error } });
    }
}
class PageName {
    static async getPageName(integrator) {
        var _a, _b;
        if (typeof epsPageName !== "undefined" && epsPageName !== "") {
            return { pageName: epsPageName, isUseEpsPageName: true };
        }
        const metaPageType = (_b = (_a = Array.from(document.head.getElementsByTagName("meta"))) === null || _a === void 0 ? void 0 : _a.find((el) => el.getAttribute("property") === "tm:eps:page-type")) === null || _b === void 0 ? void 0 : _b.getAttribute("content");
        if (metaPageType) {
            return { pageName: metaPageType, isUseEpsPageName: false };
        }
        if (integrator === "sports") {
            return {
                pageName: `${window.dataLayer[0].ClientIdentifier}_${window.dataLayer[0].PageType.toLowerCase()}`,
                isUseEpsPageName: false,
            };
        }
        await Sleep.until(() => { var _a, _b, _c; return (_c = (_b = (_a = window.digitalData) === null || _a === void 0 ? void 0 : _a.page) === null || _b === void 0 ? void 0 : _b.pageInfo) === null || _c === void 0 ? void 0 : _c.pageName; }, 5000);
        return { pageName: "pageView", isUseEpsPageName: false };
    }
    static async get() {
        if (typeof integrators === "undefined") {
            var integrators = {
                ".*tmtickets.*": "sports",
            };
        }
        if (typeof integrator === "undefined") {
            var integrator = "default";
        }
        let { pageName } = await PageName.getPageName(integrator);
        if (!pageName) {
            pageName = document.URL.split("/").slice(2, 5).join("/");
        }
        return pageName;
    }
}
class Sleep {
    static until(predicate, timeout) {
        return new Promise((resolve, reject) => {
            let running = true;
            const check = async () => {
                try {
                    const res = await predicate();
                    if (res)
                        return resolve(res);
                    if (running)
                        setTimeout(check, 100);
                }
                catch (error) {
                    reject(error);
                }
            };
            check();
            if (!timeout)
                return;
            setTimeout(() => {
                running = false;
                resolve();
            }, timeout);
        });
    }
}
class CookiesHandler {
    static get(name) {
        let cookie = document.cookie.match("(^|;) ?" + name + "=([^;]*)(;|$)");
        return cookie ? cookie[2] : null;
    }
    static async setGecV2(pageName, key, isCaptcha = false) {
        const action = pageName.replace(/[^A-Z]+/gi, "_");
        await Sleep.until(() => grecaptcha.enterprise.execute);
        const token = await grecaptcha.enterprise.execute(key, { action }).catch((err) => console.error(`gec execute failed: ${err}`));
        if (!token)
            return;
        const gecPath = [window.location.hostname, key, encodeURIComponent(action), encodeURIComponent(token)].join("/");
        const gecEndpoint = `https://${gecHost}/gec/v2/${epsfToken}/${gecPath}`;
        if (isCaptcha) {
            new Image().src = `${gecEndpoint}?captcha=1`;
        }
        else {
            new Image().src = gecEndpoint;
        }
    }
    static async setGecV3(pageName, key, isCaptcha = false) {
        const action = pageName.replace(/[^A-Z]+/gi, "_");
        await Sleep.until(() => grecaptcha.enterprise.execute);
        const token = await grecaptcha.enterprise.execute(key, { action }).catch((err) => console.error(`gec execute failed: ${err}`));
        if (!token) {
            console.error("failed to retrieve gec token");
            return;
        }
        let gecEndpoint = `https://${gecHost}/gec/v3/${epsfToken}/${action}`;
        if (isCaptcha) {
            gecEndpoint += "?captcha=1";
        }
        const body = JSON.stringify({
            hostname: window.location.hostname,
            key,
            token,
        });
        const headers = {
            "Access-Control-Allow-Credentials": "true",
            "Content-Type": "application/json",
        };
        await fetch(gecEndpoint, {
            method: "POST",
            credentials: "include",
            headers,
            body,
        }).catch((err) => {
            console.error("failed to request gec cookie", err);
        });
    }
}
class DataMappers {
    static buildForBlock(userLang = "") {
        return function (actionData) {
            const lang = Object.entries(actionData)
                .map(([lang, data]) => ({ lang: lang.toLowerCase(), data }))
                .find((item) => item.lang === userLang.toLowerCase());
            if (!lang) {
                console.error(`'${userLang}' invalid or language not supported, default to 'en-US'`);
                return actionData["en-US"];
            }
            return lang.data;
        };
    }
    static buildForChallenge(userLang = "") {
        return function (actionData) {
            const lang = Object.entries(actionData)
                .map(([lang, data]) => ({ lang: lang.toLowerCase(), data }))
                .find((item) => item.lang === userLang.toLowerCase());
            if (!lang) {
                console.error(`'${userLang}' invalid or language not supported, default to 'en-US'`);
                return actionData["en-US"];
            }
            return lang.data;
        };
    }
    static buildForIdentify(userLang = "") {
        return function (actionData) {
            const lang = Object.entries(actionData)
                .map(([lang, data]) => ({ lang: lang.toLowerCase(), data }))
                .find((item) => item.lang === userLang.toLowerCase());
            if (!lang) {
                console.error(`'${userLang}' invalid or language not supported, default to 'en-US'`);
                return actionData["en-US"];
            }
            return lang.data;
        };
    }
}
class ChallengeHandler {
    constructor(requestPoWUrl, solvePoWUrl) {
        this.requestPoWUrl = requestPoWUrl;
        this.solvePoWUrl = solvePoWUrl;
    }
    async requestPow() {
        try {
            const res = await fetch(this.requestPoWUrl);
            if (!res.ok) {
                return { ok: false, status: res.status, error: `HTTP ${res.status}` };
            }
            const data = await res.json();
            return { ok: true, status: res.status, data };
        }
        catch (err) {
            return { ok: false, status: 0, error: err.message || "Unknown error" };
        }
    }
    async validatePow(challenge, difficulty, nonce, signature) {
        try {
            const body = JSON.stringify({ challenge, difficulty, nonce, signature });
            const res = await fetch(this.solvePoWUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body,
            });
            const data = await res.text();
            return { ok: res.ok, status: res.status, data };
        }
        catch (err) {
            return { ok: false, status: 0, error: err.message || "Unknown error" };
        }
    }
}
class ProofWorkJS {
    async sha256(message) {
        const msgBuffer = new TextEncoder().encode(message);
        const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
    }
    async solvePoW(challenge, difficulty) {
        const prefix = "0".repeat(difficulty);
        let nonce = 0;
        while (true) {
            const hash = await this.sha256(challenge + nonce);
            if (hash.startsWith(prefix)) {
                console.log(`Current nonce: ${nonce}, hash: ${hash}`);
                return nonce;
            }
            nonce++;
            if (nonce % 100000 === 0) {
                console.log(`Current nonce: ${nonce}, hash: ${hash}`);
                await new Promise((resolve) => setTimeout(resolve, 0));
            }
        }
    }
}
class ProofWorkRs {
    constructor() { }
    static async init({ moduleUrl, wasmUrl }) {
        if (!ProofWorkRs.instance) {
            ProofWorkRs.instance = new ProofWorkRs();
            const mod = await import(moduleUrl);
            const wasmBytes = await fetch(wasmUrl).then((res) => res.arrayBuffer());
            ProofWorkRs.instance.wasm = mod.initSync({ module: wasmBytes });
        }
        return ProofWorkRs.instance;
    }
    solvePoW(challenge, diff) {
        const wasm = this.wasm;
        const cha_str = challenge;
        const diff_str = "0".repeat(diff);
        return new Promise((resolve, reject) => {
            wasm.find_proof(cha_str, diff_str)
                .then((result) => {
                if (!result) {
                    reject(new Error("Failed to find proof"));
                    return;
                }
                resolve(Number(result.nonce));
            })
                .catch((err) => {
                reject(new Error(`Failed to find proof: ${err.message}`));
            });
        });
    }
}
customElements.define("abuse-component", AbuseComponent);
