/* help-content.js - Contextual help content for settings UI fields
 * All HTML in detail fields is static developer-authored content.
 * No user input or settings.json data is included here.
 */
const HELP_CONTENT = {
  homepage: {
    title: '售票網站',
    short: '填入活動頁面的網址，支援多個售票平台',
    detail: `
      <p><strong>必填欄位。</strong>填入您要搶購票券的活動頁面網址。</p>
      <p>各平台網址格式範例：</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>平台</th><th>網址範例</th></tr></thead>
        <tbody>
          <tr><td>TixCraft</td><td><code>https://tixcraft.com/activity/detail/...</code></td></tr>
          <tr><td>KKTIX</td><td><code>https://kktix.com/events/...</code></td></tr>
          <tr><td>TicketPlus</td><td><code>https://ticketplus.com.tw/activity/...</code></td></tr>
          <tr><td>iBon</td><td><code>https://tickets.ibon.com.tw/event/...</code></td></tr>
          <tr><td>FamiTicket</td><td><code>https://ticket.Family.com.tw/...</code></td></tr>
        </tbody>
      </table>
      <p class="mb-0 text-muted small">提示：直接從瀏覽器網址列複製活動頁面 URL 貼入即可。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#售票網站homepage'
  },

  date_keyword: {
    title: '日期關鍵字',
    short: '指定要選擇的日期，用分號(;)分隔多組',
    detail: `
      <p>設定想選取的場次日期，系統會依序比對並選擇第一個匹配的選項。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>格式</th><th>範例</th><th>說明</th></tr></thead>
        <tbody>
          <tr><td>單一關鍵字</td><td><code>9/11</code></td><td>包含「9/11」即匹配</td></tr>
          <tr><td>分號 = OR</td><td><code>9/11;9/22;3/3</code></td><td>依序嘗試，第一個匹配就選取</td></tr>
          <tr><td>空格 = AND</td><td><code>9/11 晚上;9/22 下午</code></td><td>同時包含兩個詞才匹配</td></tr>
          <tr><td>完整日期</td><td><code>2025/12/25</code></td><td>精確比對年月日</td></tr>
          <tr><td>組合範例</td><td><code>2025/12/25 晚上;2025/12/26 下午</code></td><td>優先選 25 號晚上場</td></tr>
          <tr><td>留空</td><td>（空白）</td><td>依「日期排序方式」自動選擇</td></tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: '分號和空格分別是 OR 和 AND？',
        a: '是的。<strong>分號（;）</strong>是 OR：依序嘗試每組，第一個匹配就選取。<strong>空格</strong>是 AND：同一組內的所有關鍵字必須同時出現才算匹配。'
      },
      {
        q: '留空會怎樣？',
        a: '留空時，系統會根據「日期排序方式」（從上到下/從下到上/中間/隨機）自動選擇可用的第一個日期，等同於開啟「日期自動遞補」。'
      }
    ],
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#日期關鍵字'
  },

  area_keyword: {
    title: '區域關鍵字',
    short: '指定要選擇的區域或票種，用分號(;)分隔多組',
    detail: `
      <p>設定想選取的座位區域或票種，系統會依序比對並選擇第一個匹配的選項。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>格式</th><th>範例</th><th>說明</th></tr></thead>
        <tbody>
          <tr><td>單一關鍵字</td><td><code>搖滾區</code></td><td>包含「搖滾區」即匹配</td></tr>
          <tr><td>分號 = OR</td><td><code>搖滾區;VIP;前排</code></td><td>依序嘗試，第一個匹配就選取</td></tr>
          <tr><td>空格 = AND</td><td><code>搖滾區 前排;VIP 中央</code></td><td>同時包含兩詞才匹配</td></tr>
          <tr><td>票種含逗號</td><td><code>2,680;1,980</code></td><td>票價中逗號是文字，不影響分隔</td></tr>
          <tr><td>留空</td><td>（空白）</td><td>依「區域排序方式」自動選擇</td></tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: '票價中有逗號（如 2,680）會與分隔符衝突嗎？',
        a: '不會。系統使用<strong>分號（;）</strong>作為多組關鍵字的分隔符，逗號（,）只是一般文字。輸入 <code>2,680;1,980</code> 完全正確，系統會嘗試匹配「2,680」或「1,980」。'
      }
    ],
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#區域關鍵字'
  },

  date_auto_fallback: {
    title: '日期自動遞補',
    short: '關鍵字全未匹配時，是否自動選擇可用日期（預設：關閉）',
    detail: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>狀態</th><th>行為</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">關閉（預設）</span></td>
            <td>嚴格模式。若日期關鍵字全部未匹配，<strong>停止選擇</strong>並等待下一輪重試。</td>
          </tr>
          <tr>
            <td><span class="badge bg-success">開啟</span></td>
            <td>自動遞補。關鍵字未匹配時，依「日期排序方式」自動選擇可用的第一個日期。</td>
          </tr>
        </tbody>
      </table>
      <p><strong>使用建議：</strong>如果您確定要指定特定場次，請<strong>保持關閉</strong>，避免誤選不想要的場次。若您接受任意可用場次，可開啟此選項。</p>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>開啟後，當所有關鍵字都未匹配時系統會自動選擇，可能選到您不想要的場次（如售完的場次重新開放時）。</p>`,
    faq: [
      {
        q: '為何預設關閉？',
        a: '預設關閉是為了安全。搶票時若誤選錯誤場次，可能造成購票失敗或買到不需要的票。嚴格模式確保只有在明確匹配時才繼續。'
      },
      {
        q: '開啟後系統如何選擇日期？',
        a: '開啟後，系統依照「日期排序方式」設定（從上到下、從下到上、中間、隨機）選擇可用的第一個日期選項。'
      }
    ],
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#日期自動遞補--新功能'
  },

  // --- Group A: Guide-documented fields without help-icon ---

  auto_press_next_step_button: {
    title: 'KKTIX 點選下一步按鈕',
    short: '自動點擊 KKTIX 訂購流程的「下一步」按鈕（預設：開啟）',
    detail: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>狀態</th><th>行為</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-success">開啟（預設）</span></td>
            <td>搶到票後自動點擊「下一步」進入訂單頁面</td>
          </tr>
          <tr>
            <td><span class="badge bg-secondary">關閉</span></td>
            <td>搶到票後停在選座頁面，等待人工點擊</td>
          </tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">僅適用 KKTIX 平台。建議保持開啟以加快搶票速度。</p>`,
    link: null
  },

  max_dwell_time: {
    title: 'KKTIX 購票最長停留',
    short: '在 KKTIX 訂單頁面的最大停留秒數（預設：90 秒）',
    detail: `
      <p>設定程式在 KKTIX 訂單填寫頁面的最長等待時間（單位：秒）。</p>
      <p>超過此時間後，程式會自動送出訂單，避免因頁面逾時而失去搶到的票。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>值</th><th>說明</th></tr></thead>
        <tbody>
          <tr><td><code>90</code>（預設）</td><td>90 秒後自動送出</td></tr>
          <tr><td>較大值</td><td>給更多時間人工確認訂單資訊</td></tr>
          <tr><td>較小值</td><td>更快送出，但可能在未填完前送出</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">僅適用 KKTIX 平台。若有自動填寫功能，30-60 秒通常已足夠。</p>`,
    link: null
  },

  play_ticket_sound: {
    title: '有票時播放音效',
    short: '程式選到票時播放提示音（預設：開啟）',
    detail: `
      <p>當程式成功選到票券時，播放音效提醒您注意畫面。</p>
      <p>音效檔路徑由「音效檔」欄位設定，預設為內建的 <code>ding-dong.wav</code>。</p>
      <p class="text-muted small mb-0">在背景執行時特別有用，讓您不用一直盯著螢幕。</p>`,
    link: null
  },

  play_order_sound: {
    title: '訂購時播放音效',
    short: '程式送出訂單時播放提示音（預設：開啟）',
    detail: `
      <p>當程式成功送出訂單時，播放音效提醒您儘速完成付款。</p>
      <p>訂單送出後通常有時間限制完成付款，音效提醒可避免錯過付款時間。</p>`,
    link: null
  },

  play_sound_filename: {
    title: '音效檔',
    short: '自訂音效提示音的檔案路徑',
    detail: `
      <p>設定播放提示音時使用的音效檔案路徑。</p>
      <p><strong>預設：</strong><code>assets/sounds/ding-dong.wav</code>（已內建）</p>
      <p><strong>支援格式：</strong><code>.wav</code>、<code>.mp3</code></p>
      <p>可使用相對路徑（相對於程式執行目錄）或絕對路徑。</p>
      <p class="text-muted small mb-0">若留空或檔案不存在，則使用系統預設音效。</p>`,
    link: null
  },

  window_size: {
    title: '瀏覽器視窗大小',
    short: '設定搶票瀏覽器的視窗尺寸（格式：寬,高）',
    detail: `
      <p>設定搶票用瀏覽器視窗的寬度與高度（單位：像素）。</p>
      <p><strong>格式：</strong><code>寬度,高度</code>（例如：<code>600,1024</code>）</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>設定值</th><th>說明</th></tr></thead>
        <tbody>
          <tr><td><code>600,1024</code>（預設）</td><td>窄視窗，讓搶票視窗不佔滿螢幕</td></tr>
          <tr><td><code>1280,800</code></td><td>標準桌面尺寸</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">部分平台在太小的視窗可能有 RWD 切換，若遇到問題可嘗試加大視窗。</p>`,
    link: null
  },

  discount_code: {
    title: '優惠代碼',
    short: '自動填入優惠序號、會員序號等驗證欄位',
    detail: `
      <p>設定後，程式會自動偵測並填入訂單頁面的序號或優惠碼欄位。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>平台</th><th>用途</th></tr></thead>
        <tbody>
          <tr><td>KKTIX</td><td>會員序號（member_code）、粉絲驗證問題答案</td></tr>
          <tr><td>TicketPlus（遠大）</td><td>優惠序號（exclusive_code）</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">留空則不自動填入。若活動不需序號可留空，對搶票流程無影響。</p>`,
    link: null
  },

  ocr_model_path: {
    title: '自訂 OCR 模型',
    short: '指定自訓練 OCR 模型的資料夾路徑（目前僅支援 Ticketmaster）',
    detail: `
      <p>填入包含自訓練 OCR 模型的資料夾路徑。</p>
      <p><strong>資料夾內需包含：</strong></p>
      <ul>
        <li><code>custom.onnx</code> — ONNX 格式模型</li>
        <li><code>charsets.json</code> — 字符集定義</li>
      </ul>
      <p><strong>路徑範例：</strong><code>assets/ocr_model</code>（相對路徑）</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>狀況</th><th>行為</th></tr></thead>
        <tbody>
          <tr><td>路徑未設定</td><td>使用預設 ddddocr 模型</td></tr>
          <tr><td>檔案不存在</td><td>顯示警告，自動改用預設模型</td></tr>
        </tbody>
      </table>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>目前僅 Ticketmaster 平台支援此設定。</p>`,
    link: null
  },

  // --- Phase 4: Autofill tab (cookie fields) + Runtime tab ---

  tixcraft_sid: {
    title: '拓元家族 Cookie',
    short: '填入已登入的拓元/iVIS/拓聚 Session Cookie',
    detail: `
      <p>填入後程式可跳過登入頁面直接搶票。適用平台：<strong>TixCraft（拓元）</strong>、<strong>iVIS</strong>、<strong>拓聚 TicketPlus</strong>。</p>
      <p><strong>取得步驟（Chrome）：</strong></p>
      <ol>
        <li>在瀏覽器登入 TixCraft</li>
        <li>按 <code>F12</code> 開啟開發人員工具</li>
        <li>點選「Application」→「Cookies」→ 選擇 tixcraft.com</li>
        <li>找到 <code>TIXUISID</code>（或 <code>IVUISID</code> / <code>TIXPUISID</code>）</li>
        <li>複製 Value 欄位的值貼入此處</li>
      </ol>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>正確的 TIXUISID 不應以 "g." 開頭。若以 "g." 開頭，表示您複製了錯誤的值。</p>`,
    faq: [
      {
        q: 'Cookie 過期後怎辦？',
        a: '重新登入 TixCraft 後，再次取得新的 Cookie 值更新到此處即可。Cookie 通常有效期約數天至數週。'
      }
    ],
    link: null
  },

  ibonqware: {
    title: 'ibon Cookie',
    short: '填入已登入的 ibon 售票 Session Cookie',
    detail: `
      <p>填入後程式可跳過 ibon 售票網登入流程。</p>
      <p><strong>取得步驟（Chrome）：</strong></p>
      <ol>
        <li>在瀏覽器登入 ibon 售票網（tickets.ibon.com.tw）</li>
        <li>按 <code>F12</code> 開啟開發人員工具</li>
        <li>點選「Application」→「Cookies」→ 選擇 tickets.ibon.com.tw</li>
        <li>找到 <code>ibonqware</code></li>
        <li>複製 Value 欄位的值貼入此處</li>
      </ol>`,
    link: null
  },

  funone_session_cookie: {
    title: 'FunOne Cookie',
    short: '填入已登入的 FunOne 售票 Session Cookie',
    detail: `
      <p>填入後程式可跳過 FunOne 售票網登入流程（funone.com.tw）。</p>
      <p><strong>取得步驟（Chrome）：</strong></p>
      <ol>
        <li>在瀏覽器登入 FunOne 售票網</li>
        <li>按 <code>F12</code> 開啟開發人員工具</li>
        <li>點選「Application」→「Cookies」→ 選擇 funone.com.tw</li>
        <li>找到 <code>ticket_session</code></li>
        <li>複製 Value 欄位的值貼入此處</li>
      </ol>`,
    link: null
  },

  fansigo_cookie: {
    title: 'FANSI GO Cookie',
    short: '填入已登入的 FANSI GO Session Cookie（可取代帳號密碼登入）',
    detail: `
      <p>填入後程式使用 Cookie 登入，可取代帳號密碼方式。</p>
      <p><strong>取得步驟（Chrome）：</strong></p>
      <ol>
        <li>在瀏覽器登入 FANSI GO</li>
        <li>按 <code>F12</code> 開啟開發人員工具</li>
        <li>點選「Application」→「Cookies」→ 選擇 fansigo.com</li>
        <li>找到 <code>FansiAuthInfo</code></li>
        <li>複製 Value 欄位的值貼入此處</li>
      </ol>
      <p class="text-muted small mb-0">若同時填入帳號密碼和 Cookie，程式優先使用 Cookie。</p>`,
    link: null
  },

  idle_keyword: {
    title: '系統時間 - 暫停關鍵字',
    short: '指定時刻自動暫停搶票（格式 HH:MM:SS，分號分隔多個）',
    detail: `
      <p>當系統時間符合此欄位設定時，程式自動暫停搶票動作。</p>
      <p><strong>格式：</strong><code>HH:MM:SS</code>（時:分:秒），多個時間用分號分隔</p>
      <p><strong>範例：</strong><code>12:00:00;18:00:00</code>（每天中午和傍晚暫停）</p>
      <p class="text-muted small mb-0">搭配「繼續關鍵字」使用，可實現自動排程搶票。詳細說明請展開下方「時間控制功能說明」。</p>`,
    link: null
  },

  resume_keyword: {
    title: '系統時間 - 繼續關鍵字',
    short: '指定時刻自動恢復搶票（格式 HH:MM:SS，分號分隔多個）',
    detail: `
      <p>當系統時間符合此欄位設定時，程式自動恢復搶票動作。</p>
      <p><strong>格式：</strong><code>HH:MM:SS</code>（時:分:秒），多個時間用分號分隔</p>
      <p><strong>範例：</strong><code>10:00:00;14:00:00</code>（每天 10 點和下午 2 點開始搶票）</p>
      <p class="text-muted small mb-0">搭配「暫停關鍵字」使用，可實現自動排程搶票。詳細說明請展開下方「時間控制功能說明」。</p>`,
    link: null
  },

  idle_keyword_second: {
    title: '秒數 - 暫停關鍵字',
    short: '每分鐘的指定秒數自動暫停（格式 SS，分號分隔多個）',
    detail: `
      <p>當系統時間的<strong>秒數</strong>符合設定值時，程式自動暫停。每分鐘都會觸發一次。</p>
      <p><strong>格式：</strong>僅填秒數 <code>SS</code>（00-59），多個用分號分隔</p>
      <p><strong>範例：</strong><code>00;30</code>（每分鐘的 0 秒和 30 秒暫停）</p>
      <p class="text-muted small mb-0">適合需要精確按秒控制的情境。詳細說明請展開下方「時間控制功能說明」。</p>`,
    link: null
  },

  resume_keyword_second: {
    title: '秒數 - 繼續關鍵字',
    short: '每分鐘的指定秒數自動繼續（格式 SS，分號分隔多個）',
    detail: `
      <p>當系統時間的<strong>秒數</strong>符合設定值時，程式自動恢復搶票。每分鐘都會觸發一次。</p>
      <p><strong>格式：</strong>僅填秒數 <code>SS</code>（00-59），多個用分號分隔</p>
      <p><strong>範例：</strong><code>05;35</code>（每分鐘的 5 秒和 35 秒恢復搶票）</p>
      <p class="text-muted small mb-0">適合需要精確按秒控制的情境。詳細說明請展開下方「時間控制功能說明」。</p>`,
    link: null
  },

  // --- Phase 3: Advanced settings + Verification tab ---

  auto_reload_page_interval: {
    title: '自動刷新頁面間隔',
    short: '活動頁面的自動重新整理間隔秒數（0 = 停用）',
    detail: `
      <p>設定程式在目標頁面等待時自動刷新的間隔時間（單位：秒）。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>值</th><th>行為</th></tr></thead>
        <tbody>
          <tr><td><code>0</code></td><td>停用自動刷新</td></tr>
          <tr><td><code>3</code></td><td>每 3 秒重新整理一次</td></tr>
          <tr><td><code>5</code>（建議）</td><td>每 5 秒重新整理，平衡速度與負載</td></tr>
        </tbody>
      </table>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>TixCraft 等平台偵測到過於頻繁的刷新可能觸發限制，建議不要低於 3 秒。</p>`,
    link: null
  },

  headless: {
    title: '無圖形界面模式',
    short: '背景執行瀏覽器，不顯示視窗（預設：關閉）',
    detail: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>狀態</th><th>行為</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">關閉（預設）</span></td>
            <td>顯示瀏覽器視窗，可即時觀察搶票進度</td>
          </tr>
          <tr>
            <td><span class="badge bg-warning text-dark">開啟</span></td>
            <td>完全不顯示視窗，在背景執行，節省系統資源</td>
          </tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: '為何不建議長期開啟？',
        a: '無圖形界面模式下，若遇到需要人工介入的情況（如圖形驗證碼、異常頁面），您無法即時發現和處理。建議先以正常模式確認運作正常後再考慮開啟。'
      }
    ],
    link: null
  },

  verbose: {
    title: '輸出除錯訊息',
    short: '在輸出視窗顯示詳細操作紀錄（預設：關閉）',
    detail: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>狀態</th><th>行為</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">關閉（預設）</span></td>
            <td>只顯示重要訊息（搶票成功、錯誤等）</td>
          </tr>
          <tr>
            <td><span class="badge bg-info text-dark">開啟</span></td>
            <td>輸出每個操作步驟的詳細資訊，含時間戳</td>
          </tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">提示：排查問題時建議開啟，正常搶票時可關閉以減少輸出干擾。</p>`,
    link: null
  },

  discord_webhook_url: {
    title: 'Discord Webhook 通知',
    short: '搶票成功後傳送 Discord 通知',
    detail: `
      <p>填入 Discord Webhook URL，搶票成功時程式會自動傳送通知訊息。</p>
      <p><strong>取得 Webhook URL 步驟：</strong></p>
      <ol>
        <li>在 Discord 選擇目標頻道 → 編輯頻道</li>
        <li>點選「整合」→「Webhooks」→「新 Webhook」</li>
        <li>複製 Webhook URL 貼入此處</li>
      </ol>
      <p><strong>格式範例：</strong><br>
      <code>https://discord.com/api/webhooks/123456789/abcdef...</code></p>
      <p class="text-muted small mb-0">留空則不傳送 Discord 通知。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#discord-webhook-通知'
  },

  telegram_bot_token: {
    title: 'Telegram Bot Token',
    short: 'Telegram 通知機器人的 Token',
    detail: `
      <p>填入 Telegram Bot 的 Token，搶票成功時程式會透過此 Bot 傳送通知。</p>
      <p><strong>取得 Token 步驟：</strong></p>
      <ol>
        <li>在 Telegram 搜尋 <code>@BotFather</code></li>
        <li>傳送 <code>/newbot</code> 建立新 Bot</li>
        <li>依指示設定名稱，複製取得的 Token</li>
      </ol>
      <p><strong>格式：</strong><code>123456789:ABCdefGHI-jklMNO...</code></p>
      <p class="text-muted small mb-0">留空則不啟用 Telegram 通知。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#telegram-bot-通知'
  },

  telegram_chat_id: {
    title: 'Telegram Chat ID',
    short: '接收通知的 Telegram 聊天室 ID，多個用逗號分隔',
    detail: `
      <p>填入要接收通知的 Telegram Chat ID。</p>
      <p><strong>取得 Chat ID：</strong></p>
      <ol>
        <li>對您建立的 Bot 傳送任意訊息</li>
        <li>在瀏覽器開啟：<code>https://api.telegram.org/bot{TOKEN}/getUpdates</code></li>
        <li>從 JSON 回應中找 <code>chat.id</code> 的數值</li>
      </ol>
      <p><strong>多人通知：</strong>用逗號分隔多個 ID，例如：<code>123456789, 987654321</code></p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#telegram-bot-通知'
  },

  server_port: {
    title: '設定介面 Port',
    short: '設定 Web UI 的監聽埠號（預設：16888）',
    detail: `
      <p>設定 Tickets Hunter 設定介面的 HTTP 監聽埠號。</p>
      <p>預設值：<code>16888</code>，連線網址：<code>http://localhost:16888</code></p>
      <p>若預設埠號已被其他程式佔用，可修改為 1024–65535 之間的任意數值。</p>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>修改後需重新啟動程式，並以新的埠號連線。</p>`,
    faq: [
      {
        q: '改完後如何連線？',
        a: '重新啟動後，在瀏覽器輸入 <code>http://localhost:{新埠號}</code> 即可連線。'
      }
    ],
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#設定介面-portserver_port'
  },

  ocr_captcha_enable: {
    title: 'OCR 驗證碼辨識',
    short: '啟用 OCR 自動辨識文字驗證碼（預設：關閉）',
    detail: `
      <p>開啟後，程式會使用 OCR 模型自動辨識文字驗證碼，並自動填入答案。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>狀態</th><th>行為</th></tr></thead>
        <tbody>
          <tr><td><span class="badge bg-secondary">關閉</span></td><td>遇到驗證碼時暫停，等待人工輸入</td></tr>
          <tr><td><span class="badge bg-success">開啟</span></td><td>自動辨識並填入驗證碼</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">目前支援 TixCraft、iBon、KHAM 等平台的文字驗證碼。</p>`,
    faq: [
      {
        q: '辨識不準確時怎麼辦？',
        a: '可嘗試關閉 OCR 改為人工輸入，或查看是否有對應平台的自訓練模型可使用。'
      }
    ],
    link: null
  },

  ocr_captcha_force_submit: {
    title: 'OCR 自動送出',
    short: 'OCR 辨識後不等待確認直接送出（預設：關閉）',
    detail: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>狀態</th><th>行為</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">關閉（預設）</span></td>
            <td>OCR 辨識後填入答案，仍等待人工確認後送出</td>
          </tr>
          <tr>
            <td><span class="badge bg-warning text-dark">開啟</span></td>
            <td>辨識完成立即自動送出，不等待任何確認</td>
          </tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: '辨識錯誤後自動送出會怎樣？',
        a: '大多數平台會顯示驗證碼錯誤，程式會重新嘗試。不會造成永久性失敗，但會浪費一次嘗試機會。確認辨識準確率穩定後再開啟此選項。'
      }
    ],
    link: null
  },

  user_guess_string: {
    title: '使用者自定字典',
    short: '預先設定驗證問題的可能答案（分號分隔）',
    detail: `
      <p>當系統偵測到需要文字作答的驗證問題時，會優先嘗試此處填入的答案。</p>
      <p><strong>格式：</strong>多個答案用分號（;）分隔</p>
      <p><strong>範例：</strong><code>答案A;答案B;正確答案</code></p>
      <p>若此處留空且開啟了「自動猜測驗證問題」，系統會嘗試自動推測答案。</p>
      <p class="text-muted small mb-0">提示：填入已知的正確答案，可大幅提高通過驗證的速度。</p>`,
    faq: [
      {
        q: '答案有優先順序嗎？',
        a: '系統會依序嘗試每個答案（分號分隔）。建議將最可能的答案放在最前面。'
      }
    ],
    link: null
  },

  // --- Phase 2: Basic settings tab remaining fields ---

  ticket_number: {
    title: '張數',
    short: '每次搶購的票券張數（1-10）',
    detail: `
      <p>設定每次搶購時要選取的票券數量。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>張數</th><th>適用情境</th></tr></thead>
        <tbody>
          <tr><td>1 張</td><td>個人購票，成功率最高</td></tr>
          <tr><td>2 張</td><td>雙人同行</td></tr>
          <tr><td>3-4 張</td><td>多人同行（注意：張數越多，有票但數量不足時可能失敗）</td></tr>
        </tbody>
      </table>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>張數設定越高，因票數不足而搶購失敗的機率越大。建議以最低需求張數設定。</p>`,
    link: null
  },

  refresh_datetime: {
    title: '刷新在指定時間',
    short: '讓程式在特定時間點才開始搶票',
    detail: `
      <p>設定程式在指定的日期時間才開始嘗試搶票。用於場次在特定時間才開放售票的情境。</p>
      <p><strong>格式：</strong><code>YYYY/MM/DD HH:MM:SS</code></p>
      <p>範例：<code>2025/12/25 10:00:00</code></p>
      <p>在指定時間到達前，程式會持續等待並每秒確認時間。時間到達後立即開始刷新搶票。</p>
      <p class="text-muted small mb-0">提示：建議設定比開售時間早 1-2 秒，補償網路與處理延遲。</p>`,
    faq: [
      {
        q: '留空會怎樣？',
        a: '留空表示不設定等待時間，程式啟動後立即開始搶票。'
      },
      {
        q: '超過指定時間才啟動程式會怎樣？',
        a: '若啟動時已超過指定時間，程式會直接開始搶票，不會等待到下一個週期。'
      }
    ],
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#刷新在指定時間refresh_datetime'
  },

  date_select_mode: {
    title: '日期排序方式',
    short: '關鍵字未設定或遞補時，如何選擇可用日期',
    detail: `
      <p>當「日期關鍵字」留空、或開啟「日期自動遞補」時，系統依此設定決定選擇哪個日期。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>選項</th><th>行為</th><th>適用情境</th></tr></thead>
        <tbody>
          <tr><td><code>from top to bottom</code></td><td>選擇列表中最上方的日期</td><td>優先選最早場次</td></tr>
          <tr><td><code>from bottom to top</code></td><td>選擇列表中最下方的日期</td><td>優先選最晚場次</td></tr>
          <tr><td><code>center</code></td><td>選擇列表中間位置的日期</td><td>分散選擇</td></tr>
          <tr><td><code>random</code></td><td>隨機選擇可用日期</td><td>不在意哪場</td></tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: '設定了日期關鍵字後，排序方式還有作用嗎？',
        a: '有。當關鍵字匹配到多個日期時，系統會依照排序方式決定選哪個。另外，開啟「日期自動遞補」時也會用到此設定。'
      }
    ],
    link: null
  },

  area_select_mode: {
    title: '區域排序方式',
    short: '關鍵字未設定或遞補時，如何選擇可用區域',
    detail: `
      <p>當「區域關鍵字」留空、或開啟「區域自動遞補」時，系統依此設定決定選擇哪個區域。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>選項</th><th>行為</th></tr></thead>
        <tbody>
          <tr><td><code>from top to bottom</code></td><td>選擇列表中最上方的區域</td></tr>
          <tr><td><code>from bottom to top</code></td><td>選擇列表中最下方的區域</td></tr>
          <tr><td><code>center</code></td><td>選擇列表中間位置的區域</td></tr>
          <tr><td><code>random</code></td><td>隨機選擇可用區域</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">提示：大多數售票平台的區域列表是從貴到廉或從前排到後排排列，<code>from top to bottom</code> 通常代表較好/較貴的席別。</p>`,
    link: null
  },

  keyword_exclude: {
    title: '排除關鍵字',
    short: '指定要跳過不選的日期或區域',
    detail: `
      <p>設定不想選取的日期或區域關鍵字，即使符合其他條件也會跳過。</p>
      <p>格式與「日期/區域關鍵字」相同，使用分號（;）分隔多個條件：</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>範例</th><th>效果</th></tr></thead>
        <tbody>
          <tr><td><code>已售完</code></td><td>跳過標示「已售完」的選項</td></tr>
          <tr><td><code>輪椅;無障礙</code></td><td>跳過任何包含「輪椅」或「無障礙」的選項</td></tr>
          <tr><td><code>12/24;12/25</code></td><td>跳過 12/24 和 12/25 的場次</td></tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: '排除關鍵字和區域關鍵字同時設定，哪個優先？',
        a: '排除關鍵字優先。若某選項同時符合「區域關鍵字」（應選）和「排除關鍵字」（應跳過），系統會跳過該選項。'
      }
    ],
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#排除關鍵字'
  },

  area_auto_fallback: {
    title: '區域自動遞補',
    short: '關鍵字全未匹配時，是否自動選擇可用區域（預設：關閉）',
    detail: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>狀態</th><th>行為</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">關閉（預設）</span></td>
            <td>嚴格模式。若區域關鍵字全部未匹配，<strong>停止選擇</strong>並等待下一輪重試。</td>
          </tr>
          <tr>
            <td><span class="badge bg-success">開啟</span></td>
            <td>自動遞補。關鍵字未匹配時，依「區域排序方式」自動選擇可用的第一個區域。</td>
          </tr>
        </tbody>
      </table>
      <p><strong>使用建議：</strong>如果您指定了特定區域（如搖滾區、前排），請<strong>保持關閉</strong>，避免誤選視線不佳或無障礙專用區域。</p>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>自動遞補可能選到視線不佳區域、輪椅席或其他非預期席別，請謹慎使用。</p>`,
    faq: [
      {
        q: '日期遞補和區域遞補可以單獨設定嗎？',
        a: '可以。這是兩個獨立的開關，可以只開啟其中一個，例如允許自動選日期但嚴格限制區域，或反之。'
      },
      {
        q: '為何預設關閉？',
        a: '預設關閉是為了安全。自動遞補可能選到輪椅席、視線不佳席別或票價較高的區域，造成非預期的購票結果。'
      }
    ],
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#區域自動遞補--新功能'
  },

  show_timestamp: {
    title: '顯示時間戳記',
    short: '在每行輸出前加上 [HH:MM:SS] 時間標記',
    detail: `
      <p>啟用後，程式的每一行輸出都會加上時間戳記，方便追蹤搶票流程的時間點。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>狀態</th><th>輸出格式</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">關閉（預設）</span></td>
            <td><code>[DATE] found: 2024-12-31</code></td>
          </tr>
          <tr>
            <td><span class="badge bg-success">開啟</span></td>
            <td><code>[09:30:15] [DATE] found: 2024-12-31</code></td>
          </tr>
        </tbody>
      </table>
      <p class="mb-0 text-muted small">適合搶票後檢視日誌、分析各步驟耗時時使用。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#顯示時間戳記show_timestamp'
  },

  reset_browser_interval: {
    title: '重新啟動瀏覽器間隔(秒)',
    short: '定時自動重啟瀏覽器（0 = 停用）',
    detail: `
      <p>設定多少秒後自動重啟瀏覽器。設為 <code>0</code>（預設）則停用此功能。</p>
      <ul>
        <li>最小值：<strong>20 秒</strong>（低於此值會自動調整為 20）</li>
        <li>設為 <code>0</code> — 不自動重啟</li>
      </ul>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>此設定目前主程式尚未完整實作自動重啟邏輯，建議保持預設值 <code>0</code>。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#重新啟動瀏覽器間隔秒reset_browser_interval'
  },

  proxy_server_port: {
    title: '代理伺服器',
    short: '填入代理伺服器位址，格式：IP:Port（留空不使用）',
    detail: `
      <p>設定瀏覽器連線使用的代理伺服器，留空則直接連線。</p>
      <p><strong>格式：</strong><code>IP位址:Port</code></p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>範例</th><th>說明</th></tr></thead>
        <tbody>
          <tr><td><code>127.0.0.1:8080</code></td><td>本機代理（如 Clash、v2ray）</td></tr>
          <tr><td><code>192.168.1.1:3128</code></td><td>區域網路代理伺服器</td></tr>
          <tr><td>（空白）</td><td>不使用代理，直接連線</td></tr>
        </tbody>
      </table>
      <p class="mb-0 text-muted small">填入後，瀏覽器啟動時會自動套用 <code>--proxy-server=</code> 參數。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#代理伺服器proxy_server_port'
  },

  disable_adjacent_seat: {
    title: '停用相鄰座位',
    short: '啟用可接受非連座，提高搶票成功率',
    detail: `
      <p>控制是否接受不相鄰（非連座）的座位組合。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>狀態</th><th>行為</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">關閉（預設）</span></td>
            <td>只選相鄰連座，不接受非連座。</td>
          </tr>
          <tr>
            <td><span class="badge bg-success">開啟</span></td>
            <td>接受非連座位置，提高選到票的機率。</td>
          </tr>
        </tbody>
      </table>
      <p><strong>支援平台：</strong>iBon、年代（Ticket）、KHAM、Ticketmaster</p>
      <p class="mb-0 text-muted small">適合多人同行但不在意座位是否相鄰的情況。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#停用相鄰座位disable_adjacent_seat'
  },

  hide_some_image: {
    title: '隱藏部分圖片',
    short: '封鎖非必要資源載入，加速頁面回應',
    detail: `
      <p>啟用後，程式會透過網路封鎖減少非必要資源，讓搶票頁面載入更快。</p>
      <p><strong>封鎖的資源類型：</strong></p>
      <ul>
        <li>網頁字型（<code>.woff</code>）</li>
        <li>網站圖示（<code>.ico</code>）</li>
        <li>部分活動圖片</li>
      </ul>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>啟用後頁面外觀可能不完整，但不影響搶票功能。網路速度正常時無需啟用。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#隱藏部分圖片hide_some_image'
  },

  block_facebook_network: {
    title: '封鎖 Facebook 網路',
    short: '封鎖 Facebook 追蹤腳本，減少外部連線',
    detail: `
      <p>啟用後，程式會封鎖所有 Facebook 相關網路請求。</p>
      <p><strong>封鎖的網域：</strong></p>
      <ul>
        <li><code>*.facebook.com/*</code></li>
        <li><code>*.fbcdn.net/*</code></li>
      </ul>
      <p>部分票務平台頁面內嵌了 Facebook 追蹤腳本，若這些腳本拖慢頁面速度，可啟用此選項加速載入。</p>
      <p class="mb-0 text-muted small">與「隱藏部分圖片」可同時啟用，效果互補。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#封鎖-facebook-網路block_facebook_network'
  },

  auto_guess_options: {
    title: '自動猜測驗證選項',
    short: '自動推測選項題答案（KKTIX/TixCraft/iBon）',
    detail: `
      <p>啟用後，程式會嘗試根據題目文字自動推測驗證選項題的正確答案。</p>
      <p><strong>適用題型：</strong>部分平台在購票時出現的選擇題驗證，例如：</p>
      <ul>
        <li>數學題：「1 + 1 = ?」</li>
        <li>地理題：「台北 101 在哪個縣市？」</li>
        <li>常識題：演唱會相關問答</li>
      </ul>
      <table class="table table-sm table-bordered">
        <thead><tr><th>狀態</th><th>行為</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">關閉（預設）</span></td>
            <td>不自動猜測，等待手動選擇。</td>
          </tr>
          <tr>
            <td><span class="badge bg-success">開啟</span></td>
            <td>程式自動推測並選取答案，加快流程。</td>
          </tr>
        </tbody>
      </table>
      <p><strong>支援平台：</strong>KKTIX、TixCraft、iBon</p>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>猜測準確率依題目類型而異，若猜錯可能導致購票失敗，建議先測試後再決定是否啟用。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#自動猜測驗證選項auto_guess_options'
  },

  ocr_captcha_image_source: {
    title: 'OCR 圖片取得方式',
    short: '驗證碼圖片來源：canvas（預設）或 NonBrowser',
    detail: `
      <p>設定程式取得驗證碼圖片的方式。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>選項</th><th>說明</th></tr></thead>
        <tbody>
          <tr>
            <td><code>canvas</code>（預設）</td>
            <td>透過 JavaScript Canvas API 從瀏覽器頁面直接擷取驗證碼圖片。適用於大多數情況。</td>
          </tr>
          <tr>
            <td><code>NonBrowser</code></td>
            <td>啟動獨立的 NonBrowser 視窗來取得驗證碼（需搭配外部驗證碼工具使用）。</td>
          </tr>
        </tbody>
      </table>
      <p class="mb-0 text-muted small">一般情況保持 <code>canvas</code> 即可，若主瀏覽器無法正確擷取驗證碼才考慮切換為 <code>NonBrowser</code>。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#ocr圖片取得方式image_source'
  },

  ocr_captcha_use_universal: {
    title: '使用通用 OCR 模型',
    short: '使用內建通用模型（準確率 99%+），停用改回官方 ddddocr',
    detail: `
      <p>選擇驗證碼辨識所使用的 OCR 模型。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>狀態</th><th>模型</th><th>準確率</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-success">啟用（預設）</span></td>
            <td>通用自訓模型（<code>assets/model/universal/</code>）</td>
            <td>99%+</td>
          </tr>
          <tr>
            <td><span class="badge bg-secondary">停用</span></td>
            <td>ddddocr 官方模型</td>
            <td>較低</td>
          </tr>
        </tbody>
      </table>
      <p><strong>支援平台：</strong>TixCraft、iBon、KHAM</p>
      <p class="mb-0 text-muted small">建議保持啟用。若遇到辨識結果異常（如亂碼），可嘗試停用後測試。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#使用通用-ocr-模型use_universal'
  },

  remote_url: {
    title: '設定介面網址',
    short: '自動產生的設定 UI 存取網址（唯讀）',
    detail: `
      <p>設定介面的存取網址，由系統根據「設定介面 Port」自動產生。</p>
      <p><strong>格式：</strong><code>http://127.0.0.1:{Port}/</code></p>
      <p>例如，Port 為 <code>16888</code> 時，網址為 <code>http://127.0.0.1:16888/</code>。</p>
      <p><strong>此欄位為唯讀</strong>，修改後會在下次儲存設定時被自動覆蓋。</p>
      <p class="mb-0 text-muted small">若需要從其他腳本或工具存取設定 API，可複製此網址使用。</p>`,
    link: 'https://github.com/bouob/tickets_hunter/blob/main/guide/settings-guide.md#設定介面網址remote_url'
  }
};
