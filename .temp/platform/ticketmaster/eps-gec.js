(async () => {
    // Generate UUID for this identify session
    function generateUUID() {
        if (crypto.randomUUID) {
            return crypto.randomUUID();
        }
        // Fallback for older browsers
        return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
            const r = (Math.random() * 16) | 0;
            const v = c === "x" ? r : (r & 0x3) | 0x8;
            return v.toString(16);
        });
    }

    // Set up session UUID as global variable
    window.identifySessionUUID = generateUUID();

    async function getPageName(integrator) {
        if (typeof epsPageName !== "undefined" && epsPageName !== "") {
            return { pageName: epsPageName, isUseEpsPageName: true };
        }

        const metaPageType = Array.from(document.head.getElementsByTagName("meta"))
            ?.find((el) => el.getAttribute("property") === "tm:eps:page-type")
            ?.getAttribute("content");

        if (metaPageType) {
            return { pageName: metaPageType, isUseEpsPageName: false };
        }

        if (integrator === "sports") {
            return {
                pageName: `${window.dataLayer[0].ClientIdentifier}_${window.dataLayer[0].PageType.toLowerCase()}`,
                isUseEpsPageName: false,
            };
        }

        await waitFor(() => window.digitalData?.page?.pageInfo?.pageName, 5000);
        return { pageName: "pageView", isUseEpsPageName: false };
    }

    async function setGecCookiesV3(pageName, key, isCaptcha = false) {
        const action = pageName.replace(/[^A-Z]+/gi, "_");

        // Capture device and network metrics
        const getContextMetrics = () => {
            const metrics = {
                performanceNow: performance.now(),
            };

            // Memory usage (if available)
            if (performance.memory) {
                metrics.memoryUsedMB = Math.round(performance.memory.usedJSHeapSize / 1048576);
            }

            // Network information (if available)
            if (navigator.connection) {
                metrics.connectionType = navigator.connection.effectiveType;
                metrics.downlinkMbps = navigator.connection.downlink;
                metrics.rttMs = navigator.connection.rtt;
            }

            // Device capabilities
            if (navigator.deviceMemory) {
                metrics.deviceMemoryGB = navigator.deviceMemory;
            }
            if (navigator.hardwareConcurrency) {
                metrics.cpuCores = navigator.hardwareConcurrency;
            }

            return metrics;
        };

        // Log before attempting reCAPTCHA execute
        logIdentifyEvent("recaptcha_execute_start", {
            pageName,
            gecAction: action,
            key,
            isCaptcha,
            ...getContextMetrics(),
        });

        const executeStartTime = performance.now();

        const token = await grecaptcha.enterprise.execute(key, { action }).catch((err) => {
            const executeDuration = Math.round(performance.now() - executeStartTime);
            console.error(`gec execute failed: ${err}`);
            logIdentifyEvent("recaptcha_execute_error", {
                gecAction: action,
                error: err.message || err.toString(),
                durationMs: executeDuration,
            });
            return null;
        });

        const executeDuration = Math.round(performance.now() - executeStartTime);

        if (!token) {
            console.error("failed to retrieve gec token");
            logIdentifyEvent("gec_token_failed", {
                gecAction: action,
                durationMs: executeDuration,
            });
            return;
        }

        // Log successful reCAPTCHA token generation
        logIdentifyEvent("recaptcha_execute_success", {
            gecAction: action,
            tokenLength: token.length,
            tokenPreview: token.slice(0, 8) + "..." + token.slice(-8),
            durationMs: executeDuration,
            ...getContextMetrics(),
        });

        //gecHost comes from epsf
        let gecEndpoint = `https://${gecHost}/gec/v3/${action}`;

        if (isCaptcha) {
            gecEndpoint += "?captcha=1";
        }

        const body = JSON.stringify({
            hostname: window.location.hostname,
            key: key,
            token: token,
        });

        const headers = {
            "Access-Control-Allow-Credentials": true,
            "Content-Type": "application/json",
        };

        // Log before /gec/v3 call
        logIdentifyEvent("gec_v3_request_start", {
            action,
            isCaptcha,
        });

        try {
            const response = await fetch(gecEndpoint, {
                method: "POST",
                credentials: "include",
                headers,
                body,
            });

            // Log after /gec/v3 response
            const responseData = {
                status: response.status,
                ok: response.ok,
                action,
            };

            // Check if cookie was set after the response
            const cookieSet = isCookieSet("tmpt");
            responseData.cookieSet = cookieSet;

            logIdentifyEvent("gec_v3_response", responseData);
        } catch (err) {
            console.error("failed to request gec cookie", err);
            logIdentifyEvent("gec_v3_error", {
                action,
                error: err.message || err.toString(),
            });
        }
    }

    function matchRuleShort(str, rule) {
        return new RegExp(rule).test(str);
    }

    function waitFor(predicate, timeout) {
        return new Promise((resolve, reject) => {
            let running = true;

            const check = async () => {
                const res = await predicate();
                if (res) return resolve(res);
                if (running) setTimeout(check, 100);
            };

            check();

            if (!timeout) return;
            setTimeout(() => {
                running = false;
                resolve();
            }, timeout);
        });
    }

    function isCookieSet(cookieName) {
        for (let pair of document.cookie.split(";")) {
            if (pair.trim().startsWith(cookieName + "=")) return true;
        }
        return false;
    }

    // Helper function for RUM logging
    function logIdentifyEvent(eventName, data = {}) {
        const actionValue = typeof action !== "undefined" ? action : "unknown";

        if (actionValue === "unknown") {
            return;
        }

        const params = new URLSearchParams();
        params.append("event", eventName);
        params.append("action", actionValue);
        params.append("timestamp", Date.now());
        params.append("sessionUUID", window.identifySessionUUID);

        for (const [key, value] of Object.entries(data)) {
            params.append(key, value);
        }

        const logEndpoint = `https://${window.location.hostname}/eps/log?${params.toString()}`;
        fetch(logEndpoint, {
            method: "GET",
            keepalive: true,
        }).catch(() => {
            // Silently fail if logging fails
        });
    }

    // Capture browser environment metrics for bot/automation detection
    const getBrowserMetrics = () => {
        const metrics = {};

        // Automation detection
        metrics.webdriver = navigator.webdriver || false;

        // Browser capabilities
        metrics.languages = navigator.languages ? navigator.languages.join(",") : navigator.language;
        metrics.platform = navigator.platform;
        metrics.vendor = navigator.vendor;
        metrics.userAgent = navigator.userAgent;

        // Screen/display info
        metrics.screenWidth = screen.width;
        metrics.screenHeight = screen.height;
        metrics.screenDepth = screen.colorDepth;
        metrics.devicePixelRatio = window.devicePixelRatio;

        // Plugins (empty in modern browsers often indicates headless)
        metrics.pluginCount = navigator.plugins ? navigator.plugins.length : 0;

        // Touch support
        metrics.maxTouchPoints = navigator.maxTouchPoints || 0;

        // Battery API (often missing in headless)
        metrics.hasBattery = "getBattery" in navigator;

        // Chrome-specific detection
        metrics.hasChrome = !!window.chrome;
        metrics.hasChromeRuntime = !!(window.chrome && window.chrome.runtime);

        // Permissions API
        metrics.hasPermissions = "permissions" in navigator;

        // WebGL fingerprinting
        try {
            const canvas = document.createElement("canvas");
            const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
            if (gl) {
                const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
                if (debugInfo) {
                    metrics.webglVendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                    metrics.webglRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                }
            }
        } catch (e) {
            metrics.webglError = true;
        }

        // Timezone
        metrics.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        metrics.timezoneOffset = new Date().getTimezoneOffset();

        // DoNotTrack
        metrics.doNotTrack = navigator.doNotTrack;

        // Brave browser detection
        metrics.isBrave = navigator.brave && typeof navigator.brave.isBrave === "function";

        return metrics;
    };

    // Log before Google reCAPTCHA loads
    logIdentifyEvent("identify_start", getBrowserMetrics());

    // Track page visibility changes
    document.addEventListener("visibilitychange", () => {
        logIdentifyEvent(`page_visibility_changed_${document.visibilityState}`);
    });

    // Track page lifecycle events
    document.addEventListener("freeze", () => {
        logIdentifyEvent("page_lifecycle_freeze");
    });

    document.addEventListener("resume", () => {
        logIdentifyEvent("page_lifecycle_resume");
    });

    window.addEventListener("pagehide", (event) => {
        logIdentifyEvent("page_lifecycle_pagehide", {
            persisted: event.persisted,
        });
    });

    window.addEventListener("pageshow", (event) => {
        logIdentifyEvent("page_lifecycle_pageshow", {
            persisted: event.persisted,
        });
    });

    const key = "6LcvL3UrAAAAAO_9u8Seiuf-I6F_tP_jSS-zndXV";
    const gecStyle = document.createElement("style");
    gecStyle.innerHTML = ".grecaptcha-badge { visibility: hidden; }";
    document.head.appendChild(gecStyle);
    const gecScript = document.createElement("script");

    let integrators = {
        ".*tmtickets.*": "sports",
    };

    let integrator = "default";

    for (var k in integrators) {
        if (matchRuleShort(document.URL, k)) {
            integrator = integrators[k];
        }
    }

    // Determine reCAPTCHA endpoint based on hostname
    const recaptchaEndpoint = window.location.hostname.includes("ticketmaster.sg") ? "https://recaptcha.net/recaptcha/enterprise.js" : "https://www.google.com/recaptcha/enterprise.js";

    gecScript.src = `${recaptchaEndpoint}?render=${key}`;
    gecScript.defer = true;
    gecScript.onload = async () => {
        // Log after Google reCAPTCHA script loads
        logIdentifyEvent("recaptcha_script_loaded");

        let { pageName, isUseEpsPageName } = await getPageName(integrator);

        if (!pageName) {
            pageName = document.URL.split("/").slice(2, 5).join("/");
        }
        let ready = await waitFor(() => window.grecaptcha?.enterprise?.ready);

        // Log after Google reCAPTCHA initializes
        logIdentifyEvent("recaptcha_ready", {
            pageName,
            isUseEpsPageName,
        });

        ready(async () => {
            await setGecCookiesV3(pageName, key);

            // Log start of cookie waiting
            logIdentifyEvent("cookie_wait_start");
            let waitCheckCount = 0;
            const waitStartTime = Date.now();

            await waitFor(() => {
                waitCheckCount++;

                if (isCookieSet("tmpt")) {
                    // Log successful cookie detection
                    logIdentifyEvent("cookie_detected", {
                        waitTime: Date.now() - waitStartTime,
                        checkCount: waitCheckCount,
                        hasCallback: !!window.onCookieInitialized,
                    });

                    if (window.onCookieInitialized) {
                        // Set up reload detection
                        window.addEventListener("beforeunload", function () {
                            logIdentifyEvent("onCookieInitialize_reload_started");
                        });

                        try {
                            logIdentifyEvent("onCookieInitialize_executing");
                            window.onCookieInitialized();
                        } catch (err) {
                            logIdentifyEvent("onCookieInitialize_error", {
                                error: err.message || err.toString(),
                            });
                        }
                    } else {
                        // Cookie is set but no callback to trigger reload!
                        // Only log this for identify pages where we expect the callback
                        if (typeof action !== "undefined" && action === "identify") {
                            logIdentifyEvent("cookie_ready_no_callback");
                        }
                    }
                    return true;
                }

                // Log if we're in a waiting loop (every 50 checks = ~5 seconds)
                if (waitCheckCount % 50 === 0) {
                    logIdentifyEvent("cookie_wait_loop", {
                        waitTime: Date.now() - waitStartTime,
                        checkCount: waitCheckCount,
                    });
                }

                return false;
            });

            // Log if we exit without finding cookie (timeout)
            if (!isCookieSet("tmpt")) {
                logIdentifyEvent("cookie_wait_timeout", {
                    waitTime: Date.now() - waitStartTime,
                    checkCount: waitCheckCount,
                });
            }
        });
    };
    document.head.appendChild(gecScript);
})().catch((err) => {
    console.error(`gec failed: ${err}`);
});

