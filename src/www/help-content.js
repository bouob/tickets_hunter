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
          <tr><td>TixCraft／Ticketmaster</td><td>驗證題的會員編號／序號類提示備援答案（例如 Weverse 預購 MY MEMBERSHIP）</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">留空則不自動填入。TixCraft／Ticketmaster 僅在驗證題明確要求會員、序號或編號時才會自動送出此欄位作為備援，避免被無關題目浪費嘗試次數。</p>`,
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

  tixcraft_soft_block_delay: {
    title: '暫時鎖定等待秒數',
    short: '自訂拓元、添翼、Indievox 白畫面暫時鎖定後的等待秒數',
    detail: `
      <p>當程式遇到拓元家族白畫面暫時鎖定時，可用此欄位指定多久後再嘗試返回原頁面。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>設定值</th><th>行為</th></tr></thead>
        <tbody>
          <tr><td>留空</td><td>沿用預設隨機 <code>240-420</code> 秒</td></tr>
          <tr><td><code>30</code></td><td>固定等待 30 秒後重試</td></tr>
          <tr><td><code>60</code></td><td>固定等待 60 秒後重試</td></tr>
        </tbody>
      </table>
      <p><strong>套用範圍：</strong>僅影響拓元、添翼、Indievox 的白畫面暫時鎖定等待，不影響 Ticketmaster。</p>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>若設得太短，可能仍在封鎖期間內，重試後依然會回到白畫面。</p>`,
    link: null
  },

  tixcraft_allow_less_tickets: {
    title: '不足張數仍購買',
    short: '拓元家族票數不足時，允許購買小於設定張數的最大可用張數',
    detail: `
      <p>此開關影響拓元、添翼、Indievox 與 Ticketmaster（同一套售票系統）。預設關閉，避免買到少於您原本設定的張數。</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>狀態</th><th>行為</th></tr></thead>
        <tbody>
          <tr><td>關閉（預設）</td><td>設定 4 張但只剩 3、2、1 可選時，不送出並等待重新整理</td></tr>
          <tr><td>開啟</td><td>設定 4 張但只剩 3、2、1 可選時，改選 3 張並繼續送出</td></tr>
        </tbody>
      </table>
      <p class="text-warning-emphasis small mb-0"><strong>注意：</strong>開啟後可能買到少於原本設定的張數，請只在您能接受較少張數時使用。</p>`,
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

const HELP_CONTENT_EN_META = {
  homepage: {
    title: 'Homepage',
    short: 'Enter the event page URL. Multiple ticketing platforms are supported.',
    detailHtml: `
      <p><strong>Required field.</strong> Enter the event page URL for the tickets you want to purchase.</p>
      <p>Example URL formats by platform:</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Platform</th><th>Example URL</th></tr></thead>
        <tbody>
          <tr><td>TixCraft</td><td><code>https://tixcraft.com/activity/detail/...</code></td></tr>
          <tr><td>KKTIX</td><td><code>https://kktix.com/events/...</code></td></tr>
          <tr><td>TicketPlus</td><td><code>https://ticketplus.com.tw/activity/...</code></td></tr>
          <tr><td>iBon</td><td><code>https://tickets.ibon.com.tw/event/...</code></td></tr>
          <tr><td>FamiTicket</td><td><code>https://ticket.Family.com.tw/...</code></td></tr>
        </tbody>
      </table>
      <p class="mb-0 text-muted small">Tip: copy the event page URL directly from your browser address bar and paste it here.</p>`,
  },
  date_keyword: {
    title: 'Date keywords',
    short: 'Specify preferred dates. Separate multiple groups with semicolons (;).',
    detailHtml: `
      <p>Set the show date keywords you want to select. Tickets Hunter checks them in order and picks the first matching option.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Format</th><th>Example</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td>Single keyword</td><td><code>9/11</code></td><td>Matches any option that contains "9/11"</td></tr>
          <tr><td>Semicolon = OR</td><td><code>9/11;9/22;3/3</code></td><td>Try each group in order and select the first match</td></tr>
          <tr><td>Space = AND</td><td><code>9/11 evening;9/22 afternoon</code></td><td>All words in the same group must appear together</td></tr>
          <tr><td>Full date</td><td><code>2025/12/25</code></td><td>Match the exact year, month, and day</td></tr>
          <tr><td>Combined example</td><td><code>2025/12/25 evening;2025/12/26 afternoon</code></td><td>Prefer the evening show on the 25th first</td></tr>
          <tr><td>Leave empty</td><td>(blank)</td><td>Auto-select by the configured date selection order</td></tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: 'Do semicolons and spaces mean OR and AND?',
        a: 'Yes. A <strong>semicolon (;)</strong> means OR: each group is tried in sequence and the first match is selected. A <strong>space</strong> means AND: all keywords in the same group must appear together to count as a match.'
      },
      {
        q: 'What happens if I leave it empty?',
        a: 'If left empty, the system automatically picks the first available date based on the configured date selection order (top to bottom, bottom to top, center, or random). This is effectively the same as allowing date fallback.'
      }
    ],
  },
  area_keyword: {
    title: 'Area keywords',
    short: 'Specify preferred sections or ticket types. Separate multiple groups with semicolons (;).',
    detailHtml: `
      <p>Set the seat section or ticket type keywords you want to select. Tickets Hunter checks them in order and picks the first matching option.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Format</th><th>Example</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td>Single keyword</td><td><code>Rock Zone</code></td><td>Matches any option that contains "Rock Zone"</td></tr>
          <tr><td>Semicolon = OR</td><td><code>Rock Zone;VIP;Front Row</code></td><td>Try each group in order and select the first match</td></tr>
          <tr><td>Space = AND</td><td><code>Rock Zone Front Row;VIP Center</code></td><td>All words in the same group must appear together</td></tr>
          <tr><td>Ticket type with comma</td><td><code>2,680;1,980</code></td><td>Commas inside a ticket price are treated as plain text</td></tr>
          <tr><td>Leave empty</td><td>(blank)</td><td>Auto-select by the configured area selection order</td></tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: 'Will commas in prices such as 2,680 conflict with separators?',
        a: 'No. The system uses <strong>semicolons (;)</strong> to separate keyword groups. Commas are treated as plain text. Entering <code>2,680;1,980</code> is correct and the system will try to match either "2,680" or "1,980".'
      }
    ],
  },
  date_auto_fallback: {
    title: 'Date fallback',
    short: 'When no date keywords match, automatically select another available date. Default: off.',
    detailHtml: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>Status</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">Off (default)</span></td>
            <td>Strict mode. If none of the date keywords match, <strong>stop selecting</strong> and wait for the next retry cycle.</td>
          </tr>
          <tr>
            <td><span class="badge bg-success">On</span></td>
            <td>Fallback mode. If no keyword matches, automatically select the first available date based on the configured date selection order.</td>
          </tr>
        </tbody>
      </table>
      <p><strong>Recommended use:</strong> If you want a specific show, <strong>keep this off</strong> to avoid selecting the wrong session. Turn it on only if any available date is acceptable.</p>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> When enabled, the system will auto-select if all keywords miss, which may choose a session you do not want.</p>`,
    faq: [
      {
        q: 'Why is this disabled by default?',
        a: 'It is disabled by default for safety. Selecting the wrong show can cause the purchase to fail or result in unwanted tickets. Strict mode ensures the flow only continues when a clear keyword match is found.'
      },
      {
        q: 'How does the system choose a date when fallback is enabled?',
        a: 'It uses the configured date selection order: top to bottom, bottom to top, center, or random.'
      }
    ],
  },
  auto_press_next_step_button: {
    title: 'Auto-click next step',
    short: 'Automatically click the "Next Step" button in the KKTIX purchase flow. Default: on.',
    detailHtml: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>Status</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-success">On (default)</span></td>
            <td>Automatically click "Next Step" after tickets are selected and move to the order page</td>
          </tr>
          <tr>
            <td><span class="badge bg-secondary">Off</span></td>
            <td>Stay on the seat selection page after tickets are found and wait for manual input</td>
          </tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">KKTIX only. Keeping this enabled is recommended to reduce delay after tickets are selected.</p>`,
  },
  max_dwell_time: {
    title: 'KKTIX max dwell time',
    short: 'Maximum time to stay on the KKTIX order page, in seconds. Default: 90.',
    detailHtml: `
      <p>Set the maximum time that the bot stays on the KKTIX order form page before submitting automatically.</p>
      <p>After this time is reached, the order is submitted automatically to reduce the chance of losing the tickets because the page times out.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Value</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td><code>90</code> (default)</td><td>Submit automatically after 90 seconds</td></tr>
          <tr><td>Higher value</td><td>Allow more time for manual review of order details</td></tr>
          <tr><td>Lower value</td><td>Submit faster, but may submit before you finish checking the form</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">KKTIX only. If autofill is configured, 30-60 seconds is usually enough.</p>`,
  },
  play_ticket_sound: {
    title: 'Play sound when tickets are found',
    short: 'Play an alert sound when tickets are selected. Default: on.',
    detailHtml: `
      <p>Play an alert sound when the bot successfully selects tickets.</p>
      <p>The sound file path is configured in the "Sound file" field. The built-in default is <code>ding-dong.wav</code>.</p>
      <p class="text-muted small mb-0">This is especially useful when the browser is running in the background and you are not watching the screen continuously.</p>`,
  },
  play_order_sound: {
    title: 'Play sound on order submit',
    short: 'Play an alert sound after the order is submitted. Default: on.',
    detailHtml: `
      <p>Play an alert sound when the order is submitted successfully so you can complete payment quickly.</p>
      <p>Most platforms allow only a limited time to finish payment after the order is created, so the alert helps you avoid missing the payment window.</p>`,
  },
  play_sound_filename: {
    title: 'Sound file',
    short: 'Custom file path for the notification sound.',
    detailHtml: `
      <p>Set the file path used when alert sounds are played.</p>
      <p><strong>Default:</strong> <code>assets/sounds/ding-dong.wav</code> (built in)</p>
      <p><strong>Supported formats:</strong> <code>.wav</code>, <code>.mp3</code></p>
      <p>You can use either a relative path (relative to the program working directory) or an absolute path.</p>
      <p class="text-muted small mb-0">If left empty or if the file does not exist, the system default sound is used.</p>`,
  },
  window_size: {
    title: 'Browser window size',
    short: 'Set the browser window size for ticketing. Format: width,height.',
    detailHtml: `
      <p>Set the width and height of the ticketing browser window in pixels.</p>
      <p><strong>Format:</strong> <code>width,height</code> (for example <code>600,1024</code>)</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Value</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td><code>600,1024</code> (default)</td><td>Narrow window so the browser does not occupy the whole screen</td></tr>
          <tr><td><code>1280,800</code></td><td>Standard desktop size</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">Some platforms switch to a responsive layout when the window is too small. If that causes issues, try increasing the size.</p>`,
  },
  discount_code: {
    title: 'Discount / member code',
    short: 'Automatically fill discount codes, member codes, or similar verification fields.',
    detailHtml: `
      <p>When set, the bot automatically detects and fills serial code or discount code fields on the order page.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Platform</th><th>Usage</th></tr></thead>
        <tbody>
          <tr><td>KKTIX</td><td>Member code and fan-verification answers</td></tr>
          <tr><td>TicketPlus</td><td>Exclusive discount code</td></tr>
          <tr><td>TixCraft / Ticketmaster</td><td>Fallback answer when a verification prompt explicitly asks for a membership number or serial number</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">If left empty, nothing is filled automatically. On TixCraft and Ticketmaster, this value is only submitted as a fallback when the prompt clearly asks for a membership number or serial to avoid wasting attempts on unrelated questions.</p>`,
  },
  ocr_model_path: {
    title: 'Custom OCR model',
    short: 'Path to a self-trained OCR model folder. Currently supported only on Ticketmaster.',
    detailHtml: `
      <p>Enter the folder path that contains your self-trained OCR model.</p>
      <p><strong>The folder must include:</strong></p>
      <ul>
        <li><code>custom.onnx</code> - the ONNX model file</li>
        <li><code>charsets.json</code> - the character set definition</li>
      </ul>
      <p><strong>Example path:</strong> <code>assets/ocr_model</code> (relative path)</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Condition</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr><td>Path not set</td><td>Use the default ddddocr model</td></tr>
          <tr><td>Files missing</td><td>Show a warning and automatically fall back to the default model</td></tr>
        </tbody>
      </table>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> This setting is currently supported only on Ticketmaster.</p>`,
  },
  tixcraft_sid: {
    title: 'TixCraft family cookie',
    short: 'Paste a logged-in session cookie for TixCraft, iVIS, or TicketPlus.',
    detailHtml: `
      <p>With this cookie, the bot can skip the login page and start directly from an authenticated session. Supported platforms: <strong>TixCraft</strong>, <strong>iVIS</strong>, and <strong>TicketPlus</strong>.</p>
      <p><strong>How to get it in Chrome:</strong></p>
      <ol>
        <li>Log in to TixCraft in your browser.</li>
        <li>Press <code>F12</code> to open Developer Tools.</li>
        <li>Open "Application" -> "Cookies" -> select <code>tixcraft.com</code>.</li>
        <li>Find <code>TIXUISID</code> (or <code>IVUISID</code> / <code>TIXPUISID</code>).</li>
        <li>Copy the Value field and paste it here.</li>
      </ol>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> A correct <code>TIXUISID</code> should not start with <code>g.</code>. If it does, you copied the wrong value.</p>`,
    faq: [
      {
        q: 'What if the cookie expires?',
        a: 'Log in again and copy a fresh cookie value. These cookies usually stay valid for several days to several weeks.'
      }
    ],
  },
  ibonqware: {
    title: 'iBon cookie',
    short: 'Paste the logged-in session cookie for the iBon ticketing site.',
    detailHtml: `
      <p>With this cookie, the bot can skip the iBon login flow.</p>
      <p><strong>How to get it in Chrome:</strong></p>
      <ol>
        <li>Log in to the iBon ticketing site (<code>tickets.ibon.com.tw</code>).</li>
        <li>Press <code>F12</code> to open Developer Tools.</li>
        <li>Open "Application" -> "Cookies" -> select <code>tickets.ibon.com.tw</code>.</li>
        <li>Find <code>ibonqware</code>.</li>
        <li>Copy the Value field and paste it here.</li>
      </ol>`,
  },
  funone_session_cookie: {
    title: 'FunOne cookie',
    short: 'Paste the logged-in session cookie for FunOne.',
    detailHtml: `
      <p>With this cookie, the bot can skip the FunOne login flow (<code>funone.com.tw</code>).</p>
      <p><strong>How to get it in Chrome:</strong></p>
      <ol>
        <li>Log in to the FunOne ticketing site.</li>
        <li>Press <code>F12</code> to open Developer Tools.</li>
        <li>Open "Application" -> "Cookies" -> select <code>funone.com.tw</code>.</li>
        <li>Find <code>ticket_session</code>.</li>
        <li>Copy the Value field and paste it here.</li>
      </ol>`,
  },
  fansigo_cookie: {
    title: 'FANSI GO cookie',
    short: 'Paste the logged-in FANSI GO session cookie. This can replace account/password login.',
    detailHtml: `
      <p>With this cookie, the bot logs in through the cookie instead of using an account and password.</p>
      <p><strong>How to get it in Chrome:</strong></p>
      <ol>
        <li>Log in to FANSI GO in your browser.</li>
        <li>Press <code>F12</code> to open Developer Tools.</li>
        <li>Open "Application" -> "Cookies" -> select <code>fansigo.com</code>.</li>
        <li>Find <code>FansiAuthInfo</code>.</li>
        <li>Copy the Value field and paste it here.</li>
      </ol>
      <p class="text-muted small mb-0">If both account credentials and a cookie are filled in, the bot uses the cookie first.</p>`,
  },
  idle_keyword: {
    title: 'System time pause keywords',
    short: 'Pause ticketing automatically at specific times. Format: HH:MM:SS, separated by semicolons.',
    detailHtml: `
      <p>When the system time matches any value in this field, the bot pauses automatically.</p>
      <p><strong>Format:</strong> <code>HH:MM:SS</code> (hour:minute:second). Separate multiple values with semicolons.</p>
      <p><strong>Example:</strong> <code>12:00:00;18:00:00</code> (pause every day at noon and 6 PM)</p>
      <p class="text-muted small mb-0">Use together with "resume keywords" for automatic ticketing schedules. For more details, open the "Time control" help section below.</p>`,
  },
  resume_keyword: {
    title: 'System time resume keywords',
    short: 'Resume ticketing automatically at specific times. Format: HH:MM:SS, separated by semicolons.',
    detailHtml: `
      <p>When the system time matches any value in this field, the bot resumes automatically.</p>
      <p><strong>Format:</strong> <code>HH:MM:SS</code> (hour:minute:second). Separate multiple values with semicolons.</p>
      <p><strong>Example:</strong> <code>10:00:00;14:00:00</code> (resume every day at 10 AM and 2 PM)</p>
      <p class="text-muted small mb-0">Use together with "pause keywords" for automatic ticketing schedules. For more details, open the "Time control" help section below.</p>`,
  },
  idle_keyword_second: {
    title: 'Second-based pause keywords',
    short: 'Pause ticketing automatically at specific seconds each minute. Format: SS, separated by semicolons.',
    detailHtml: `
      <p>When the <strong>seconds</strong> part of the system time matches a configured value, the bot pauses automatically. This triggers once every minute.</p>
      <p><strong>Format:</strong> second values only, <code>SS</code> (00-59). Separate multiple values with semicolons.</p>
      <p><strong>Example:</strong> <code>00;30</code> (pause at 0 and 30 seconds every minute)</p>
      <p class="text-muted small mb-0">Useful when you need precise second-level control. For more details, open the "Time control" help section below.</p>`,
  },
  resume_keyword_second: {
    title: 'Second-based resume keywords',
    short: 'Resume ticketing automatically at specific seconds each minute. Format: SS, separated by semicolons.',
    detailHtml: `
      <p>When the <strong>seconds</strong> part of the system time matches a configured value, the bot resumes automatically. This triggers once every minute.</p>
      <p><strong>Format:</strong> second values only, <code>SS</code> (00-59). Separate multiple values with semicolons.</p>
      <p><strong>Example:</strong> <code>05;35</code> (resume at 5 and 35 seconds every minute)</p>
      <p class="text-muted small mb-0">Useful when you need precise second-level control. For more details, open the "Time control" help section below.</p>`,
  },
  auto_reload_page_interval: {
    title: 'Auto reload interval',
    short: 'Automatic page reload interval in seconds. Set to 0 to disable.',
    detailHtml: `
      <p>Set how often the bot reloads the target page while waiting, in seconds.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Value</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr><td><code>0</code></td><td>Disable auto reload</td></tr>
          <tr><td><code>3</code></td><td>Reload every 3 seconds</td></tr>
          <tr><td><code>5</code> (recommended)</td><td>Reload every 5 seconds for a balance between speed and load</td></tr>
        </tbody>
      </table>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> Platforms such as TixCraft may throttle or restrict overly frequent reloads. Using less than 3 seconds is not recommended.</p>`,
  },
  tixcraft_soft_block_delay: {
    title: 'TixCraft soft-block delay',
    short: 'Custom wait time after the TixCraft-family white-screen soft block.',
    detailHtml: `
      <p>When the bot hits the TixCraft-family white-screen soft block, this value controls how long it waits before returning to the original page.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Value</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr><td>Empty</td><td>Keep the default randomized <code>240-420</code> seconds</td></tr>
          <tr><td><code>30</code></td><td>Always wait 30 seconds before retrying</td></tr>
          <tr><td><code>60</code></td><td>Always wait 60 seconds before retrying</td></tr>
        </tbody>
      </table>
      <p><strong>Scope:</strong> applies only to TixCraft, TeamEar, and Indievox. It does not change Ticketmaster behavior.</p>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> If you set it too short, the block may still be active and the retry can land on the same white screen again.</p>`,
  },
  tixcraft_allow_less_tickets: {
    title: 'Buy fewer TixCraft tickets if needed',
    short: 'Allow the TixCraft family to buy the largest available count below your configured ticket count.',
    detailHtml: `
      <p>This switch applies to TixCraft, TeamEar, Indievox, and Ticketmaster (the same ticketing backend). It is off by default to avoid buying fewer tickets than requested.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Status</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr><td>Off (default)</td><td>If you request 4 tickets but only 3, 2, and 1 are available, do not submit and wait for a reload</td></tr>
          <tr><td>On</td><td>If you request 4 tickets but only 3, 2, and 1 are available, select 3 and continue submitting</td></tr>
        </tbody>
      </table>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> Enable this only when you accept buying fewer tickets than originally configured.</p>`,
  },
  headless: {
    title: 'Headless mode',
    short: 'Run the browser in the background without showing a window. Default: off.',
    detailHtml: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>Status</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">Off (default)</span></td>
            <td>Show the browser window so you can observe the ticketing flow in real time</td>
          </tr>
          <tr>
            <td><span class="badge bg-warning text-dark">On</span></td>
            <td>Run completely in the background without showing a browser window and save system resources</td>
          </tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: 'Why is long-term use not recommended?',
        a: 'In headless mode, you cannot immediately notice or handle situations that need manual intervention, such as visual captchas or unexpected pages. It is better to confirm the workflow in normal mode first.'
      }
    ],
  },
  verbose: {
    title: 'Verbose logs',
    short: 'Show detailed runtime logs in the output window. Default: off.',
    detailHtml: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>Status</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">Off (default)</span></td>
            <td>Show only important messages such as success and errors</td>
          </tr>
          <tr>
            <td><span class="badge bg-info text-dark">On</span></td>
            <td>Print detailed information for each step, including timestamps</td>
          </tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">Tip: enable this when troubleshooting. Turn it off during normal runs to reduce log noise.</p>`,
  },
  discord_webhook_url: {
    title: 'Discord webhook',
    short: 'Send a Discord notification after ticketing succeeds.',
    detailHtml: `
      <p>Enter a Discord webhook URL. The bot sends a notification automatically when ticketing succeeds.</p>
      <p><strong>How to get the webhook URL:</strong></p>
      <ol>
        <li>In Discord, open the target channel and choose Edit Channel.</li>
        <li>Open "Integrations" -> "Webhooks" -> "New Webhook".</li>
        <li>Copy the webhook URL and paste it here.</li>
      </ol>
      <p><strong>Example format:</strong><br>
      <code>https://discord.com/api/webhooks/123456789/abcdef...</code></p>
      <p class="text-muted small mb-0">If left empty, Discord notifications are disabled.</p>`,
  },
  telegram_bot_token: {
    title: 'Telegram bot token',
    short: 'Token for the Telegram bot that sends notifications.',
    detailHtml: `
      <p>Enter the Telegram bot token. When ticketing succeeds, the bot sends notifications through this Telegram bot.</p>
      <p><strong>How to get the token:</strong></p>
      <ol>
        <li>Search for <code>@BotFather</code> in Telegram.</li>
        <li>Send <code>/newbot</code> to create a new bot.</li>
        <li>Follow the prompts, then copy the issued token.</li>
      </ol>
      <p><strong>Format:</strong> <code>123456789:ABCdefGHI-jklMNO...</code></p>
      <p class="text-muted small mb-0">If left empty, Telegram notifications are disabled.</p>`,
  },
  telegram_chat_id: {
    title: 'Telegram chat ID',
    short: 'Telegram chat IDs that receive notifications. Separate multiple IDs with commas.',
    detailHtml: `
      <p>Enter the Telegram chat ID that should receive notifications.</p>
      <p><strong>How to get the chat ID:</strong></p>
      <ol>
        <li>Send any message to the bot you created.</li>
        <li>Open <code>https://api.telegram.org/bot{TOKEN}/getUpdates</code> in your browser.</li>
        <li>Find the value of <code>chat.id</code> in the JSON response.</li>
      </ol>
      <p><strong>Multiple recipients:</strong> Separate multiple IDs with commas, for example: <code>123456789, 987654321</code></p>`,
  },
  server_port: {
    title: 'Settings UI port',
    short: 'HTTP listening port for the local settings UI. Default: 16888.',
    detailHtml: `
      <p>Set the HTTP listening port used by the Tickets Hunter settings page.</p>
      <p>Default value: <code>16888</code>. Default URL: <code>http://localhost:16888</code></p>
      <p>If the default port is already used by another application, choose any value between 1024 and 65535.</p>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> After changing the port, restart the program and reconnect using the new port.</p>`,
    faq: [
      {
        q: 'How do I reconnect after changing the port?',
        a: 'After restarting, open <code>http://localhost:{new port}</code> in your browser.'
      }
    ],
  },
  ocr_captcha_enable: {
    title: 'OCR captcha recognition',
    short: 'Enable OCR-based text captcha recognition. Default: off.',
    detailHtml: `
      <p>When enabled, the bot uses an OCR model to recognize text captchas automatically and fill in the answer.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Status</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr><td><span class="badge bg-secondary">Off</span></td><td>Pause on captcha and wait for manual input</td></tr>
          <tr><td><span class="badge bg-success">On</span></td><td>Recognize the captcha and fill it automatically</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">Currently supports text captchas on platforms such as TixCraft, iBon, and KHAM.</p>`,
    faq: [
      {
        q: 'What if the recognition result is inaccurate?',
        a: 'Try disabling OCR and entering the captcha manually, or check whether a custom model is available for that platform.'
      }
    ],
  },
  ocr_captcha_force_submit: {
    title: 'OCR auto-submit',
    short: 'Submit immediately after OCR fills the captcha, without waiting for confirmation. Default: off.',
    detailHtml: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>Status</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">Off (default)</span></td>
            <td>Fill the OCR result, but still wait for manual confirmation before submitting</td>
          </tr>
          <tr>
            <td><span class="badge bg-warning text-dark">On</span></td>
            <td>Submit immediately after OCR finishes, without waiting for any confirmation</td>
          </tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: 'What happens if OCR is wrong and auto-submit is enabled?',
        a: 'Most platforms simply reject the captcha and let the bot try again. It usually does not cause a permanent failure, but it does waste one attempt. Enable this only after you are confident in the recognition quality.'
      }
    ],
  },
  user_guess_string: {
    title: 'Custom answer dictionary',
    short: 'Pre-fill possible answers for text verification questions. Separate multiple answers with semicolons.',
    detailHtml: `
      <p>When the system detects a verification question that requires a text answer, it tries the answers listed here first.</p>
      <p><strong>Format:</strong> separate multiple answers with semicolons (<code>;</code>)</p>
      <p><strong>Example:</strong> <code>Answer A;Answer B;Correct Answer</code></p>
      <p>If this field is empty and "auto-guess options" is enabled, the system tries to infer the answer automatically.</p>
      <p class="text-muted small mb-0">Tip: providing known correct answers can significantly increase the success rate of verification.</p>`,
    faq: [
      {
        q: 'Do answers have priority order?',
        a: 'Yes. The system tries them in the order they are listed. Put the most likely answer first.'
      }
    ],
  },
  ticket_number: {
    title: 'Tickets',
    short: 'Number of tickets to purchase each time. Range: 1-10.',
    detailHtml: `
      <p>Set how many tickets the bot should try to select in each purchase attempt.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Quantity</th><th>Typical use</th></tr></thead>
        <tbody>
          <tr><td>1 ticket</td><td>Solo purchase, highest success rate</td></tr>
          <tr><td>2 tickets</td><td>Two people attending together</td></tr>
          <tr><td>3-4 tickets</td><td>Group purchase. Be aware that higher quantities increase the chance of failure when only a few seats remain.</td></tr>
        </tbody>
      </table>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> The higher the ticket count, the higher the chance that the purchase fails because not enough tickets are available. Use the minimum quantity you actually need.</p>`,
  },
  refresh_datetime: {
    title: 'Refresh at specific time',
    short: 'Wait until a specific date and time before starting the ticketing flow.',
    detailHtml: `
      <p>Set the exact date and time when the bot should start trying to get tickets. This is useful when sales open at a specific moment.</p>
      <p><strong>Format:</strong> <code>YYYY/MM/DD HH:MM:SS</code></p>
      <p>Example: <code>2025/12/25 10:00:00</code></p>
      <p>Before the target time, the bot waits and checks the time once per second. As soon as the target time is reached, it starts refreshing and ticketing immediately.</p>
      <p class="text-muted small mb-0">Tip: set this 1-2 seconds before the official sale time to compensate for network and processing delay.</p>`,
    faq: [
      {
        q: 'What happens if I leave it empty?',
        a: 'The bot starts ticketing immediately after launch.'
      },
      {
        q: 'What if I start the program after the configured time has already passed?',
        a: 'The bot starts immediately. It does not wait for another cycle.'
      }
    ],
  },
  date_select_mode: {
    title: 'Date selection order',
    short: 'Choose how available dates are selected when date keywords are empty or date fallback is used.',
    detailHtml: `
      <p>When "Date keywords" is empty, or when "Date fallback" is enabled, this setting determines which date is selected.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Option</th><th>Behavior</th><th>Typical use</th></tr></thead>
        <tbody>
          <tr><td><code>from top to bottom</code></td><td>Select the topmost date in the list</td><td>Prefer the earliest available show</td></tr>
          <tr><td><code>from bottom to top</code></td><td>Select the bottommost date in the list</td><td>Prefer the latest available show</td></tr>
          <tr><td><code>center</code></td><td>Select a date near the middle of the list</td><td>Spread selection away from the top and bottom extremes</td></tr>
          <tr><td><code>random</code></td><td>Select a random available date</td><td>Any session is acceptable</td></tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: 'Does this still matter when date keywords are configured?',
        a: 'Yes. If multiple dates match the keywords, this order decides which one is chosen first. It is also used when date fallback is enabled.'
      }
    ],
  },
  area_select_mode: {
    title: 'Area selection order',
    short: 'Choose how available areas are selected when area keywords are empty or area fallback is used.',
    detailHtml: `
      <p>When "Area keywords" is empty, or when "Area fallback" is enabled, this setting determines which area is selected.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Option</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr><td><code>from top to bottom</code></td><td>Select the topmost area in the list</td></tr>
          <tr><td><code>from bottom to top</code></td><td>Select the bottommost area in the list</td></tr>
          <tr><td><code>center</code></td><td>Select an area near the middle of the list</td></tr>
          <tr><td><code>random</code></td><td>Select a random available area</td></tr>
        </tbody>
      </table>
      <p class="text-muted small mb-0">Tip: on many ticketing sites, area lists are sorted from more expensive / better seats to cheaper / farther seats, so <code>from top to bottom</code> usually means better seats first.</p>`,
  },
  keyword_exclude: {
    title: 'Exclude keywords',
    short: 'Specify dates or areas that must be skipped even if they match other rules.',
    detailHtml: `
      <p>Set keywords for dates or areas that you do not want to select. Matching options are skipped even if they also satisfy other selection rules.</p>
      <p>The format is the same as the date/area keyword fields. Use semicolons (<code>;</code>) to separate multiple conditions:</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Example</th><th>Effect</th></tr></thead>
        <tbody>
          <tr><td><code>Sold Out</code></td><td>Skip options marked as sold out</td></tr>
          <tr><td><code>Wheelchair;Accessible</code></td><td>Skip any option containing "Wheelchair" or "Accessible"</td></tr>
          <tr><td><code>12/24;12/25</code></td><td>Skip sessions on 12/24 and 12/25</td></tr>
        </tbody>
      </table>`,
    faq: [
      {
        q: 'If both area keywords and exclude keywords match, which one wins?',
        a: 'Exclude keywords win. If an option matches both "select" and "exclude" rules, the bot skips it.'
      }
    ],
  },
  area_auto_fallback: {
    title: 'Area fallback',
    short: 'When no area keywords match, automatically select another available area. Default: off.',
    detailHtml: `
      <table class="table table-sm table-bordered mb-3">
        <thead><tr><th>Status</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">Off (default)</span></td>
            <td>Strict mode. If none of the area keywords match, <strong>stop selecting</strong> and wait for the next retry cycle.</td>
          </tr>
          <tr>
            <td><span class="badge bg-success">On</span></td>
            <td>Fallback mode. If no keyword matches, automatically select the first available area based on the configured area selection order.</td>
          </tr>
        </tbody>
      </table>
      <p><strong>Recommended use:</strong> If you specified a particular area such as a front row or standing zone, <strong>keep this off</strong> to avoid unwanted restricted-view or accessible-only areas.</p>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> Area fallback may select restricted-view seats, wheelchair seats, or other unintended sections. Use carefully.</p>`,
    faq: [
      {
        q: 'Can date fallback and area fallback be configured independently?',
        a: 'Yes. They are separate switches. You can allow automatic date selection while keeping areas strict, or the other way around.'
      },
      {
        q: 'Why is this disabled by default?',
        a: 'For safety. Automatic fallback may choose wheelchair seats, restricted-view seats, or higher-priced sections that you did not intend to buy.'
      }
    ],
  },
  show_timestamp: {
    title: 'Show timestamps',
    short: 'Prefix each output line with a [HH:MM:SS] timestamp.',
    detailHtml: `
      <p>When enabled, each output line includes a timestamp so you can track the timing of each step in the ticketing flow.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Status</th><th>Output format</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">Off (default)</span></td>
            <td><code>[DATE] found: 2024-12-31</code></td>
          </tr>
          <tr>
            <td><span class="badge bg-success">On</span></td>
            <td><code>[09:30:15] [DATE] found: 2024-12-31</code></td>
          </tr>
        </tbody>
      </table>
      <p class="mb-0 text-muted small">Useful for reviewing logs after ticketing and comparing how long each step took.</p>`,
  },
  reset_browser_interval: {
    title: 'Browser restart interval (seconds)',
    short: 'Restart the browser periodically. Set to 0 to disable.',
    detailHtml: `
      <p>Set how many seconds the browser should run before restarting automatically. Use <code>0</code> (default) to disable this feature.</p>
      <ul>
        <li>Minimum value: <strong>20 seconds</strong> (any lower value is adjusted to 20 automatically)</li>
        <li>Set <code>0</code> to disable auto-restart</li>
      </ul>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> The automatic restart behavior is not fully implemented in the main program yet. Keeping the default value <code>0</code> is recommended.</p>`,
  },
  proxy_server_port: {
    title: 'Proxy server',
    short: 'Set the proxy server address in IP:Port format. Leave empty to connect directly.',
    detailHtml: `
      <p>Set the proxy server used by the browser for network connections. Leave it empty to connect directly.</p>
      <p><strong>Format:</strong> <code>IP:Port</code></p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Example</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td><code>127.0.0.1:8080</code></td><td>Local proxy such as Clash or v2ray</td></tr>
          <tr><td><code>192.168.1.1:3128</code></td><td>LAN proxy server</td></tr>
          <tr><td>(blank)</td><td>No proxy, connect directly</td></tr>
        </tbody>
      </table>
      <p class="mb-0 text-muted small">If set, the browser launches with the <code>--proxy-server=</code> argument automatically.</p>`,
  },
  disable_adjacent_seat: {
    title: 'Allow non-adjacent seats',
    short: 'Accept seats that are not next to each other to improve the chance of success.',
    detailHtml: `
      <p>Control whether the bot accepts seat combinations that are not adjacent.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Status</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">Off (default)</span></td>
            <td>Select adjacent seats only</td>
          </tr>
          <tr>
            <td><span class="badge bg-success">On</span></td>
            <td>Allow non-adjacent seats to increase the chance of getting tickets</td>
          </tr>
        </tbody>
      </table>
      <p><strong>Supported platforms:</strong> iBon, Ticket, KHAM, Ticketmaster</p>
      <p class="mb-0 text-muted small">Useful when multiple people are attending together but sitting together is not required.</p>`,
  },
  hide_some_image: {
    title: 'Hide some images',
    short: 'Block non-essential resources to speed up page loading.',
    detailHtml: `
      <p>When enabled, the bot blocks some non-essential resources so the ticketing page can load faster.</p>
      <p><strong>Blocked resource types:</strong></p>
      <ul>
        <li>Web fonts (<code>.woff</code>)</li>
        <li>Site icons (<code>.ico</code>)</li>
        <li>Some event images</li>
      </ul>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> The page may look incomplete after enabling this, but the ticketing flow should still work. If your network speed is already normal, you usually do not need this.</p>`,
  },
  block_facebook_network: {
    title: 'Block Facebook network requests',
    short: 'Block Facebook tracking scripts and related requests to reduce extra network traffic.',
    detailHtml: `
      <p>When enabled, the bot blocks all Facebook-related network requests.</p>
      <p><strong>Blocked domains:</strong></p>
      <ul>
        <li><code>*.facebook.com/*</code></li>
        <li><code>*.fbcdn.net/*</code></li>
      </ul>
      <p>Some ticketing sites embed Facebook tracking scripts. If those scripts slow down the page, enabling this option may improve loading speed.</p>
      <p class="mb-0 text-muted small">This can be used together with "Hide some images". The effects are complementary.</p>`,
  },
  auto_guess_options: {
    title: 'Auto-guess verification options',
    short: 'Automatically infer answers for multiple-choice verification questions on supported platforms.',
    detailHtml: `
      <p>When enabled, the bot tries to infer the correct answer for multiple-choice verification questions based on the text of the prompt.</p>
      <p><strong>Typical question types:</strong></p>
      <ul>
        <li>Math question, such as "1 + 1 = ?"</li>
        <li>Geography question, such as "Which city is Taipei 101 in?"</li>
        <li>General knowledge or event-related questions</li>
      </ul>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Status</th><th>Behavior</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-secondary">Off (default)</span></td>
            <td>Do not guess automatically. Wait for manual selection.</td>
          </tr>
          <tr>
            <td><span class="badge bg-success">On</span></td>
            <td>Infer and select an answer automatically to speed up the flow.</td>
          </tr>
        </tbody>
      </table>
      <p><strong>Supported platforms:</strong> KKTIX, TixCraft, iBon</p>
      <p class="text-warning-emphasis small mb-0"><strong>Note:</strong> Accuracy depends on the question type. A wrong guess can cause the purchase to fail, so test carefully before relying on it.</p>`,
  },
  ocr_captcha_image_source: {
    title: 'OCR image source',
    short: 'Choose whether captcha images are captured from canvas (default) or NonBrowser.',
    detailHtml: `
      <p>Set how the program captures captcha images for OCR.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Option</th><th>Description</th></tr></thead>
        <tbody>
          <tr>
            <td><code>canvas</code> (default)</td>
            <td>Capture the captcha image directly from the page through the JavaScript Canvas API. Suitable for most cases.</td>
          </tr>
          <tr>
            <td><code>NonBrowser</code></td>
            <td>Launch a separate NonBrowser window to capture the captcha image. This is intended for use with external captcha tools.</td>
          </tr>
        </tbody>
      </table>
      <p class="mb-0 text-muted small">In most cases, keep <code>canvas</code>. Switch to <code>NonBrowser</code> only if the main browser cannot capture the captcha correctly.</p>`,
  },
  ocr_captcha_use_universal: {
    title: 'Use universal OCR model',
    short: 'Use the built-in universal OCR model (99%+ accuracy). Disable it to fall back to the official ddddocr model.',
    detailHtml: `
      <p>Select which OCR model is used for captcha recognition.</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Status</th><th>Model</th><th>Accuracy</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge bg-success">Enabled (default)</span></td>
            <td>Universal self-trained model (<code>assets/model/universal/</code>)</td>
            <td>99%+</td>
          </tr>
          <tr>
            <td><span class="badge bg-secondary">Disabled</span></td>
            <td>Official ddddocr model</td>
            <td>Lower</td>
          </tr>
        </tbody>
      </table>
      <p><strong>Supported platforms:</strong> TixCraft, iBon, KHAM</p>
      <p class="mb-0 text-muted small">Keeping this enabled is recommended. If you see abnormal recognition results, try disabling it and test again.</p>`,
  },
  remote_url: {
    title: 'Settings UI URL',
    short: 'Auto-generated URL for accessing the settings UI. Read-only.',
    detailHtml: `
      <p>This is the access URL for the settings UI. It is generated automatically from the configured "Settings UI port".</p>
      <p><strong>Format:</strong> <code>http://127.0.0.1:{Port}/</code></p>
      <p>For example, if the port is <code>16888</code>, the URL becomes <code>http://127.0.0.1:16888/</code>.</p>
      <p><strong>This field is read-only.</strong> Any manual changes will be overwritten the next time settings are saved.</p>
      <p class="mb-0 text-muted small">If another script or tool needs to access the settings API, you can copy this URL and use it directly.</p>`,
  },
};

function buildLocalizedHelpEntry(baseContent, localizedMeta, defaultTitle) {
  const meta = localizedMeta || {
    title: defaultTitle,
    short: 'Configuration help',
    detail: 'Refer to the linked documentation for details.',
  };

  return {
    title: meta.title,
    short: meta.short,
    detail: meta.detailHtml || `<p>${meta.detail}</p>`,
    faq: meta.faq || [],
    link: meta.link || baseContent.link || null,
  };
}

const HELP_CONTENT_EN = Object.fromEntries(
  Object.entries(HELP_CONTENT).map(([key, value]) => [key, buildLocalizedHelpEntry(value, HELP_CONTENT_EN_META[key], key)])
);

window.HELP_CONTENT = HELP_CONTENT;
window.HELP_CONTENT_MAP = {
  'zh-TW': HELP_CONTENT,
  en: HELP_CONTENT_EN,
};
