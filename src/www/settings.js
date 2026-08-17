
// action bar
const run_button = document.querySelector('#run_btn');
const save_button = document.querySelector('#save_btn');
const reset_button = document.querySelector('#reset_btn');
const exit_button = document.querySelector('#exit_btn');
const pause_button = document.querySelector('#pause_btn');
const resume_button = document.querySelector('#resume_btn');

// preference
const homepage = document.querySelector('#homepage');
const ticket_number = document.querySelector('#ticket_number');
const refresh_datetime = document.querySelector('#refresh_datetime');
const date_select_mode = document.querySelector('#date_select_mode');
const date_keyword = document.querySelector('#date_keyword');
const date_auto_fallback = document.querySelector('#date_auto_fallback');
const area_select_mode = document.querySelector('#area_select_mode');
const area_keyword = document.querySelector('#area_keyword');
const area_auto_fallback = document.querySelector('#area_auto_fallback');
const keyword_exclude = document.querySelector('#keyword_exclude');

// advance
const play_ticket_sound = document.querySelector('#play_ticket_sound');
const play_order_sound = document.querySelector('#play_order_sound');
const play_sound_filename = document.querySelector('#play_sound_filename');
const discord_webhook_url = document.querySelector('#discord_webhook_url');
const notification_message = document.querySelector('#notification_message');
const telegram_bot_token = document.querySelector('#telegram_bot_token');
const telegram_chat_id = document.querySelector('#telegram_chat_id');

const auto_press_next_step_button = document.querySelector('#auto_press_next_step_button');
const max_dwell_time = document.querySelector('#max_dwell_time');

const auto_reload_page_interval = document.querySelector('#auto_reload_page_interval');
const tixcraft_soft_block_delay = document.querySelector('#tixcraft_soft_block_delay');
const tixcraft_allow_less_tickets = document.querySelector('#tixcraft_allow_less_tickets');
const reset_browser_interval = document.querySelector('#reset_browser_interval');
const server_port = document.querySelector('#server_port');
const proxy_server_port = document.querySelector('#proxy_server_port');
const window_size = document.querySelector('#window_size');
const disable_adjacent_seat = document.querySelector('#disable_adjacent_seat');

const hide_some_image = document.querySelector('#hide_some_image');
const block_facebook_network = document.querySelector('#block_facebook_network');
const headless = document.querySelector('#headless');
const verbose = document.querySelector('#verbose');
const show_timestamp = document.querySelector('#show_timestamp');


const ocr_captcha_enable = document.querySelector('#ocr_captcha_enable');
const ocr_captcha_image_source = document.querySelector('#ocr_captcha_image_source');
const ocr_captcha_force_submit = document.querySelector('#ocr_captcha_force_submit');
const ocr_captcha_use_universal = document.querySelector('#ocr_captcha_use_universal');
const remote_url = document.querySelector('#remote_url');
const ocr_model_path = document.querySelector('#ocr_model_path');

// dictionary
const user_guess_string = document.querySelector('#user_guess_string');
const auto_guess_options = document.querySelector('#auto_guess_options');


// user info - personal data
const real_name = document.querySelector('#real_name');
const phone = document.querySelector('#phone');
const credit_card_prefix = document.querySelector('#credit_card_prefix');

// auto fill
const tixcraft_sid = document.querySelector('#tixcraft_sid');
const ibonqware = document.querySelector('#ibonqware');
const funone_session_cookie = document.querySelector('#funone_session_cookie');
const fansigo_cookie = document.querySelector('#fansigo_cookie');
const fansigo_account = document.querySelector('#fansigo_account');
const fansigo_password = document.querySelector('#fansigo_password');
const facebook_account = document.querySelector('#facebook_account');
const kktix_account = document.querySelector('#kktix_account');
const fami_account = document.querySelector('#fami_account');
const kham_account = document.querySelector('#kham_account');
const ticket_account = document.querySelector('#ticket_account');
const udn_account = document.querySelector('#udn_account');
const ticketplus_account = document.querySelector('#ticketplus_account');
const cityline_account = document.querySelector('#cityline_account');
const urbtix_account = document.querySelector('#urbtix_account');
const hkticketing_account = document.querySelector('#hkticketing_account');

const facebook_password = document.querySelector('#facebook_password');
const kktix_password = document.querySelector('#kktix_password');
const fami_password = document.querySelector('#fami_password');
const kham_password = document.querySelector('#kham_password');
const ticket_password = document.querySelector('#ticket_password');
const udn_password = document.querySelector('#udn_password');
const ticketplus_password = document.querySelector('#ticketplus_password');
const discount_code = document.querySelector('#discount_code');
const urbtix_password = document.querySelector('#urbtix_password');
const hkticketing_password = document.querySelector('#hkticketing_password');

// runtime
const idle_keyword = document.querySelector('#idle_keyword');
const resume_keyword = document.querySelector('#resume_keyword');
const idle_keyword_second = document.querySelector('#idle_keyword_second');
const resume_keyword_second = document.querySelector('#resume_keyword_second');
const dark_mode_toggle = document.querySelector('#dark_mode_toggle');
const theme_status = document.querySelector('#theme_status');
const language_selector = document.querySelector('#language_selector');

var settings = null;
let currentLanguage = 'zh-TW';
let helpOffcanvasInstance = null;
let currentHelpField = null;
const ORIGINAL_STATE = new Map();
const ORIGINAL_TITLE = document.title;
const HELP_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/><path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0"/></svg>';
const QUESTION_ALERT_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-exclamation-triangle-fill me-2" viewBox="0 0 16 16"><path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg>';
const INFO_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-info-circle me-1" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/><path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0"/></svg>';

function normalizeLanguage(language) {
    const value = (language || '').toString().trim().toLowerCase();
    if (['english', 'en', 'en-us', 'en-gb'].includes(value)) {
        return 'en';
    }
    if (['繁體中文', 'traditional chinese', 'traditional_chinese', 'zh-tw', 'zh-hant', 'tw', 'zh'].includes(value)) {
        return 'zh-TW';
    }
    return 'zh-TW';
}

function serializeLanguage(language) {
    return normalizeLanguage(language) === 'en' ? 'English' : '繁體中文';
}

function rememberOriginalState(key, getter) {
    if (!ORIGINAL_STATE.has(key)) {
        ORIGINAL_STATE.set(key, getter());
    }
}

function applyElementValue(selector, property, value) {
    const element = document.querySelector(selector);
    if (!element) {
        return;
    }

    const key = `${selector}::${property}`;
    rememberOriginalState(key, () => {
        if (property === 'innerHTML') return element.innerHTML;
        if (property === 'textContent') return element.textContent;
        return element.getAttribute(property);
    });

    if (property === 'innerHTML') {
        element.innerHTML = value;
    } else if (property === 'textContent') {
        element.textContent = value;
    } else {
        element.setAttribute(property, value);
    }
}

function restoreElementValue(selector, property) {
    const element = document.querySelector(selector);
    const key = `${selector}::${property}`;
    if (!element || !ORIGINAL_STATE.has(key)) {
        return;
    }

    const value = ORIGINAL_STATE.get(key);
    if (property === 'innerHTML') {
        element.innerHTML = value;
    } else if (property === 'textContent') {
        element.textContent = value;
    } else if (value === null || value === undefined) {
        element.removeAttribute(property);
    } else {
        element.setAttribute(property, value);
    }
}

function applyNodeValue(key, element, property, value) {
    if (!element) {
        return;
    }

    rememberOriginalState(key, () => {
        if (property === 'innerHTML') return element.innerHTML;
        if (property === 'textContent') return element.textContent;
        return element.getAttribute(property);
    });

    if (property === 'innerHTML') {
        element.innerHTML = value;
    } else if (property === 'textContent') {
        element.textContent = value;
    } else {
        element.setAttribute(property, value);
    }
}

function restoreNodeValue(key, element, property) {
    if (!element || !ORIGINAL_STATE.has(key)) {
        return;
    }

    const value = ORIGINAL_STATE.get(key);
    if (property === 'innerHTML') {
        element.innerHTML = value;
    } else if (property === 'textContent') {
        element.textContent = value;
    } else if (value === null || value === undefined) {
        element.removeAttribute(property);
    } else {
        element.setAttribute(property, value);
    }
}

function applyDocumentTitle(value) {
    document.title = value;
}

function restoreDocumentTitle() {
    document.title = ORIGINAL_TITLE;
}