(async () => {
    const metrics = {
        // Basic checks for PublicKeyCredential
        hasPublicKeyCredential: "PublicKeyCredential" in window,
        hasConditionalMediation: "PublicKeyCredential" in window && "isConditionalMediationAvailable" in PublicKeyCredential,

        // Platform authenticator availability
        platformAuthenticator: false,
        err: "",
    };

    // Check if platform authenticator is available
    if (metrics.hasPublicKeyCredential) {
        try {
            metrics.platformAuthenticator = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
        } catch (e) {
            metrics.platformAuthenticator = false;
            metrics.err = e.toString().replace(/[^a-zA-Z0-9]/g, "");
        }
    }

    // Check conditional UI support
    if (metrics.hasConditionalMediation) {
        try {
            metrics.conditionalMediationAvailable = await PublicKeyCredential.isConditionalMediationAvailable();
        } catch (e) {
            metrics.conditionalMediationAvailable = false;
            metrics.err = e.toString().replace(/[^a-zA-Z0-9]/g, "");
        }
    }
    // Convert metrics to URL parameters
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(metrics)) {
        params.append(key, value);
    }

    const logEndpoint = `https://${window.location.hostname}/eps/log?${params.toString()}`;
    // Send metrics to server using GET
    fetch(logEndpoint, {
        method: "GET",
        // Use keepalive to ensure the request completes even if page is unloading
        keepalive: true,
    }).catch(() => {
        // Silently fail if logging fails
        // This prevents any user-visible errors
    });
})().catch((err) => {
    console.error(`log failed: ${err}`);
});

(async () => {
    let hosts = [
        "www.loisirs.showroomprive.com",
        "www.leclercbilletterie.com",
        "billetterie.ldlcarena.com",
        "billetterie.groupama-stadium.com",
        "billetterie.cultura.com",
        "tickets.cdiscount.com",
        "www.spectaclescarrefour.leparisien.fr",
        "www.spectacles.carrefour.fr",
        "billetterie.arenaaix.com",
        "billetterie.auchanpro.fr",
        "billetterie.auchan.fr",
        "billetterie.arkeaarena.com",
        "billetterie.aegpresents.fr",
        "billetterie.adidasarena.com",
        "ticketmaster.fr",
        "billetterie.accorarena.com",
    ];

    hosts.forEach((h) => {
        if (window.location.hostname.indexOf(h) != -1) {
            window.setInterval(function () {
                if (document.cookie.indexOf("tmpt") == -1) {
                    window.location.reload();
                }
            }, 15000);
        }
    });
})().catch((err) => {
    console.error(`refresh failed: ${err}`);
});