function escapeAttribute(value) {
    return String(value).replace(/"/g, '&quot;');
}

function getHelpContent(fieldId) {
    const map = window.HELP_CONTENT_MAP || {};
    return map[currentLanguage]?.[fieldId]
        || map['zh-TW']?.[fieldId]
        || window.HELP_CONTENT?.[fieldId]
        || null;
}

function helpIconMarkup(fieldId) {
    const content = getHelpContent(fieldId);
    const title = content ? content.title : fieldId;
    const helpTitle = currentLanguage === 'en' ? `${title} help` : `${title}說明`;
    const ariaLabel = currentLanguage === 'en' ? `${title} help` : `${title} 說明`;
    return `<span class="help-icon" data-help="${fieldId}" title="${escapeAttribute(helpTitle)}" tabindex="0" role="button" aria-label="${escapeAttribute(ariaLabel)}"></span>`;
}

function fieldLabel(text, helpFieldId) {
    return `${text}${helpIconMarkup(helpFieldId)}`;
}

function setRowLabelForField(fieldId, englishHtml) {
    const input = document.getElementById(fieldId);
    const label = input?.closest('.row')?.querySelector('label.col-sm-2');
    if (!label) {
        return;
    }

    const key = `rowlabel:${fieldId}`;
    if (currentLanguage === 'en') {
        applyNodeValue(key, label, 'innerHTML', englishHtml);
    } else {
        restoreNodeValue(key, label, 'innerHTML');
    }
}

function setInputGroupTexts(fieldId, englishTexts) {
    const input = document.getElementById(fieldId);
    const texts = input?.closest('.row')?.querySelectorAll('.input-group-text');
    if (!texts || !texts.length) {
        return;
    }

    texts.forEach((item, index) => {
        const key = `inputgroup:${fieldId}:${index}`;
        if (currentLanguage === 'en') {
            applyNodeValue(key, item, 'textContent', englishTexts[index] || item.textContent);
        } else {
            restoreNodeValue(key, item, 'textContent');
        }
    });
}

function setNearestFormText(fieldId, englishHtml, occurrence = 0) {
    const input = document.getElementById(fieldId);
    const texts = input?.closest('.row')?.querySelectorAll('.form-text, small.form-text');
    const element = texts?.[occurrence];
    if (!element) {
        return;
    }

    const key = `formtext:${fieldId}:${occurrence}`;
    if (currentLanguage === 'en') {
        applyNodeValue(key, element, 'innerHTML', englishHtml);
    } else {
        restoreNodeValue(key, element, 'innerHTML');
    }
}

function setSwitchLabelForInput(inputId, englishText = 'Enabled') {
    const input = document.getElementById(inputId);
    const label = input?.closest('.form-check')?.querySelector(`label[for="${inputId}"]`);
    if (!label) {
        return;
    }

    const key = `switchlabel:${inputId}`;
    if (currentLanguage === 'en') {
        applyNodeValue(key, label, 'textContent', englishText);
    } else {
        restoreNodeValue(key, label, 'textContent');
    }
}

function renderHelpIcons() {
    document.querySelectorAll('.help-icon').forEach(function(el) {
        el.innerHTML = HELP_ICON_SVG;
    });
}

function applyOrRestore(selector, property, englishValue) {
    if (currentLanguage === 'en') {
        applyElementValue(selector, property, englishValue);
    } else {
        restoreElementValue(selector, property);
    }
}

function renderReadmePane() {
    const englishHtml = `
<div class="alert alert-info" role="alert">
  <p class="mb-0"><strong>Version</strong>: Tickets Hunter (2026.08.17) | <strong>Technical support</strong>: Claude Code AI-assisted development</p>
</div>

<div class="accordion mb-3" id="devStatusAccordion">
  <div class="accordion-item border-warning">
    <h2 class="accordion-header" id="devStatusHeading">
      <button class="accordion-button collapsed bg-warning bg-opacity-10" type="button" data-bs-toggle="collapse" data-bs-target="#devStatusCollapse" aria-expanded="false" aria-controls="devStatusCollapse">
        <span class="badge bg-warning text-dark me-2">In Development</span>
        <strong>Rapid development phase notice</strong>
      </button>
    </h2>
    <div id="devStatusCollapse" class="accordion-collapse collapse" aria-labelledby="devStatusHeading" data-bs-parent="#devStatusAccordion">
      <div class="accordion-body bg-warning bg-opacity-10">
        <p><strong>This project is currently in a rapid development phase.</strong> New features are being added continuously, so you may still encounter bugs or unstable behavior.</p>
        <hr>
        <p class="mb-0">If you run into any issue, please help by:</p>
        <ul class="mb-2">
          <li>Recording the exact reproduction steps, such as the platform and keywords used</li>
          <li>Saving a screenshot or copying the error message</li>
          <li>Joining the <a href="https://discord.gg/GCE5s6W6dV" target="_blank">Discord community</a> for discussion, or reporting it through <a href="https://github.com/bouob/tickets_hunter/issues" target="_blank">GitHub Issues</a></li>
        </ul>
        <p class="mb-0"><small>Thanks for your patience and help improving Tickets Hunter.</small></p>
      </div>
    </div>
  </div>
</div>

<hr/>

<h3>Legal notice</h3>

<div class="bd-callout bd-callout-warning">
  <strong>Important reminder for Taiwan users</strong><br/>
  Article 10 of Taiwan's Cultural and Creative Industries Development Act uses the term <code>improper means</code> without a precise definition, which means any ticketing automation software could be considered legally risky. Please evaluate your own legal exposure carefully.
</div>

<p>By using this repository or any related code, you agree to the <a href="https://github.com/bouob/tickets_hunter/blob/main/LEGAL_NOTICE.md" target="_blank">legal notice</a>. The author does not endorse or take responsibility for how the repository is used, nor for copies, forks, reuploads, or any other Tickets Hunter related content published by others. This is the author's only official account and repository. To avoid impersonation or irresponsible redistribution, please follow the GNU GPL license used by this repository.</p>

<hr/>

<h3>Quick start guide</h3>

<p>This guide is designed for <strong>first-time users</strong> and focuses on practical onboarding without requiring a programming background.</p>

<p><a href="https://github.com/bouob/tickets_hunter/blob/main/guide/README.md" target="_blank" class="btn btn-primary btn-sm mb-2">Open the full guide index</a></p>

<h4>Quick links</h4>

<ul class="mb-3">
  <li><a href="https://github.com/bouob/tickets_hunter/blob/main/guide/installation.md" target="_blank">Installation and first launch</a> - Full setup guide for packaged releases</li>
  <li><a href="https://github.com/bouob/tickets_hunter/blob/main/guide/quick-start.md" target="_blank">Python quick start</a> - Guide for source-code users</li>
  <li><a href="https://github.com/bouob/tickets_hunter/blob/main/guide/keyword-mechanism.md" target="_blank">Keyword and fallback logic</a> - Understand the selection behavior in depth</li>
  <li><a href="https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md" target="_blank">Settings reference</a> - Full field reference for settings.json</li>
</ul>

<hr/>

<h4>Support the project</h4>
<p>If this project helps you, consider buying the developer a bubble tea to support ongoing maintenance and improvements.</p>

<div class="mt-3 mb-3">
  <a href="https://buymeacoffee.com/victor0x1" target="_blank" class="btn btn-lg bmc-button">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-cup-straw" viewBox="0 0 16 16"><path d="M13.902.334a.5.5 0 0 1-.28.65l-2.254.902-.4 1.927c.376.095.715.215.972.367.228.135.56.396.56.82q0 .069-.011.132l-.962 9.068a1.28 1.28 0 0 1-.524.93c-.488.34-1.494.87-3.01.87s-2.522-.53-3.01-.87a1.28 1.28 0 0 1-.524-.93L3.51 5.132A1 1 0 0 1 3.5 5c0-.424.332-.685.56-.82.262-.154.607-.276.99-.372L5.024 2.02 2.595.903a.5.5 0 0 1 .37-.928L5.643 1.25l.4-1.922a.5.5 0 0 1 .976.206L6.596 1.88q.376-.031.774-.04L7.5 1a.5.5 0 0 1 .5.42l.157.753q.396.01.77.04l-.42-1.685a.5.5 0 1 1 .97-.242l.42 1.681.157-.753A.5.5 0 0 1 10.5 1l.13.84q.4.01.776.04l.423-1.686a.5.5 0 0 1 .97.242l-.42 1.68q.376.05.726.115l.399-1.917a.5.5 0 0 1 .398-.28M6.08 5.21a.5.5 0 0 1 0 .58l-.545.82a.5.5 0 0 1-.83-.554l.545-.82a.5.5 0 0 1 .83-.027M7.5 3.5a.5.5 0 0 1 .5.42l.5 3a.5.5 0 0 1-.99.16l-.5-3a.5.5 0 0 1 .49-.58"/></svg>
    <span>Buy me a bubble tea</span>
  </a>
</div>`;
    applyOrRestore('#readme-tab-pane', 'innerHTML', englishHtml);
}

function renderPageChrome() {
    applyDocumentTitle(ORIGINAL_TITLE);
    restoreElementValue('#page_title', 'innerHTML');
    applyOrRestore('#readme-tab', 'textContent', 'Getting Started');
    applyOrRestore('#home-tab', 'textContent', 'Basic Settings');
    applyOrRestore('#advanced-tab', 'textContent', 'Advanced');
    applyOrRestore('#verification-tab', 'textContent', 'Verification');
    applyOrRestore('#autofill-tab', 'textContent', 'Autofill');
    applyOrRestore('#runtime-tab', 'textContent', 'Runtime');
    applyOrRestore('a[href="https://discord.gg/GCE5s6W6dV"]', 'textContent', 'Discord');
    applyOrRestore('a[href="https://github.com/bouob/tickets_hunter/issues"]', 'textContent', 'Report Issue');
    applyOrRestore('label[for="language_selector"]', 'textContent', 'Language');
    restoreElementValue('#language_selector option[value="zh-TW"]', 'textContent');
    applyOrRestore('#language_selector option[value="en"]', 'textContent', 'English');
    applyOrRestore('label[for="dark_mode_toggle"]', 'textContent', 'Dark Mode');
    applyOrRestore('#run_btn', 'textContent', 'Run');
    applyOrRestore('#save_btn', 'textContent', 'Save');
    applyOrRestore('#reset_btn', 'textContent', 'Reset to Defaults');
    applyOrRestore('#exit_btn', 'textContent', 'Exit');
    applyOrRestore('#message_modal .btn-close', 'aria-label', 'Close');
    applyOrRestore('#message_modal .modal-footer button', 'textContent', 'Close');
    applyOrRestore('#helpPanelTitle', 'textContent', 'Help');
    applyOrRestore('#helpPanel .btn-close', 'aria-label', 'Close');
    applyOrRestore('#helpPanelLink', 'textContent', 'View full guide on GitHub');
}

function renderBasicTabTranslations() {
    setSwitchLabelForInput('date_auto_fallback');
    setSwitchLabelForInput('area_auto_fallback');
    applyOrRestore('#accordionExample .accordion-button', 'textContent', 'Supported ticketing platforms');
    applyOrRestore('#collapseSites .accordion-body', 'innerHTML', `
<h6><strong>Taiwan</strong></h6>
<div class="mb-3">
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://tixcraft.com')">Tixcraft</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://www.teamear.com')">Teamear</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://www.indievox.com')">Indievox</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://kktix.com')">KKTIX</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://ticket.ibon.com.tw')">iBon</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://www.famiticket.com.tw')">FamiTicket</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://kham.com.tw')">Kham</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://ticket.com.tw')">Ticket.com.tw</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://tickets.udnfunlife.com')">UDN</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://ticketplus.com.tw')">TicketPlus</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://tickets.funone.io')">FunOne Tickets</button>
  <button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="fillHomepage('https://go.fansi.me')">FANSI GO</button>
</div>

<h6><strong>International</strong></h6>
<div class="mb-0">
  <button type="button" class="btn btn-outline-secondary btn-sm me-2 mb-2" onclick="fillHomepage('https://ticket.urbtix.hk')">Urbtix</button>
  <button type="button" class="btn btn-outline-secondary btn-sm me-2 mb-2" onclick="fillHomepage('https://www.cityline.com')">Cityline</button>
  <button type="button" class="btn btn-outline-secondary btn-sm me-2 mb-2" onclick="fillHomepage('https://hotshow.hkticketing.com/')">HKTicketing</button>
  <button type="button" class="btn btn-outline-secondary btn-sm me-2 mb-2" onclick="fillHomepage('https://www.galaxymacau.com')">Galaxy Macau</button>
  <button type="button" class="btn btn-outline-secondary btn-sm me-2 mb-2" onclick="fillHomepage('https://www.ticketmaster.sg')">Ticketmaster Singapore</button>
  <button type="button" class="btn btn-outline-secondary btn-sm me-2 mb-2" onclick="fillHomepage('https://www.ticketek.com.au')">Ticketek Australia</button>
</div>`);
    applyOrRestore('#refresh_datetime', 'placeholder', 'YYYY/MM/DD HH:MM:SS');
    applyOrRestore('#ticket_number option[selected="selected"]', 'textContent', 'Tickets');

    setRowLabelForField('homepage', fieldLabel('Homepage', 'homepage'));
    setRowLabelForField('auto_press_next_step_button', fieldLabel('Auto-click KKTIX next step', 'auto_press_next_step_button'));
    setRowLabelForField('max_dwell_time', fieldLabel('KKTIX max dwell time (sec)', 'max_dwell_time'));
    setRowLabelForField('ticket_number', fieldLabel('Tickets', 'ticket_number'));
    setRowLabelForField('refresh_datetime', fieldLabel('Refresh at specific time', 'refresh_datetime'));
    setRowLabelForField('date_select_mode', fieldLabel('Date selection order', 'date_select_mode'));
    setRowLabelForField('date_keyword', fieldLabel('Date keywords', 'date_keyword'));
    setRowLabelForField('date_auto_fallback', fieldLabel('Date fallback', 'date_auto_fallback'));
    setRowLabelForField('area_select_mode', fieldLabel('Area selection order', 'area_select_mode'));
    setRowLabelForField('area_keyword', fieldLabel('Area keywords', 'area_keyword'));
    setRowLabelForField('area_auto_fallback', fieldLabel('Area fallback', 'area_auto_fallback'));
    setRowLabelForField('keyword_exclude', fieldLabel('Exclude keywords', 'keyword_exclude'));

    const versionLabel = document.querySelector('#maxbot_version')?.closest('.row')?.querySelector('label.col-sm-2');
    if (versionLabel) {
        if (currentLanguage === 'en') {
            applyNodeValue('rowlabel:maxbot_version', versionLabel, 'textContent', 'Version');
        } else {
            restoreNodeValue('rowlabel:maxbot_version', versionLabel, 'textContent');
        }
    }

    applyOrRestore('#collapseDateLogic .accordion-button', 'textContent', 'Date keyword logic');
    applyOrRestore('#collapseAreaLogic .accordion-button', 'textContent', 'Area keyword logic');
    applyOrRestore('#collapseDateLogic .accordion-body', 'innerHTML', `
<p><strong>OR logic (match any)</strong>: <code>9/11;9/22;3/3</code><br>
Try each keyword group in order and select the first match.</p>
<p><strong>AND logic (match all)</strong>: <code>9/11 weekend;9/22 weekday</code><br>
Keywords separated by spaces inside one group must all match.</p>
<p><strong>Example</strong>:<br><code>2024/12/25 evening;2024/12/26 afternoon;weekend</code></p>`);
    applyOrRestore('#collapseAreaLogic .accordion-body', 'innerHTML', `
<p><strong>OR logic (match any)</strong>: <code>Rock;VIP;Front Row</code><br>
Select the first matching area or ticket type.</p>
<p><strong>AND logic (combined condition)</strong>: <code>Rock Front;VIP Center</code><br>
Keywords separated by spaces inside one group must all appear in the option.</p>`);

    const orderTranslations = {
        'from top to bottom': 'Top to bottom',
        'from bottom to top': 'Bottom to top',
        'center': 'Center',
        'random': 'Random',
    };
    [date_select_mode, area_select_mode].forEach((select) => {
        if (!select) return;
        Array.from(select.options).forEach((option) => {
            if (currentLanguage === 'en') {
                option.textContent = orderTranslations[option.value] || option.value;
            } else {
                option.textContent = option.value;
            }
        });
    });
}

function renderAdvancedTabTranslations() {
    setSwitchLabelForInput('play_ticket_sound');
    setSwitchLabelForInput('play_order_sound');
    setSwitchLabelForInput('disable_adjacent_seat');
    setSwitchLabelForInput('hide_some_image');
    setSwitchLabelForInput('block_facebook_network');
    setSwitchLabelForInput('headless');
    setSwitchLabelForInput('verbose');
    setSwitchLabelForInput('show_timestamp');
    setSwitchLabelForInput('tixcraft_allow_less_tickets');
    setSwitchLabelForInput('ocr_captcha_enable');
    setSwitchLabelForInput('ocr_captcha_force_submit');
    setSwitchLabelForInput('ocr_captcha_use_universal');
    setRowLabelForField('play_ticket_sound', fieldLabel('Play sound when tickets are found', 'play_ticket_sound'));
    setRowLabelForField('play_order_sound', fieldLabel('Play sound when submitting the order', 'play_order_sound'));
    setRowLabelForField('play_sound_filename', fieldLabel('Sound file', 'play_sound_filename'));
    setRowLabelForField('discord_webhook_url', fieldLabel('Discord webhook URL', 'discord_webhook_url'));
    setRowLabelForField('telegram_bot_token', fieldLabel('Telegram bot token', 'telegram_bot_token'));
    setRowLabelForField('telegram_chat_id', fieldLabel('Telegram chat ID', 'telegram_chat_id'));
    setRowLabelForField('notification_message', 'Notification message');
    setRowLabelForField('auto_reload_page_interval', fieldLabel('Auto reload interval (sec)', 'auto_reload_page_interval'));
    setRowLabelForField('tixcraft_soft_block_delay', fieldLabel('TixCraft soft-block delay (sec)', 'tixcraft_soft_block_delay'));
    setRowLabelForField('tixcraft_allow_less_tickets', fieldLabel('Buy fewer TixCraft tickets if needed', 'tixcraft_allow_less_tickets'));
    setRowLabelForField('reset_browser_interval', fieldLabel('Browser restart interval (sec)', 'reset_browser_interval'));
    setRowLabelForField('server_port', fieldLabel('Settings UI port', 'server_port'));
    setRowLabelForField('proxy_server_port', fieldLabel('Proxy IP:PORT', 'proxy_server_port'));
    setRowLabelForField('window_size', fieldLabel('Browser window size', 'window_size'));
    setRowLabelForField('disable_adjacent_seat', fieldLabel('Allow non-adjacent seats', 'disable_adjacent_seat'));
    setRowLabelForField('hide_some_image', fieldLabel('Hide some images', 'hide_some_image'));
    setRowLabelForField('block_facebook_network', fieldLabel('Block Facebook requests', 'block_facebook_network'));
    setRowLabelForField('headless', fieldLabel('Headless mode', 'headless'));
    setRowLabelForField('verbose', fieldLabel('Verbose logs', 'verbose'));
    setRowLabelForField('show_timestamp', fieldLabel('Show timestamps', 'show_timestamp'));
    setRowLabelForField('ocr_captcha_enable', fieldLabel('OCR', 'ocr_captcha_enable'));
    setRowLabelForField('ocr_captcha_image_source', fieldLabel('OCR image source', 'ocr_captcha_image_source'));
    setRowLabelForField('ocr_captcha_force_submit', fieldLabel('Auto-submit', 'ocr_captcha_force_submit'));
    setRowLabelForField('ocr_captcha_use_universal', fieldLabel('Use universal model', 'ocr_captcha_use_universal'));
    setRowLabelForField('remote_url', fieldLabel('OCR server URL', 'remote_url'));
    setRowLabelForField('ocr_model_path', fieldLabel('Custom OCR model', 'ocr_model_path'));

    applyOrRestore('#btn_test_discord_webhook', 'textContent', 'Test');
    applyOrRestore('#btn_test_telegram', 'textContent', 'Test');
    applyOrRestore('#notification_message', 'placeholder', 'Leave empty to use the default English notification');
    applyOrRestore('#discord_webhook_url', 'placeholder', 'https://discord.com/api/webhooks/...');
    applyOrRestore('#telegram_bot_token', 'placeholder', '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11');
    applyOrRestore('#telegram_chat_id', 'placeholder', '123456789, 987654321');
    applyOrRestore('#server_port', 'placeholder', '16888');
    applyOrRestore('#tixcraft_soft_block_delay', 'placeholder', 'Leave empty to use the default 240-420 seconds');
    applyOrRestore('#ocr_model_path', 'placeholder', 'Example: assets/ocr_model or C:\\models\\my_ocr');

    setNearestFormText('notification_message', 'This message will be sent to both Discord and Telegram when tickets are found. Leave it empty to keep the default message.');
    setNearestFormText('tixcraft_soft_block_delay', 'Applies only to the TixCraft, TeamEar, and Indievox soft-block white screen. Leave it empty to keep the default randomized delay.');
    setNearestFormText('tixcraft_allow_less_tickets', 'Applies to TixCraft, TeamEar, Indievox, and Ticketmaster. When enabled, Tickets Hunter buys the largest available count below your configured ticket count if the exact count is unavailable.');
    setNearestFormText('ocr_captcha_use_universal', 'When enabled, Tickets Hunter uses the self-trained OCR model instead of the upstream ddddocr model and beta configuration.');
    setNearestFormText('ocr_model_path', 'Path to the custom OCR model <strong>folder</strong>. The folder must contain <code>custom.onnx</code> and <code>charsets.json</code>. Relative paths are supported. If left empty, the built-in ddddocr model is used.');

    applyOrRestore('#tixcraft-refresh-warning', 'innerHTML', `
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-exclamation-triangle-fill me-2" viewBox="0 0 16 16">
  <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
</svg>
<strong>Tixcraft refresh warning:</strong> Refresh intervals below 8 seconds may trigger a temporary IP soft block. Use 8 seconds or more, or distribute requests across different networks or devices.
<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`);
}

function renderVerificationTabTranslations() {
    setSwitchLabelForInput('auto_guess_options');
    setRowLabelForField('user_guess_string', fieldLabel('Custom answer dictionary', 'user_guess_string'));
    setRowLabelForField('auto_guess_options', fieldLabel('Auto-guess verification options', 'auto_guess_options'));
    setRowLabelForField('discount_code', fieldLabel('Discount / member code', 'discount_code'));

    applyOrRestore('#user_guess_string', 'placeholder', 'Separate multiple answers with semicolons, for example: answer A;answer B;answer C');
    applyOrRestore('#discount_code', 'placeholder', 'Discount code / add-on code / member code');
    setNearestFormText('user_guess_string', 'When a verification question is detected, Tickets Hunter will try these answers first. If left empty and auto-guess is enabled, it will attempt to infer the answer automatically.');
    setNearestFormText('auto_guess_options', 'When the custom answer dictionary is empty, Tickets Hunter will try to infer the answer from the question text, such as dates or time slots.');
    setNearestFormText('discount_code', 'Used for platform-specific discount, add-on, or member codes. The value is also used as the final TixCraft fallback when the custom answer dictionary is empty and auto-guess is disabled.');

    const detectedHeading = document.querySelector('#detected-question-alert .alert-heading');
    if (detectedHeading) {
        if (currentLanguage === 'en') {
            applyNodeValue('detected-question-heading', detectedHeading, 'innerHTML', `${QUESTION_ALERT_ICON}Verification question detected!`);
        } else {
            restoreNodeValue('detected-question-heading', detectedHeading, 'innerHTML');
        }
    }
    applyOrRestore('#detected-question-alert p.mb-2', 'innerHTML', '<strong>Question:</strong>');
    applyOrRestore('#detected-question-alert small.text-muted', 'innerHTML', `${INFO_ICON_SVG}Tip: if auto-answer fails, search above and then copy the result into the custom answer dictionary field.`);

    applyOrRestore('#question-instance-row > label', 'textContent', 'Answer target instance');
    applyOrRestore('#question-instance-row .form-text', 'textContent', 'Defaults to the active tab; pick another running instance to monitor its pending question.');
}

function renderAutofillTabTranslations() {
    applyOrRestore('#autofill-tab-pane .card-header h6', 'textContent', 'Shared personal information');
    setRowLabelForField('real_name', 'Full name');
    setRowLabelForField('phone', 'Mobile number');
    setRowLabelForField('credit_card_prefix', 'First 6 digits of card');
    applyOrRestore('#real_name', 'placeholder', 'Enter your legal name');
    applyOrRestore('#phone', 'placeholder', 'Example: 0912345678');
    applyOrRestore('#credit_card_prefix', 'placeholder', 'Example: 412345');
    setNearestFormText('credit_card_prefix', 'Some platforms may require the first 6 digits of the credit card for verification.');

    setRowLabelForField('tixcraft_sid', fieldLabel('Tixcraft family cookie (TIXUISID / IVUISID / TIXPUISID)', 'tixcraft_sid'));
    setRowLabelForField('ibonqware', fieldLabel('iBon cookie ibonqware', 'ibonqware'));
    setRowLabelForField('funone_session_cookie', fieldLabel('FunOne cookie (ticket_session)', 'funone_session_cookie'));
    setRowLabelForField('fansigo_cookie', fieldLabel('FANSI GO cookie (FansiAuthInfo)', 'fansigo_cookie'));
    setRowLabelForField('discount_code', fieldLabel('Discount / member code', 'discount_code'));

    setInputGroupTexts('fansigo_account', ['Email', 'Password']);
    setInputGroupTexts('facebook_account', ['Account', 'Password']);
    setInputGroupTexts('kktix_account', ['Account', 'Password']);
    setInputGroupTexts('fami_account', ['Account', 'Password']);
    setInputGroupTexts('kham_account', ['Account', 'Password']);
    setInputGroupTexts('ticket_account', ['Account', 'Password']);
    setInputGroupTexts('udn_account', ['Account', 'Password']);
    setInputGroupTexts('ticketplus_account', ['Account', 'Password']);
    setInputGroupTexts('cityline_account', ['Email']);
    setInputGroupTexts('urbtix_account', ['Account', 'Password']);
    setInputGroupTexts('hkticketing_account', ['Account', 'Password']);

    applyOrRestore('#cityline_account', 'placeholder', 'Enter your email address');
    setRowLabelForField('fansigo_account', 'FANSI GO');
    setRowLabelForField('facebook_account', 'Facebook');
    setRowLabelForField('kktix_account', 'KKTIX');
    setRowLabelForField('fami_account', 'FamiTicket');
    setRowLabelForField('kham_account', 'Kham');
    setRowLabelForField('ticket_account', 'Ticket.com.tw');
    setRowLabelForField('udn_account', 'UDN');
    setRowLabelForField('ticketplus_account', 'TicketPlus');
    setRowLabelForField('cityline_account', 'Cityline');
    setRowLabelForField('urbtix_account', 'URBTIX');
    setRowLabelForField('hkticketing_account', 'HKTICKETING');
    applyOrRestore('#cityline-login-hint .col', 'innerHTML', `
<strong>Cityline login notes (semi-automatic mode):</strong>
<ol class="mb-0 mt-2">
  <li>Tickets Hunter auto-fills the account email</li>
  <li>Retrieve the verification code from your mailbox and enter it manually</li>
  <li>Complete the Cloudflare Turnstile verification</li>
  <li>After verification, click the login button manually</li>
  <li>Once logged in, Tickets Hunter detects the success state and continues automatically</li>
</ol>`);
    applyOrRestore('#tixcraft-sid-warning', 'innerHTML', `
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-exclamation-triangle-fill me-2" viewBox="0 0 16 16">
  <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
</svg>
<strong>Warning:</strong> The pasted value may not be a valid TIXUISID. A real TIXUISID should not start with "g.".
<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`);
    const hkticketingWarning = hkticketing_account?.closest('.row')?.querySelector('.alert');
    if (hkticketingWarning) {
        if (currentLanguage === 'en') {
            applyNodeValue('hkticketing-warning', hkticketingWarning, 'innerHTML', '<strong>Security warning:</strong> Saving passwords in the settings file may expose your credentials if the file is leaked.');
        } else {
            restoreNodeValue('hkticketing-warning', hkticketingWarning, 'innerHTML');
        }
    }
}

function renderRuntimeTabTranslations() {
    // Exclude the dynamically-added instances panel so the positional labels
    // below still map to the status / url / system-time rows.
    const runtimeRows = document.querySelectorAll('#runtime-tab-pane > .row:not(#instances_panel)');
    if (runtimeRows.length >= 3) {
        if (currentLanguage === 'en') {
            applyNodeValue('runtime-label-0', runtimeRows[0].querySelector('label.col-sm-2'), 'textContent', 'Runtime status');
            applyNodeValue('runtime-label-1', runtimeRows[1].querySelector('label.col-sm-2'), 'textContent', 'Current URL');
            applyNodeValue('runtime-label-2', runtimeRows[2].querySelector('label.col-sm-2'), 'textContent', 'System time');
        } else {
            restoreNodeValue('runtime-label-0', runtimeRows[0].querySelector('label.col-sm-2'), 'textContent');
            restoreNodeValue('runtime-label-1', runtimeRows[1].querySelector('label.col-sm-2'), 'textContent');
            restoreNodeValue('runtime-label-2', runtimeRows[2].querySelector('label.col-sm-2'), 'textContent');
        }
    }
    applyOrRestore('#pause_btn', 'textContent', 'Pause');
    applyOrRestore('#resume_btn', 'textContent', 'Resume');
    setRowLabelForField('idle_keyword', fieldLabel('System time - <span class="text-danger">Pause</span> keywords', 'idle_keyword'));
    setRowLabelForField('resume_keyword', fieldLabel('System time - <span class="text-success">Resume</span> keywords', 'resume_keyword'));
    setRowLabelForField('idle_keyword_second', fieldLabel('Seconds - <span class="text-danger">Pause</span> keywords', 'idle_keyword_second'));
    setRowLabelForField('resume_keyword_second', fieldLabel('Seconds - <span class="text-success">Resume</span> keywords', 'resume_keyword_second'));

    applyOrRestore('#idle_keyword', 'placeholder', 'Example: 09:30:00;14:15:30');
    applyOrRestore('#resume_keyword', 'placeholder', 'Example: 09:35:00;14:20:30');
    applyOrRestore('#idle_keyword_second', 'placeholder', 'Example: 00;30;50');
    applyOrRestore('#resume_keyword_second', 'placeholder', 'Example: 05;35;55');
    applyOrRestore('#accordionRuntimeHelp .accordion-button', 'textContent', 'Time control guide');
    applyOrRestore('#collapseRuntimeHelp .accordion-body', 'innerHTML', `
<strong>How it works:</strong>
<ul class="mb-3">
  <li><strong>System time keywords:</strong> use the <code>HH:MM:SS</code> format</li>
  <li><strong>Second keywords:</strong> use only the <code>SS</code> part to trigger at specific seconds of every minute</li>
  <li><strong>Pause:</strong> matching pause keywords temporarily stops ticket actions</li>
  <li><strong>Resume:</strong> matching resume keywords continues ticket actions automatically</li>
</ul>

<div class="alert alert-success mb-3">
  <strong>Input examples:</strong>
  <div class="row">
    <div class="col-md-6">
      <strong>System time:</strong>
      <ul class="mb-1">
        <li><code>09:30:00;15:55:00</code></li>
        <li><code>"09:30:00";"15:55:00"</code></li>
        <li><code>14:30:00</code> (single time)</li>
      </ul>
    </div>
    <div class="col-md-6">
      <strong>Seconds:</strong>
      <ul class="mb-1">
        <li><code>00;30;50</code></li>
        <li><code>"00";"30";"50"</code></li>
        <li><code>30</code> (single second)</li>
      </ul>
    </div>
  </div>
</div>

<div class="alert alert-warning mb-0">
  <strong>Notes:</strong>
  <ul class="mb-0">
    <li>Time formats must be exact or the feature will not trigger</li>
    <li>Tickets Hunter checks system time continuously and executes actions immediately after a match</li>
    <li>Use pause and resume together so the bot does not stay paused indefinitely</li>
    <li>Second-based keywords are useful for periodic control within every minute</li>
  </ul>
</div>`);

    // Instances dashboard (Phase 3) static labels.
    applyOrRestore('#instances_panel > label', 'textContent', 'Running instances');
    applyOrRestore('#pause_all_btn', 'textContent', 'Pause all');
    applyOrRestore('#instances_panel .text-muted.small', 'textContent', 'Refreshes every 2s; offline = no heartbeat for 30s');
    applyOrRestore('#instances_panel thead th:nth-child(1)', 'textContent', 'Instance');
    applyOrRestore('#instances_panel thead th:nth-child(2)', 'textContent', 'Liveness');
    applyOrRestore('#instances_panel thead th:nth-child(3)', 'textContent', 'State');
    applyOrRestore('#instances_panel thead th:nth-child(4)', 'textContent', 'Current URL');
}

function renderProfileBarTranslations() {
    // Top-of-page profile bar + the "add profile" modal (outside the tabs).
    applyOrRestore('#profile_bar > span.text-muted', 'textContent', 'Profiles:');
    applyOrRestore('#profile_add_btn', 'textContent', '+ Add');
    applyOrRestore('#profile_add_btn', 'title', 'Add an instance profile (choose a platform)');
    applyOrRestore('#profile_modal .modal-title', 'textContent', 'Add instance profile');
    applyOrRestore('#profile_modal .modal-body > p.text-muted', 'textContent', 'Choosing a platform creates a new profile from the current settings (homepage auto-filled). Each profile can launch as its own instance.');
    applyOrRestore('#profile_custom_name', 'placeholder', 'Custom name (letters, digits, underscore, hyphen)');
    applyOrRestore('#profile_modal .input-group button', 'textContent', 'Create blank');
}

function renderStaticTranslations() {
    renderPageChrome();
    renderProfileBarTranslations();
    renderReadmePane();
    renderBasicTabTranslations();
    renderAdvancedTabTranslations();
    renderVerificationTabTranslations();
    renderAutofillTabTranslations();
    renderRuntimeTabTranslations();
    renderHelpIcons();
}

function applyLanguage(language) {
    currentLanguage = normalizeLanguage(language);
    document.documentElement.lang = currentLanguage === 'en' ? 'en' : 'zh-Hant';
    if (language_selector) {
        language_selector.value = currentLanguage;
    }
    renderStaticTranslations();
    // Warning badges are dynamic; re-render them in the new language.
    if (typeof update_multi_open_warnings === 'function') update_multi_open_warnings(last_profile_details);
    updateThemeStatus(document.documentElement.getAttribute('data-bs-theme') || 'light');

    if (currentHelpField) {
        const openField = currentHelpField;
        currentHelpField = null;
        showHelp(openField);
    }
}

function uiText(key, extra = '') {
    const messages = {
        'reset_done': { 'zh-TW': '已重設為預設值', en: 'Reset to defaults' },
        'launching': { 'zh-TW': '啟動 MaxBot 主程式中...', en: 'Launching Tickets Hunter...' },
        'launch_sent': { 'zh-TW': '啟動指令已發送，請稍候瀏覽器視窗開啟...', en: 'Launch request sent. Please wait for the browser window...' },
        'launch_failed': { 'zh-TW': `啟動失敗：無法連線到後端服務 (${extra})`, en: `Launch failed: cannot connect to the backend service (${extra})` },
        'save_failed': { 'zh-TW': `儲存失敗：${extra}`, en: `Save failed: ${extra}` },
        'saving': { 'zh-TW': '儲存中...', en: 'Saving...' },
        'saved': { 'zh-TW': '已存檔', en: 'Saved' },
        'missing_ticket_number': { 'zh-TW': '提示: 請指定張數', en: 'Please select the number of tickets.' },
        'invalid_tixcraft_soft_block_delay': { 'zh-TW': '提示: 暫時鎖定等待秒數請填 1 到 600 的整數，或留空使用預設值。', en: 'Enter an integer from 1 to 600 for the TixCraft soft-block delay, or leave it empty to use the default.' },
        'status_paused': { 'zh-TW': '已暫停', en: 'Paused' },
        'status_running': { 'zh-TW': '已啟動', en: 'Running' },
        'discord_empty': { 'zh-TW': '請先輸入 Discord Webhook URL。', en: 'Please enter the Discord webhook URL first.' },
        'telegram_empty': { 'zh-TW': '請先輸入 Telegram Bot Token 與 Chat ID。', en: 'Please enter both the Telegram bot token and chat ID first.' },
        'test_failed': { 'zh-TW': `測試失敗：${extra}`, en: `Test failed: ${extra}` },
        'copy_failed': { 'zh-TW': `無法自動複製問題。請手動複製：\n\n${extra}`, en: `Unable to copy automatically. Please copy this manually:\n\n${extra}` },
        'copied_notice': { 'zh-TW': `問題已複製！請貼上到 ${extra}`, en: `Prompt copied. Paste it into ${extra}` },
        'dup_run_confirm': { 'zh-TW': '此設定檔已有執行中的實例。同帳號同活動多開可能被平台踢掉登入狀態 (session)。仍要再開一個實例嗎？', en: 'This profile already has a running instance. Opening another with the same account on the same event may get your session kicked by the platform. Open another instance anyway?' },
        'instance_alive': { 'zh-TW': '存活', en: 'Alive' },
        'instance_offline': { 'zh-TW': '離線', en: 'Offline' },
        'instance_paused': { 'zh-TW': '暫停', en: 'Paused' },
        'instance_running': { 'zh-TW': '運行中', en: 'Running' },
        'btn_pause': { 'zh-TW': '暫停', en: 'Pause' },
        'btn_resume': { 'zh-TW': '繼續', en: 'Resume' },
        'btn_stop': { 'zh-TW': '停止', en: 'Stop' },
        'stop_confirm': { 'zh-TW': `停止會關閉實例「${extra}」的瀏覽器並結束行程，無法復原。確定要停止嗎？`, en: `Stopping closes the browser for instance "${extra}" and ends its process. This cannot be undone. Stop it?` },
        'risk_kktix': { 'zh-TW': 'KKTIX 多開風險：可能打亂排隊順序甚至被導入假排隊', en: 'KKTIX multi-open risk: may disrupt your queue order or trap you in a fake queue' },
        'risk_tixcraft': { 'zh-TW': '拓元/遠大多開風險：同帳號同活動會被踢 session', en: 'Tixcraft family multi-open risk: same account on the same event gets session-kicked' },
        'risk_ibon': { 'zh-TW': 'iBon 多開風險：Queue-it 排隊序可能受影響', en: 'iBon multi-open risk: Queue-it ordering may be affected' },
        'question_target_active': { 'zh-TW': '（目前分頁）', en: '(active tab)' },
    };

    return messages[key]?.[currentLanguage] || messages[key]?.['zh-TW'] || '';
}

// ===== Instance profiles (multi-instance) =====
// Each profile = one full settings json under profiles/<name>.json.
// "default" maps to settings.json. The active profile is kept in
// localStorage only (no schema change in settings.json).

const PROFILE_PLATFORMS = [
    { slug: 'tixcraft',     label: 'Tixcraft 拓元',    homepage: 'https://tixcraft.com' },
    { slug: 'kktix',        label: 'KKTIX',            homepage: 'https://kktix.com' },
    { slug: 'ibon',         label: 'iBon',             homepage: 'https://ticket.ibon.com.tw' },
    { slug: 'famiticket',   label: 'FamiTicket 全網',  homepage: 'https://www.famiticket.com.tw' },
    { slug: 'kham',         label: 'Kham 寬宏',        homepage: 'https://kham.com.tw' },
    { slug: 'ticket',       label: '年代售票',          homepage: 'https://ticket.com.tw' },
    { slug: 'udn',          label: 'UDN 售票網',        homepage: 'https://tickets.udnfunlife.com' },
    { slug: 'ticketplus',   label: 'TicketPlus 遠大',  homepage: 'https://ticketplus.com.tw' },
    { slug: 'funone',       label: 'FunOne',           homepage: 'https://tickets.funone.io' },
    { slug: 'fansigo',      label: 'FANSI GO',         homepage: 'https://go.fansi.me' },
    { slug: 'cityline',     label: 'Cityline',         homepage: 'https://www.cityline.com' },
    { slug: 'urbtix',       label: 'Urbtix',           homepage: 'https://ticket.urbtix.hk' },
    { slug: 'hkticketing',  label: 'HKTicketing',      homepage: 'https://hotshow.hkticketing.com/' },
    { slug: 'ticketmaster', label: 'TicketMaster SG',  homepage: 'https://www.ticketmaster.sg' },
];

const PROFILE_STORAGE_KEY = 'maxbot_current_profile';
let current_profile = localStorage.getItem(PROFILE_STORAGE_KEY) || 'default';

function profile_query() {
    return (current_profile && current_profile !== 'default')
        ? '?profile=' + encodeURIComponent(current_profile) : '';
}

function refresh_profile_tabs(callback) {
    $.get('/profiles').done(function(data) {
        const profiles = (data && data.profiles) ? data.profiles : ['default'];
        const details = (data && data.details) ? data.details : profiles.map(function(n) { return { name: n, homepage: '' }; });
        if (!profiles.includes(current_profile)) {
            current_profile = 'default';
            localStorage.setItem(PROFILE_STORAGE_KEY, current_profile);
        }
        const container = $('#profile_tabs');
        container.empty();
        details.forEach(function(d) {
            const name = d.name;
            const li = $('<li class="nav-item"></li>');
            const btn = $('<button type="button" class="nav-link py-1 px-3"></button>').text(name);
            if (d.homepage) btn.attr('title', d.homepage);
            if (name === current_profile) btn.addClass('active');
            btn.on('click', function() { switch_profile(name); });
            if (name !== 'default') {
                const close = $('<span class="ms-2" style="cursor:pointer;" title="刪除此設定檔">&times;</span>');
                close.on('click', function(ev) {
                    ev.stopPropagation();
                    delete_profile(name);
                });
                btn.append(close);
            }
            li.append(btn);
            container.append(li);
        });
        update_multi_open_warnings(details);
        if (callback) callback(profiles);
    }).fail(function() {
        // Profile API unavailable (old backend): hide the bar, keep legacy behavior.
        $('#profile_bar').addClass('d-none');
        if (callback) callback(['default']);
    });
}

function switch_profile(name) {
    if (name === current_profile) return;
    current_profile = name;
    localStorage.setItem(PROFILE_STORAGE_KEY, name);
    // Reset question alert so the new tab's pending question shows immediately
    if (typeof lastDetectedQuestion !== 'undefined') lastDetectedQuestion = '';
    refresh_profile_tabs();
    maxbot_load_api();
}

// Multi-open risk per platform: show a badge when >=2 profiles target the same
// risk-bearing platform. Matched by homepage substring so renamed/custom
// profiles still count. Text flows through uiText() for i18n.
const PROFILE_MULTI_OPEN_RISKS = [
    { match: 'kktix.c',      key: 'risk_kktix' },
    { match: 'tixcraft.com', key: 'risk_tixcraft' },
    { match: 'ticketmaster', key: 'risk_tixcraft' },
    { match: 'ibon',         key: 'risk_ibon' },
];

// Cache the last profile details so a language switch can re-render the
// (dynamic) warning badges, which renderStaticTranslations does not cover.
let last_profile_details = [];

function update_multi_open_warnings(details) {
    last_profile_details = details || [];
    const container = $('#profile_warnings');
    container.empty();
    const shown = new Set();
    PROFILE_MULTI_OPEN_RISKS.forEach(function(risk) {
        const count = (details || []).filter(function(d) {
            return (d.homepage || '').indexOf(risk.match) >= 0;
        }).length;
        if (count >= 2 && !shown.has(risk.key)) {
            shown.add(risk.key);
            const text = uiText(risk.key);
            $('<span class="badge text-bg-warning"></span>').text(text).attr('title', text).appendTo(container);
        }
    });
}

function show_profile_modal() {
    const container = $('#profile_platform_buttons');
    container.empty();
    PROFILE_PLATFORMS.forEach(function(p) {
        const btn = $('<button type="button" class="btn btn-outline-primary btn-sm me-2 mb-2"></button>').text(p.label);
        btn.on('click', function() { create_profile_for_platform(p.slug, p.homepage); });
        container.append(btn);
    });
    $('#profile_modal_error').addClass('d-none');
    $('#profile_custom_name').val('');
    $('#profile_modal').modal('show');
}

function profile_modal_error(msg) {
    $('#profile_modal_error').removeClass('d-none').text(msg);
}

function create_profile_for_platform(slug, homepage) {
    $.get('/profiles').done(function(data) {
        const existing = (data && data.profiles) ? data.profiles : [];
        let name = slug;
        let n = 2;
        while (existing.includes(name)) { name = slug + '-' + n; n++; }
        create_profile(name, homepage);
    });
}

function create_profile_custom() {
    const name = ($('#profile_custom_name').val() || '').trim();
    if (!/^[A-Za-z0-9_-]{1,32}$/.test(name) || name === 'default') {
        profile_modal_error('名稱限英數、底線、連字號（最長 32 字元），且不可為 default');
        return;
    }
    create_profile(name, '');
}

function create_profile(name, homepage) {
    // Clone current form settings as the base config for the new profile.
    const cfg = settings ? JSON.parse(JSON.stringify(settings)) : null;
    if (cfg && homepage) cfg.homepage = homepage;
    $.ajax({
        url: '/profiles',
        method: 'POST',
        data: JSON.stringify({ name: name, config: cfg })
    }).done(function() {
        $('#profile_modal').modal('hide');
        current_profile = name;
        localStorage.setItem(PROFILE_STORAGE_KEY, name);
        refresh_profile_tabs();
        maxbot_load_api();
    }).fail(function(xhr) {
        let msg = '建立失敗';
        try { msg = JSON.parse(xhr.responseText).error || msg; } catch (e) {}
        profile_modal_error(msg);
    });
}

function delete_profile(name) {
    if (!window.confirm('刪除設定檔「' + name + '」？運行中的實例不會被停止，但設定將無法再熱更新。')) return;
    $.ajax({
        url: '/profiles?profile=' + encodeURIComponent(name),
        method: 'DELETE'
    }).done(function() {
        if (current_profile === name) {
            current_profile = 'default';
            localStorage.setItem(PROFILE_STORAGE_KEY, current_profile);
            maxbot_load_api();
        }
        refresh_profile_tabs();
    });
}

refresh_profile_tabs(function() {
    maxbot_load_api();
});

// Keyword conversion functions (aligned with util.py logic)
function format_keyword_for_display(keyword_string) {
    // Convert JSON format to user display format
    // Input:  "AA BB","CC","DD"
    // Output: AA BB;CC;DD
    if (!keyword_string || keyword_string.length === 0) {
        return '';
    }

    // Replace "," or ',' with ";" or ';' (convert delimiter)
    keyword_string = keyword_string.replace(/","/g, '";').replace(/','/, "';");

    // Remove all quotes for display
    keyword_string = keyword_string.replace(/["']/g, '');

    return keyword_string;
}

function format_config_keyword_for_json(user_input) {
    // Convert user input to JSON format
    // Input:  AA BB;CC;DD
    // Output: "AA BB","CC","DD"
    if (!user_input || user_input.length === 0) {
        return '';
    }

    // Remove any existing quotes first
    user_input = user_input.replace(/["']/g, '');

    // Use semicolon as the ONLY delimiter (Issue #23)
    if (user_input.includes(';')) {
        const items = user_input.split(';')
            .map(item => item.trim())
            .filter(item => item.length > 0);
        return items.map(item => `"${item}"`).join(',');
    } else {
        return `"${user_input.trim()}"`;
    }
}

// Toggle Cityline login hint visibility based on account input
function updateCitylineHintVisibility() {
    const citylineHint = document.querySelector('#cityline-login-hint');
    if (citylineHint && cityline_account) {
        citylineHint.style.display = cityline_account.value.trim() !== '' ? '' : 'none';
    }
}

// Check if URL is Tixcraft family — delegates to PLATFORM_MAP as single source of truth
function isTixcraftFamily(url) {
    return detectPlatform(url) === 'tixcraft';
}

function isTixcraftSoftBlockScope(url) {
    if (!url) return false;
    return ['tixcraft.com', 'teamear.com', 'indievox.com'].some(domain => url.includes(domain));
}

// Platform detection map
const PLATFORM_MAP = [
    { key: 'tixcraft',    domains: ['tixcraft.com', 'teamear.com', 'indievox.com', 'ticketmaster.'] },
    { key: 'kktix',       domains: ['kktix.com', 'kktix.cc'] },
    { key: 'ibon',        domains: ['ibon.com'] },
    { key: 'famiticket',  domains: ['famiticket.com'] },
    { key: 'kham',        domains: ['kham.com.tw'] },
    { key: 'ticket',      domains: ['ticket.com.tw'] },
    { key: 'udn',         domains: ['udnfunlife.com'] },
    { key: 'ticketplus',  domains: ['ticketplus.com'] },
    { key: 'cityline',    domains: ['cityline.com'] },
    { key: 'hkticketing', domains: ['hkticketing.com', 'galaxymacau.com', 'ticketek.com'] },
    { key: 'funone',      domains: ['funone.io'] },
    { key: 'fansigo',     domains: ['fansi.me'] },
    { key: 'urbtix',      domains: ['urbtix.hk'] },
];

function detectPlatform(url) {
    if (!url) return null;
    for (const platform of PLATFORM_MAP) {
        if (platform.domains.some(d => url.includes(d))) {
            return platform.key;
        }
    }
    return null;
}

let _lastPlatform = undefined;

function updatePlatformFields(url) {
    const platform = detectPlatform(url);
    if (platform === _lastPlatform) {
        updateTixcraftSoftBlockDelayVisibility(url);
        return;
    }
    _lastPlatform = platform;
    const fields = $('[data-under]').addClass('disappear');
    if (platform) {
        fields.filter(`[data-under~="${platform}"]`).removeClass('disappear');
    }
    updateTixcraftSoftBlockDelayVisibility(url);
    updateCitylineHintVisibility();
}

// Soft-block delay is the only field limited to the three TixCraft-proper hosts;
// the custom delay is ignored on Ticketmaster (see _resolve_soft_block_wait_seconds).
// The allow-less-tickets row is NOT handled here -- it applies to the whole
// TixCraft family incl. Ticketmaster and is driven by data-under="tixcraft".
function updateTixcraftSoftBlockDelayVisibility(url) {
    const row = document.getElementById('tixcraft-soft-block-delay-row');
    if (!row) return;

    if (isTixcraftSoftBlockScope(url)) {
        row.classList.remove('disappear');
    } else {
        row.classList.add('disappear');
    }
}

// Toggle Tixcraft refresh rate warning visibility
function updateTixcraftRefreshWarning() {
    const warningElement = document.getElementById('tixcraft-refresh-warning');
    if (!warningElement) return;

    const url = homepage.value;
    const interval = parseFloat(auto_reload_page_interval.value);

    // Show warning if: Tixcraft family site AND refresh interval < 8 seconds
    const shouldShowWarning = isTixcraftFamily(url) && !isNaN(interval) && interval > 0 && interval < 8;

    if (shouldShowWarning) {
        warningElement.style.display = 'block';
        setTimeout(() => {
            warningElement.classList.add('show');
        }, 10);
    } else {
        if (warningElement.classList.contains('show')) {
            warningElement.classList.remove('show');
            setTimeout(() => {
                warningElement.style.display = 'none';
            }, 150);
        }
    }
}

function load_settins_to_form(settings)
{
    if (settings)
    {
        const normalizedLanguage = normalizeLanguage(settings.language);
        settings.language = serializeLanguage(normalizedLanguage);
        if (language_selector) {
            language_selector.value = normalizedLanguage;
        }

        //console.log("ticket_number:"+ settings.ticket_number);
        // preference
        homepage.value = settings.homepage;
        ticket_number.value = settings.ticket_number;
        refresh_datetime.value = settings.refresh_datetime;
        date_select_mode.value = settings.date_auto_select.mode;
        date_keyword.value = format_keyword_for_display(settings.date_auto_select.date_keyword);
        date_auto_fallback.checked = settings.date_auto_fallback || false;

        area_select_mode.value = settings.area_auto_select.mode;
        area_keyword.value = format_keyword_for_display(settings.area_auto_select.area_keyword);
        area_auto_fallback.checked = settings.area_auto_fallback || false;

        keyword_exclude.value = format_keyword_for_display(settings.keyword_exclude);
        
        // advanced

        play_ticket_sound.checked = settings.advanced.play_sound.ticket;
        play_order_sound.checked = settings.advanced.play_sound.order;
        play_sound_filename.value = settings.advanced.play_sound.filename;
        discord_webhook_url.value = settings.advanced.discord_webhook_url || '';
        notification_message.value = settings.advanced.discord_message || settings.advanced.telegram_message || '';
        telegram_bot_token.value = settings.advanced.telegram_bot_token || '';
        telegram_chat_id.value = settings.advanced.telegram_chat_id || '';

        auto_press_next_step_button.checked = settings.kktix.auto_press_next_step_button;
        max_dwell_time.value = settings.kktix.max_dwell_time;

        auto_reload_page_interval.value = settings.advanced.auto_reload_page_interval;
        tixcraft_soft_block_delay.value = settings.advanced.tixcraft_soft_block_delay || '';
        tixcraft_allow_less_tickets.checked = settings.tixcraft?.allow_less_tickets || false;
        reset_browser_interval.value = settings.advanced.reset_browser_interval;
        server_port.value = settings.advanced.server_port || 16888;
        proxy_server_port.value  = settings.advanced.proxy_server_port;
        window_size.value  = settings.advanced.window_size;

        disable_adjacent_seat.checked = settings.advanced.disable_adjacent_seat;

        hide_some_image.checked = settings.advanced.hide_some_image;
        block_facebook_network.checked = settings.advanced.block_facebook_network;
        headless.checked = settings.advanced.headless;
        verbose.checked = settings.advanced.verbose;
        show_timestamp.checked = settings.advanced.show_timestamp;


        ocr_captcha_enable.checked = settings.ocr_captcha.enable;
        ocr_captcha_image_source.value  = settings.ocr_captcha.image_source;
        ocr_captcha_force_submit.checked = settings.ocr_captcha.force_submit;

        if(settings.ocr_captcha.use_universal !== undefined) {
            ocr_captcha_use_universal.checked = settings.ocr_captcha.use_universal;
        } else {
            ocr_captcha_use_universal.checked = true;
        }

        let remote_url_string = "";
        let remote_url_array = [];
        if(settings.advanced.remote_url.length > 0) {
            remote_url_array = JSON.parse('[' +  settings.advanced.remote_url +']');
        }
        if(remote_url_array.length) {
            remote_url_string = remote_url_array[0];
        }
        remote_url.value = remote_url_string;

        // custom OCR model path
        if(settings.ocr_captcha.path) {
            ocr_model_path.value = settings.ocr_captcha.path;
        } else {
            ocr_model_path.value = "";
        }

        // dictionary
        user_guess_string.value = format_keyword_for_display(settings.advanced.user_guess_string);
        auto_guess_options.checked = settings.advanced.auto_guess_options;

        // contact info
        if (settings.contact) {
            real_name.value = settings.contact.real_name || '';
            phone.value = settings.contact.phone || '';
            credit_card_prefix.value = settings.contact.credit_card_prefix || '';
        }

        // auto fill (accounts section)
        tixcraft_sid.value = settings.accounts.tixcraft_sid;
        ibonqware.value = settings.accounts.ibonqware;
        funone_session_cookie.value = settings.accounts.funone_session_cookie || '';
        fansigo_cookie.value = settings.accounts.fansigo_cookie || '';
        fansigo_account.value = settings.accounts.fansigo_account || '';
        fansigo_password.value = settings.accounts.fansigo_password || '';
        facebook_account.value = settings.accounts.facebook_account;
        kktix_account.value = settings.accounts.kktix_account;
        fami_account.value = settings.accounts.fami_account;
        kham_account.value = settings.accounts.kham_account;
        ticket_account.value = settings.accounts.ticket_account;
        udn_account.value = settings.accounts.udn_account;
        ticketplus_account.value = settings.accounts.ticketplus_account;
        cityline_account.value = settings.accounts.cityline_account;
        urbtix_account.value = settings.accounts.urbtix_account;
        hkticketing_account.value = settings.accounts.hkticketing_account;

        facebook_password.value = settings.accounts.facebook_password;
        kktix_password.value = settings.accounts.kktix_password;
        fami_password.value = settings.accounts.fami_password;
        kham_password.value = settings.accounts.kham_password;
        ticket_password.value = settings.accounts.ticket_password;
        udn_password.value = settings.accounts.udn_password;
        ticketplus_password.value = settings.accounts.ticketplus_password;
        discount_code.value = settings.advanced.discount_code || '';
        urbtix_password.value = settings.accounts.urbtix_password;
        hkticketing_password.value = settings.accounts.hkticketing_password;

        // runtime
        idle_keyword.value = settings.advanced.idle_keyword;
        if(idle_keyword.value=='""') {
            idle_keyword.value='';
        }
        resume_keyword.value = settings.advanced.resume_keyword;
        if(resume_keyword.value=='""') {
            resume_keyword.value='';
        }
        idle_keyword_second.value = settings.advanced.idle_keyword_second;
        if(idle_keyword_second.value=='""') {
            idle_keyword_second.value='';
        } else if(idle_keyword_second.value && idle_keyword_second.value.includes('","')) {
            // 新增：簡化顯示格式 "00","30","50" → 00,30,50
            idle_keyword_second.value = idle_keyword_second.value.replace(/"/g, '');
        }
        resume_keyword_second.value = settings.advanced.resume_keyword_second;
        if(resume_keyword_second.value=='""') {
            resume_keyword_second.value='';
        } else if(resume_keyword_second.value && resume_keyword_second.value.includes('","')) {
            // 新增：簡化顯示格式
            resume_keyword_second.value = resume_keyword_second.value.replace(/"/g, '');
        }

        // Update platform-aware fields, Cityline hint, and Tixcraft warning after loading settings
        _lastPlatform = undefined;
        updatePlatformFields(homepage.value);
        updateTixcraftRefreshWarning();
        applyLanguage(normalizedLanguage);
    } else {
        console.log('no settings found');
    }
}

function maxbot_load_api()
{
    let api_url = "/load" + profile_query();
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        //console.log(data);
        settings = data;
        load_settins_to_form(data);
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

function maxbot_reset_api()
{
    if (current_profile !== 'default') {
        message('重設僅支援 default 設定檔；其他設定檔請直接刪除後重建。');
        return;
    }
    let api_url = "/reset";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        //console.log(data);
        settings = data;
        load_settins_to_form(data);
        check_unsaved_fields();
        run_message(uiText('reset_done'));
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

let messageClearTimer;

function message(msg)
{
    $("#message_detail").text(msg);
    $("#message_modal").modal("show");
}

function message_old(msg)
{
    clearTimeout(messageClearTimer);
    const message = document.querySelector('#message');
    message.innerText = msg;
    messageClearTimer = setTimeout(function ()
        {
            message.innerText = '';
        }, 3000);
}

function next_instance_id(base, rows)
{
    // Lowest free numbered id for a duplicate launch: base-2, base-3, ...
    const existing = new Set((rows || []).map(function(it){ return it.id; }));
    let n = 2;
    while (existing.has(base + '-' + n)) n++;
    return base + '-' + n;
}

function maxbot_launch()
{
    // Warn when this profile already has a live instance (same-account session
    // kick risk). If confirmed, launch a second instance under a numbered id.
    $.get('/instances').done(function(data) {
        const rows = (data && data.instances) ? data.instances : [];
        const alive = rows.some(function(it){ return it.id === current_profile && it.alive; });
        if (alive) {
            if (!window.confirm(uiText('dup_run_confirm'))) return;
            do_launch(next_instance_id(current_profile, rows));
        } else {
            do_launch('');
        }
    }).fail(function() {
        // /instances unavailable (older backend): fall back to a plain launch.
        do_launch('');
    });
}

function do_launch(instance_override)
{
    run_message(uiText('launching'));
    if (!save_changes_to_dict(true)) return;
    maxbot_save_api(function(){ maxbot_run_api(instance_override); });
}

function maxbot_run_api(instance_override)
{
    let api_url = "/run" + profile_query();
    if (instance_override) {
        api_url += (profile_query() ? '&' : '?') + 'instance=' + encodeURIComponent(instance_override);
    }
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        run_message(uiText('launch_sent'));
        console.log("[MaxBot] Launch API response:", data);
    })
    .fail(function(xhr, status, error) {
        run_message(uiText('launch_failed', status));
        console.error("[MaxBot] Launch API error:", status, error);
        console.error("[MaxBot] Response content:", xhr.responseText);
    })
    .always(function() {
        //alert( "finished" );
    });
}

function maxbot_shutdown_api()
{
    let api_url = "/shutdown";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        window.close();
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

function save_changes_to_dict(silent_flag)
{
    const ticket_number_value = parseInt(ticket_number.value);
    const tixcraft_soft_block_delay_value = (tixcraft_soft_block_delay?.value || '').trim();
    //console.log(ticket_number_value);
    if (!ticket_number_value)
    {
        message(uiText('missing_ticket_number'));
        return false;
    } else {
        if (tixcraft_soft_block_delay) {
            tixcraft_soft_block_delay.classList.remove('is-invalid');
        }

        if (tixcraft_soft_block_delay_value) {
            const parsed_delay = Number(tixcraft_soft_block_delay_value);
            const is_integer = Number.isInteger(parsed_delay);
            if (!is_integer || parsed_delay < 1 || parsed_delay > 600) {
                tixcraft_soft_block_delay.classList.add('is-invalid');
                message(uiText('invalid_tixcraft_soft_block_delay'));
                return false;
            }
        }

        if(settings) {

            // preference
            settings.language = serializeLanguage(currentLanguage);
            settings.homepage = homepage.value;
            settings.ticket_number = ticket_number_value;
            settings.refresh_datetime = refresh_datetime.value;
            settings.date_auto_select.mode = date_select_mode.value;
            settings.date_auto_select.date_keyword = format_config_keyword_for_json(date_keyword.value);
            settings.date_auto_fallback = date_auto_fallback.checked;

            settings.area_auto_select.mode = area_select_mode.value;
            settings.area_auto_select.area_keyword = format_config_keyword_for_json(area_keyword.value);
            settings.area_auto_fallback = area_auto_fallback.checked;

            settings.keyword_exclude = format_config_keyword_for_json(keyword_exclude.value);

            // advanced
            settings.advanced.play_sound.ticket = play_ticket_sound.checked;
            settings.advanced.play_sound.order = play_order_sound.checked;
            settings.advanced.play_sound.filename = play_sound_filename.value;
            settings.advanced.discord_webhook_url = discord_webhook_url.value;
            settings.advanced.discord_message = notification_message.value;
            settings.advanced.telegram_bot_token = telegram_bot_token.value;
            settings.advanced.telegram_chat_id = telegram_chat_id.value;
            settings.advanced.telegram_message = notification_message.value;

            settings.kktix.auto_press_next_step_button = auto_press_next_step_button.checked;
            settings.kktix.max_dwell_time = parseInt(max_dwell_time.value);
            if (!settings.tixcraft) settings.tixcraft = {};

            settings.advanced.auto_reload_page_interval = Number(auto_reload_page_interval.value);
            settings.advanced.tixcraft_soft_block_delay = tixcraft_soft_block_delay_value;
            settings.tixcraft.allow_less_tickets = tixcraft_allow_less_tickets.checked;
            settings.advanced.reset_browser_interval = parseInt(reset_browser_interval.value);
            settings.advanced.server_port = parseInt(server_port.value) || 16888;
            settings.advanced.proxy_server_port = proxy_server_port.value;
            settings.advanced.window_size = window_size.value;

            settings.advanced.disable_adjacent_seat = disable_adjacent_seat.checked;

            settings.advanced.hide_some_image = hide_some_image.checked;
            settings.advanced.block_facebook_network = block_facebook_network.checked;
            settings.advanced.headless = headless.checked;
            settings.advanced.verbose = verbose.checked;
            settings.advanced.show_timestamp = show_timestamp.checked;


            settings.ocr_captcha.enable = ocr_captcha_enable.checked;
            settings.ocr_captcha.image_source = ocr_captcha_image_source.value;
            settings.ocr_captcha.force_submit = ocr_captcha_force_submit.checked;
            settings.ocr_captcha.use_universal = ocr_captcha_use_universal.checked;

            let remote_url_array = [];
            remote_url_array.push(remote_url.value);
            let remote_url_string = JSON.stringify(remote_url_array);
            remote_url_string = remote_url_string.substring(0,remote_url_string.length-1);
            remote_url_string = remote_url_string.substring(1);
            //console.log("final remote_url_string:"+remote_url_string);
            settings.advanced.remote_url = remote_url_string;

            // custom OCR model path (migrated from advanced.ocr_model_path)
            settings.ocr_captcha.path = ocr_model_path.value;
            // Remove deprecated field if exists
            if (settings.advanced && settings.advanced.ocr_model_path !== undefined) {
                delete settings.advanced.ocr_model_path;
            }

            // dictionary
            settings.advanced.user_guess_string = format_config_keyword_for_json(user_guess_string.value);

            settings.advanced.auto_guess_options = auto_guess_options.checked;

            // contact info
            if (!settings.contact) settings.contact = {};
            settings.contact.real_name = real_name.value;
            settings.contact.phone = phone.value;
            settings.contact.credit_card_prefix = credit_card_prefix.value;

            // auto fill (accounts section)
            settings.accounts.tixcraft_sid = tixcraft_sid.value;
            settings.accounts.ibonqware = ibonqware.value;
            settings.accounts.funone_session_cookie = funone_session_cookie.value;
            settings.accounts.fansigo_cookie = fansigo_cookie.value;
            settings.accounts.fansigo_account = fansigo_account.value;
            settings.accounts.fansigo_password = fansigo_password.value;
            settings.accounts.facebook_account = facebook_account.value;
            settings.accounts.kktix_account = kktix_account.value;
            settings.accounts.fami_account = fami_account.value;
            settings.accounts.kham_account = kham_account.value;
            settings.accounts.ticket_account = ticket_account.value;
            settings.accounts.udn_account = udn_account.value;
            settings.accounts.ticketplus_account = ticketplus_account.value;
            settings.accounts.cityline_account = cityline_account.value;
            settings.accounts.urbtix_account = urbtix_account.value;
            settings.accounts.hkticketing_account = hkticketing_account.value;

            settings.accounts.facebook_password = facebook_password.value;
            settings.accounts.kktix_password = kktix_password.value;
            settings.accounts.fami_password = fami_password.value;
            settings.accounts.kham_password = kham_password.value;
            settings.accounts.ticket_password = ticket_password.value;
            settings.accounts.udn_password = udn_password.value;
            settings.accounts.ticketplus_password = ticketplus_password.value;
            settings.advanced.discount_code = discount_code.value;
            settings.accounts.urbtix_password = urbtix_password.value;
            settings.accounts.hkticketing_password = hkticketing_password.value;

            // runtime
            settings.advanced.idle_keyword = idle_keyword.value;
            settings.advanced.resume_keyword = resume_keyword.value;
            settings.advanced.idle_keyword_second = idle_keyword_second.value;
            settings.advanced.resume_keyword_second = resume_keyword_second.value;


        }
        if(!silent_flag) {
            message(uiText('saved'));
        }
        return true;
    }
    return false;
}

function maxbot_save_api(callback)
{
    let api_url = "/save" + profile_query();
    if(settings) {
        $.post( api_url, JSON.stringify(settings), function() {
            //alert( "success" );
        })
        .done(function(data) {
            console.log("[MaxBot] 設定儲存成功");
            check_unsaved_fields();
            if(callback) callback();
        })
        .fail(function(xhr, status, error) {
            console.error("[MaxBot] Save API error:", status, error);
            console.error("[MaxBot] Response content:", xhr.responseText);
            run_message(uiText('save_failed', status));
        })
        .always(function() {
            //alert( "finished" );
        });
    }
}

function maxbot_pause_api()
{
    let api_url = "/pause" + profile_query();
    if(settings) {
        $.get( api_url, function() {
            //alert( "success" );
        })
        .done(function(data) {
            //alert( "second success" );
        })
        .fail(function() {
            //alert( "error" );
        })
        .always(function() {
            //alert( "finished" );
        });
    }
}

function maxbot_resume_api()
{
    let api_url = "/resume" + profile_query();
    if(settings) {
        $.get( api_url, function() {
            //alert( "success" );
        })
        .done(function(data) {
            //alert( "second success" );
        })
        .fail(function() {
            //alert( "error" );
        })
        .always(function() {
            //alert( "finished" );
        });
    }
}
function maxbot_save()
{
    run_message(uiText('saving'));
    if (!save_changes_to_dict(true)) return;
    maxbot_save_api(function() {
        run_message(uiText('saved'));
    });
}

function check_unsaved_fields()
{
    if(settings) {
        if (language_selector) {
            const currentStoredLanguage = normalizeLanguage(settings.language);
            if (currentLanguage !== currentStoredLanguage) {
                language_selector.classList.add('is-invalid');
            } else {
                language_selector.classList.remove('is-invalid');
            }
        }
        const field_list_basic = ["homepage","ticket_number","refresh_datetime"];
        field_list_basic.forEach(f => {
            const field = document.querySelector('#'+f);
            if(field.value != settings[f]) {
                $("#"+f).addClass("is-invalid");
            } else {
                $("#"+f).removeClass("is-invalid");
            }
        });
        const field_list_accounts = [
            "tixcraft_sid",
            "ibonqware",
            "funone_session_cookie",
            "fansigo_cookie",
            "fansigo_account",
            "fansigo_password",
            "facebook_account",
            "kktix_account",
            "fami_account",
            "cityline_account",
            "urbtix_account",
            "hkticketing_account",
            "kham_account",
            "ticket_account",
            "udn_account",
            "ticketplus_account",
            "facebook_password",
            "kktix_password",
            "fami_password",
            "urbtix_password",
            "hkticketing_password",
            "kham_password",
            "ticket_password",
            "udn_password",
            "ticketplus_password"
        ];
        field_list_accounts.forEach(f => {
            const field = document.querySelector('#'+f);
            let formated_input = field.value;
            let formated_saved_value = settings["accounts"][f];
            if(typeof formated_saved_value == "string") {
                if(formated_input=='')
                    formated_input='""';
                if(formated_saved_value=='')
                    formated_saved_value='""';
                if(formated_saved_value.indexOf('"') > -1) {
                    if(formated_input.length) {
                        if(formated_input != '""') {
                            formated_input = '"' + formated_input + '"';
                        }
                    }
                }
            }
            let is_not_match = (formated_input != formated_saved_value);
            if(is_not_match) {
                $("#"+f).addClass("is-invalid");
            } else {
                $("#"+f).removeClass("is-invalid");
            }
        });
        const field_list_advance = [
            "user_guess_string",
            "remote_url",
            "auto_reload_page_interval",
            "tixcraft_soft_block_delay",
            "reset_browser_interval",
            "proxy_server_port",
            "window_size",
            "idle_keyword",
            "resume_keyword",
            "idle_keyword_second",
            "resume_keyword_second",
            "discount_code"
        ];
        field_list_advance.forEach(f => {
            const field = document.querySelector('#'+f);
            let formated_input = field.value;
            let formated_saved_value = settings["advanced"][f];
            //console.log(f);
            //console.log(field.value);
            //console.log(formated_saved_value);
            if(typeof formated_saved_value == "string") {
                if(formated_input=='')
                    formated_input='""';
                if(formated_saved_value=='')
                    formated_saved_value='""';
                if(formated_saved_value.indexOf('"') > -1) {
                    if(formated_input.length) {
                        if(formated_input != '""') {
                            formated_input = '"' + formated_input + '"';
                        }
                    }
                }
            }
            let is_not_match = (formated_input != formated_saved_value);
            if(is_not_match) {
                //console.log(f);
                //console.log(formated_input);
                //console.log(formated_saved_value);
                $("#"+f).addClass("is-invalid");
            } else {
                $("#"+f).removeClass("is-invalid");
            }
        });

        if (tixcraft_allow_less_tickets) {
            const currentValue = tixcraft_allow_less_tickets.checked;
            const savedValue = settings.tixcraft?.allow_less_tickets || false;
            if (currentValue !== savedValue) {
                tixcraft_allow_less_tickets.classList.add('is-invalid');
            } else {
                tixcraft_allow_less_tickets.classList.remove('is-invalid');
            }
        }

    }
}

function maxbot_status_api()
{
    // Status / pause / resume all follow the currently selected profile tab
    let api_url = "/status" + profile_query();
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        //alert( "second success" );
        let status_text = uiText('status_paused');
        let status_class = "badge text-bg-danger";
        if(data.status) {
            status_text=uiText('status_running');
            status_class = "badge text-bg-success";
            $("#pause_btn").removeClass("disappear");
            $("#resume_btn").addClass("disappear");
        } else {
            $("#pause_btn").addClass("disappear");
            $("#resume_btn").removeClass("disappear");
        }
        $("#last_url").text(data.last_url);
        $("#maxbot_status").html(status_text).prop( "class", status_class);
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

function maxbot_version_api()
{
    let api_url = "/version";
    $.get( api_url, function() {
        //alert( "success" );
    })
    .done(function(data) {
        $("#maxbot_version").html(data.version);
    })
    .fail(function() {
        //alert( "error" );
    })
    .always(function() {
        //alert( "finished" );
    });
}

function update_system_time()
{
    var currentdate = new Date(); 
    var datetime = ("0" + currentdate.getHours()).slice(-2) + ":"  
                + ("0" + currentdate.getMinutes()).slice(-2) + ":" 
                + ("0" + currentdate.getSeconds()).slice(-2);
    $("#system_time").html(datetime);
}

var status_interval= setInterval(() => {
    maxbot_status_api();
    update_system_time();
}, 500);

// ===== Instance dashboard (Phase 3 multi-instance overview) =====
// Polls /instances and renders one row per instance (every profile plus any
// CLI --instance run). Per-row pause/resume and "pause all" reuse the
// existing /pause /resume endpoints with ?profile=<id>.
function instance_query(id) {
    return (id && id !== 'default') ? '?profile=' + encodeURIComponent(id) : '';
}

function render_instances(rows) {
    const tbody = $('#instances_tbody');
    tbody.empty();
    rows.forEach(function(it) {
        const tr = $('<tr></tr>');
        tr.append($('<td></td>').text(it.id));
        const live_badge = it.alive
            ? $('<span class="badge text-bg-success"></span>').text(uiText('instance_alive'))
            : $('<span class="badge text-bg-secondary"></span>').text(uiText('instance_offline'));
        tr.append($('<td></td>').append(live_badge));
        const state_badge = it.paused
            ? $('<span class="badge text-bg-danger"></span>').text(uiText('instance_paused'))
            : $('<span class="badge text-bg-success"></span>').text(uiText('instance_running'));
        tr.append($('<td></td>').append(state_badge));
        const url = it.last_url || '';
        tr.append($('<td class="text-truncate" style="max-width:240px;"></td>').text(url).attr('title', url));
        const action_td = $('<td class="text-end"></td>');
        const action_btn = it.paused
            ? $('<button type="button" class="btn btn-sm btn-outline-success"></button>').text(uiText('btn_resume')).on('click', function(){ instance_resume(it.id); })
            : $('<button type="button" class="btn btn-sm btn-outline-danger"></button>').text(uiText('btn_pause')).on('click', function(){ instance_pause(it.id); });
        action_td.append(action_btn);
        // Stop is only meaningful for a live process; offline rows have nothing to stop.
        if (it.alive) {
            const stop_btn = $('<button type="button" class="btn btn-sm btn-outline-secondary ms-1"></button>').text(uiText('btn_stop')).on('click', function(){ instance_stop(it.id); });
            action_td.append(stop_btn);
        }
        tr.append(action_td);
        tbody.append(tr);
    });
}

function instances_dashboard_api() {
    $.get('/instances').done(function(data) {
        const rows = (data && data.instances) ? data.instances : [];
        render_instances(rows);
        refresh_question_instance_options(rows);
    }).fail(function() {
        // Older backend without /instances: hide the panel, keep single-instance UI.
        $('#instances_panel').addClass('d-none');
    });
}

function instance_pause(id) {
    $.get('/pause' + instance_query(id)).always(instances_dashboard_api);
}

function instance_resume(id) {
    $.get('/resume' + instance_query(id)).always(instances_dashboard_api);
}

function instance_stop(id) {
    // Irreversible (closes the browser, ends the process) -> require confirmation.
    if (!window.confirm(uiText('stop_confirm', id))) return;
    $.get('/stop' + instance_query(id)).always(instances_dashboard_api);
}

function pause_all_instances() {
    // Mirror the planned semantics: build a pause flag for every alive,
    // non-paused instance individually (no global pause file).
    $.get('/instances').done(function(data) {
        const rows = (data && data.instances) ? data.instances : [];
        rows.filter(function(it){ return it.alive && !it.paused; })
            .forEach(function(it){ $.get('/pause' + instance_query(it.id)); });
        setTimeout(instances_dashboard_api, 300);
    });
}

var instances_interval = setInterval(instances_dashboard_api, 2000);
instances_dashboard_api();

maxbot_version_api();

run_button.addEventListener('click', maxbot_launch);
save_button.addEventListener('click', maxbot_save);
reset_button.addEventListener('click', maxbot_reset_api);
exit_button.addEventListener('click', maxbot_shutdown_api);
pause_button.addEventListener('click', maxbot_pause_api);
resume_button.addEventListener('click', maxbot_resume_api);

const onchange_tag_list = ["input","select","textarea"];
onchange_tag_list.forEach((tag) => {
    const input_items = document.querySelectorAll(tag);
    input_items.forEach((userItem) => {
        userItem.addEventListener('change', check_unsaved_fields);
    });
});

homepage.addEventListener('keyup', check_unsaved_fields);
homepage.addEventListener('input', () => updatePlatformFields(homepage.value));

ocr_captcha_use_universal.addEventListener('change', function() {
    if (this.checked) {
        ocr_model_path.value = 'assets/model/universal';
    } else {
        ocr_model_path.value = '';
    }
});

document.querySelector('#btn_test_discord_webhook').addEventListener('click', function() {
    const url = discord_webhook_url.value.trim();
    if (!url) {
        alert(uiText('discord_empty'));
        return;
    }
    const btn = this;
    btn.disabled = true;
    btn.textContent = '...';
    $.ajax({
        url: '/test_discord_webhook',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ webhook_url: url, custom_message: notification_message.value }),
        dataType: 'json'
    })
    .done(function(data) {
        if (data.success) {
            btn.className = 'btn btn-outline-success';
            btn.textContent = 'OK';
        } else {
            btn.className = 'btn btn-outline-danger';
            btn.textContent = 'Failed';
            alert(uiText('test_failed', data.message));
        }
    })
    .fail(function() {
        btn.className = 'btn btn-outline-danger';
        btn.textContent = 'Error';
    })
    .always(function() {
        setTimeout(function() {
            btn.disabled = false;
            btn.textContent = currentLanguage === 'en' ? 'Test' : '\u6E2C\u8A66';
            btn.className = 'btn btn-outline-secondary';
        }, 3000);
    });
});

document.querySelector('#btn_test_telegram').addEventListener('click', function() {
    const token = telegram_bot_token.value.trim();
    const chatId = telegram_chat_id.value.trim();
    if (!token || !chatId) {
        alert(uiText('telegram_empty'));
        return;
    }
    const btn = this;
    btn.disabled = true;
    btn.textContent = '...';
    $.ajax({
        url: '/test_telegram',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ bot_token: token, chat_id: chatId, custom_message: notification_message.value }),
        dataType: 'json'
    })
    .done(function(data) {
        if (data.success) {
            btn.className = 'btn btn-outline-success';
            btn.textContent = 'OK';
        } else {
            btn.className = 'btn btn-outline-danger';
            btn.textContent = 'Failed';
            alert(uiText('test_failed', data.message));
        }
    })
    .fail(function() {
        btn.className = 'btn btn-outline-danger';
        btn.textContent = 'Error';
    })
    .always(function() {
        setTimeout(function() {
            btn.disabled = false;
            btn.textContent = currentLanguage === 'en' ? 'Test' : '\u6E2C\u8A66';
            btn.className = 'btn btn-outline-secondary';
        }, 3000);
    });
});

let runMessageClearTimer;

function run_message(msg)
{
    clearTimeout(runMessageClearTimer);
    const message = document.querySelector('#run_btn_pressed_message');
    message.innerText = msg;
    runMessageClearTimer = setTimeout(function ()
        {
            message.innerText = '';
        }, 3000);
}

function home_tab_clicked() {
    document.getElementById("homepage").focus();
}

// Dark Mode Functions
function initTheme() {
    // Check if user has a saved preference
    const savedTheme = localStorage.getItem('theme');

    // If no saved preference, check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');

    // Apply theme
    applyTheme(theme);

    // Update toggle state
    dark_mode_toggle.checked = (theme === 'dark');
    updateThemeStatus(theme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
}

function updateThemeStatus(theme) {
    // Update status badge if it exists (optional display element)
    if (theme_status) {
        if (theme === 'dark') {
            theme_status.textContent = currentLanguage === 'en' ? 'On' : '已啟用';
            theme_status.className = 'badge bg-success ms-2';
        } else {
            theme_status.textContent = currentLanguage === 'en' ? 'Off' : '已關閉';
            theme_status.className = 'badge bg-secondary ms-2';
        }
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    applyTheme(newTheme);
    updateThemeStatus(newTheme);
}

// Initialize theme on page load
initTheme();

// Add event listener for theme toggle
dark_mode_toggle.addEventListener('change', toggleTheme);
language_selector?.addEventListener('change', function() {
    applyLanguage(this.value);
    check_unsaved_fields();
});

// ========================================
// Question Detection Feature
// ========================================

let questionCheckInterval = null;
let lastDetectedQuestion = '';
// '' = follow the active profile tab; otherwise monitor this specific instance.
let question_target_instance = '';

function on_question_instance_change() {
    const sel = document.getElementById('question-instance-select');
    question_target_instance = sel ? sel.value : '';
    lastDetectedQuestion = '';  // force re-render for the newly chosen target
    checkDetectedQuestion();
}

// Populate the answer-panel instance picker from the /instances poll, keeping
// the current selection stable across refreshes.
function refresh_question_instance_options(rows) {
    const sel = document.getElementById('question-instance-select');
    if (!sel) return;
    const prev = sel.value;
    sel.innerHTML = '';
    const opt_default = document.createElement('option');
    opt_default.value = '';
    opt_default.textContent = uiText('question_target_active');
    sel.appendChild(opt_default);
    (rows || []).forEach(function(it) {
        const opt = document.createElement('option');
        opt.value = it.id;
        opt.textContent = it.id + (it.alive ? '' : ' (' + uiText('instance_offline') + ')');
        sel.appendChild(opt);
    });
    const ids = (rows || []).map(function(it){ return it.id; });
    if (prev && ids.indexOf(prev) >= 0) {
        sel.value = prev;
    } else if (prev) {
        // Selected instance vanished -> fall back to the active tab.
        sel.value = '';
        question_target_instance = '';
    }
}

/**
 * Check if MAXBOT_QUESTION.txt exists and display the question
 */
async function checkDetectedQuestion() {
    try {
        const target_query = question_target_instance ? instance_query(question_target_instance) : profile_query();
        const response = await fetch('/question' + target_query);
        const data = await response.json();

        const alertElement = document.getElementById('detected-question-alert');
        const questionTextElement = document.getElementById('detected-question-text');

        if (data.exists && data.question) {
            // Only update if question content changed
            if (data.question !== lastDetectedQuestion) {
                lastDetectedQuestion = data.question;

                // Update question text
                questionTextElement.textContent = data.question;

                // Show alert with fade-in effect
                alertElement.style.display = 'block';
                setTimeout(() => {
                    alertElement.classList.add('show');
                }, 10);

                // Auto-scroll to the alert if verification tab is active
                const verificationTab = document.getElementById('verification-tab');
                if (verificationTab.classList.contains('active')) {
                    alertElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }

                console.log('[QUESTION DETECTED]', data.question);
            }
        } else {
            // Hide alert if no question or file doesn't exist
            if (alertElement.classList.contains('show')) {
                alertElement.classList.remove('show');
                setTimeout(() => {
                    alertElement.style.display = 'none';
                }, 150);
                lastDetectedQuestion = '';
            }
        }
    } catch (error) {
        console.error('[QUESTION CHECK] Error:', error);
    }
}

/**
 * Start polling for question detection
 */
function startQuestionPolling() {
    // Check immediately
    checkDetectedQuestion();

    // Then check every 0.5 seconds
    if (!questionCheckInterval) {
        questionCheckInterval = setInterval(checkDetectedQuestion, 500);
        console.log('[QUESTION POLLING] Started (every 0.5 seconds)');
    }
}

/**
 * Stop polling
 */
function stopQuestionPolling() {
    if (questionCheckInterval) {
        clearInterval(questionCheckInterval);
        questionCheckInterval = null;
        console.log('[QUESTION POLLING] Stopped');
    }
}

// Start polling when page loads
startQuestionPolling();

// Cityline login hint visibility control
if (cityline_account) {
    cityline_account.addEventListener('input', updateCitylineHintVisibility);
}

// Tixcraft refresh warning visibility control
if (homepage) {
    homepage.addEventListener('input', updateTixcraftRefreshWarning);
    homepage.addEventListener('change', updateTixcraftRefreshWarning);
}
if (auto_reload_page_interval) {
    auto_reload_page_interval.addEventListener('input', updateTixcraftRefreshWarning);
    auto_reload_page_interval.addEventListener('change', updateTixcraftRefreshWarning);
}

// Also check when verification tab is clicked
const verificationTab = document.getElementById('verification-tab');
if (verificationTab) {
    verificationTab.addEventListener('click', () => {
        // Force check immediately when tab is clicked
        checkDetectedQuestion();
    });
}

// Search button handlers
async function searchQuestion(engine, event) {
    const questionText = document.getElementById('detected-question-text').textContent.trim();
    if (!questionText) {
        console.warn('[SEARCH] No question text available');
        return;
    }

    // AI prompt for direct answers
    const aiPrompt = "Answer this question directly in the same language as the question, provide only the answer without explanation:\n\n";

    // Determine if this is an AI service (needs prompt) or search engine (no prompt)
    const isAI = ['perplexity', 'chatgpt', 'grok', 'claude'].includes(engine);
    const fullQuestion = isAI ? aiPrompt + questionText : questionText;
    const encodedQuestion = encodeURIComponent(fullQuestion);

    let searchUrl = '';
    let needsCopy = false;

    switch (engine) {
        case 'google':
            searchUrl = `https://www.google.com/search?q=${encodeURIComponent(questionText)}`;
            break;
        case 'bing':
            searchUrl = `https://www.bing.com/search?q=${encodeURIComponent(questionText)}`;
            break;
        case 'perplexity':
            searchUrl = `https://www.perplexity.ai/?q=${encodedQuestion}`;
            break;
        case 'chatgpt':
            searchUrl = `https://chatgpt.com?q=${encodedQuestion}`;
            break;
        case 'claude':
            searchUrl = 'https://claude.ai/new';
            needsCopy = true;
            break;
        case 'grok':
            searchUrl = `https://grok.com?q=${encodedQuestion}`;
            break;
        default:
            console.error('[SEARCH] Unknown search engine:', engine);
            return;
    }

    // Check if Ctrl/Cmd/Middle-click (should open in background)
    const openInBackground = event && (event.ctrlKey || event.metaKey || event.button === 1);

    // For AI services, copy question to clipboard
    if (needsCopy) {
        try {
            await navigator.clipboard.writeText(fullQuestion);
            console.log(`[SEARCH] Question copied to clipboard for ${engine}`);

            // Only show notification if not opening in background
            if (!openInBackground) {
                const alertElement = document.getElementById('detected-question-alert');
                const originalText = alertElement.querySelector('h5').innerHTML;
                alertElement.querySelector('h5').innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-check-circle-fill me-2" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg>${uiText('copied_notice', engine.toUpperCase())}`;

                // Restore original text after 2 seconds
                setTimeout(() => {
                    alertElement.querySelector('h5').innerHTML = originalText;
                }, 2000);
            }
        } catch (err) {
            console.error('[SEARCH] Failed to copy to clipboard:', err);
            if (!openInBackground) {
                alert(uiText('copy_failed', fullQuestion));
            }
        }
    }

    console.log(`[SEARCH] Opening ${engine}:`, searchUrl, openInBackground ? '(background)' : '(foreground)');

    // Open the URL
    // Note: window.open() behavior with Ctrl/Cmd is browser-dependent
    // Most modern browsers will open in background automatically when Ctrl/Cmd is pressed
    window.open(searchUrl, '_blank', 'noopener,noreferrer');
}

// Attach search button event listeners (pass event object)
document.getElementById('search-google-btn')?.addEventListener('click', (e) => searchQuestion('google', e));
document.getElementById('search-bing-btn')?.addEventListener('click', (e) => searchQuestion('bing', e));
document.getElementById('search-perplexity-btn')?.addEventListener('click', (e) => searchQuestion('perplexity', e));
document.getElementById('search-chatgpt-btn')?.addEventListener('click', (e) => searchQuestion('chatgpt', e));
document.getElementById('search-claude-btn')?.addEventListener('click', (e) => searchQuestion('claude', e));
document.getElementById('search-grok-btn')?.addEventListener('click', (e) => searchQuestion('grok', e));

// Also handle middle-click (button 1) for all search buttons
const searchButtons = [
    'search-google-btn', 'search-bing-btn', 'search-perplexity-btn',
    'search-chatgpt-btn', 'search-claude-btn', 'search-grok-btn'
];
searchButtons.forEach(btnId => {
    const btn = document.getElementById(btnId);
    const engine = btnId.replace('search-', '').replace('-btn', '');
    btn?.addEventListener('mousedown', (e) => {
        if (e.button === 1) { // Middle mouse button
            e.preventDefault();
            searchQuestion(engine, e);
        }
    });
});

// TixCraft SID validation
if (tixcraft_sid) {
    tixcraft_sid.addEventListener('input', () => {
        const warningElement = document.getElementById('tixcraft-sid-warning');
        const value = tixcraft_sid.value.trim();

        if (value.startsWith('g.')) {
            // Show warning with fade-in effect
            warningElement.style.display = 'block';
            setTimeout(() => {
                warningElement.classList.add('show');
            }, 10);
        } else {
            // Hide warning with fade-out effect
            if (warningElement.classList.contains('show')) {
                warningElement.classList.remove('show');
                setTimeout(() => {
                    warningElement.style.display = 'none';
                }, 150);
            }
        }
    });
}

// Help Panel — SVG icon injected from static constant (no user data)
renderHelpIcons();

function getHelpOffcanvas() {
    if (!helpOffcanvasInstance) {
        const el = document.getElementById('helpPanel');
        if (!el) return null;
        helpOffcanvasInstance = new bootstrap.Offcanvas(el);
        el.addEventListener('hide.bs.offcanvas', () => {
            currentHelpField = null;
        });
    }
    return helpOffcanvasInstance;
}

function buildHelpBody(content) {
    let html = '';
    if (content.short) {
        html += '<p class="text-secondary-emphasis mb-3">' + content.short + '</p>';
    }
    html += '<div class="mb-3">' + content.detail + '</div>';
    if (content.faq && content.faq.length > 0) {
        html += '<div class="accordion accordion-flush" id="helpFaqAccordion">';
        content.faq.forEach(function(item, i) {
            html += '<div class="accordion-item">'
                + '<h2 class="accordion-header">'
                + '<button class="accordion-button collapsed py-2" type="button"'
                + ' data-bs-toggle="collapse" data-bs-target="#helpFaq' + i + '"'
                + ' aria-expanded="false">' + item.q + '</button>'
                + '</h2>'
                + '<div id="helpFaq' + i + '" class="accordion-collapse collapse"'
                + ' data-bs-parent="#helpFaqAccordion">'
                + '<div class="accordion-body py-2">' + item.a + '</div>'
                + '</div></div>';
        });
        html += '</div>';
    }
    return html;
}

function showHelp(fieldId) {
    var content = getHelpContent(fieldId);
    if (!content) return;
    if (currentHelpField === fieldId) return;

    var oc = getHelpOffcanvas();
    if (!oc) return;

    currentHelpField = fieldId;
    document.getElementById('helpPanelTitle').textContent = content.title;
    // Safe: buildHelpBody returns static developer-authored HTML from help-content.js, no user input
    document.getElementById('helpPanelBody').innerHTML = buildHelpBody(content);

    var footer = document.getElementById('helpPanelFooter');
    var link = document.getElementById('helpPanelLink');
    if (content.link) {
        link.href = content.link;
        footer.style.display = '';
    } else {
        footer.style.display = 'none';
    }

    oc.show();
}

document.addEventListener('click', function(e) {
    var icon = e.target.closest('.help-icon');
    if (icon) {
        e.preventDefault();
        e.stopPropagation();
        showHelp(icon.dataset.help);
    }
});

document.addEventListener('keydown', function(e) {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.classList.contains('help-icon')) {
        e.preventDefault();
        showHelp(e.target.dataset.help);
    }
});

// Clean up when page unloads
window.addEventListener('beforeunload', () => {
    stopQuestionPolling();
});
