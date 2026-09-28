# CLAUDE.md

本檔提供給 AI 編碼工具（Claude Code、Cursor、Copilot、Aider 等）與外部貢獻者，
說明 Tickets Hunter 的架構約定、程式碼規範與提交流程。

**專案**：Tickets Hunter — 多平台搶票自動化系統
**授權**：GNU GPL
**貢獻流程**：見 [CONTRIBUTING.md](CONTRIBUTING.md)

> 本專案是一項 AI 輔助軟體工程實驗，程式碼主要透過自然語言指令與 AI 協作產生。
> 歡迎 fork 後用不同的 AI 工具實驗，但請遵守下方的法律與倫理邊界。

---

## 法律與倫理邊界（優先於所有技術規範）

- 本軟體僅供教育與研究用途，完整條款見 [LEGAL_NOTICE.md](LEGAL_NOTICE.md)。
- 禁止用於加價轉售、商業牟利或惡意囤票。
- 台灣地區禁止用於文化創意產業發展法涵蓋之票券（演唱會、戲劇、展覽等），
  詳見 README 的法律聲明段落。
- **不得實作自動付款。** 偵測到付款頁面只發通知，付款由使用者手動完成。
- 單純為了繞過某個平台風控的 PR，不會合併。
- 不得在記錄、錯誤訊息或提交內容中輸出密碼、Cookie 或 webhook URL。

---

## 開始之前（AI 起手流程）

接到任務時依序進行：

1. **確認有對應的 Issue。** 每個 PR 都必須先有 Issue，且 PR 內容第一行寫 `Closes #編號`
   （只處理一部分則寫 `Refs #編號`）。沒有 Issue 就先協助使用者開一個，寫明問題、
   調查過程與根因。PR 內容有自動檢查，沒有連結 Issue 會被標記失敗。詳見 [CONTRIBUTING.md](CONTRIBUTING.md)。
2. **讀邊界與範本。** 先讀 `docs/02-development/code-boundaries.md`，再找**同類功能在其他平台的
   既有實作**當範本，例如表單填值可參考 `platforms/ibon.py` 的 `nodriver_ibon_card_vaildate`。
   多數問題已經在某個平台解過一次。
3. **修改。** 遵守下方的程式碼規範與「常見陷阱」。
4. **驗證。** 執行「建置與測試指令」，並在 PR 寫明實際驗證過的活動與頁面。

---

## 專案概要

Python + zendriver 驅動 Chrome，支援台灣與港澳／澳洲共 17 個票務平台。
發行版以 PyInstaller 打包，由 GitHub Actions 建置 Windows 與 macOS（Apple Silicon）兩個版本。

### 環境設定

```bash
pip install -r requirement.txt       # 執行期相依套件
python src/settings.py               # 開啟設定介面
```

需要 Chrome 145 以上。`src/settings.json` 是使用者的私人設定檔，已列入 `.gitignore`，
請勿提交，也不要在程式碼或記錄中輸出其內容。

### 建置與測試指令

```bash
python -m py_compile src/nodriver_tixcraft.py   # 語法檢查（修改過的檔案都要跑）
python build_scripts/build_local.py             # 打包並驗證能啟動（改動相依套件、.spec 或新增 import 時）
```

宣告工作完成前必須實際執行上述指令，不得僅憑閱讀程式碼推斷結果。

測試套件由維護者另行維護，公開庫不含 `tests/`。外部貢獻以 `py_compile` 與實機驗證為準，
平台邏輯的改動請在 PR 說明實際跑過哪個活動、走到哪一頁。

---

## 架構

- 所有瀏覽器自動化使用 **zendriver**（nodriver 的活躍 fork，支援 Chrome 145+）。
  寫法為 `import zendriver as uc`；檔名維持 `nodriver_*.py` 不變（模組名稱，非套件名稱）。
- 入口點為 `src/nodriver_tixcraft.py`（主迴圈 + URL 路由），各平台邏輯拆分於 `src/platforms/*.py`。
- `src/nodriver_common.py` 為共用瀏覽器基礎設施（DOM 工具、暫停機制、Cloudflare、瀏覽器初始化）。
- `src/util.py` 為所有平台共用的純工具函式。
- 所有執行期行為由 `settings.json` 控制。禁止把使用者可能需要調整的值寫死在程式碼中。
- 新增設定鍵必須同時在 `src/settings.py` 的設定綱要中宣告。

### 目錄結構

```
src/
  nodriver_tixcraft.py   主迴圈與 URL 路由（入口點）
  nodriver_common.py     共用瀏覽器基礎設施（DOM、暫停、Cloudflare、瀏覽器初始化）
  util.py                共用純工具函式（文字比對、關鍵字解析、DebugLogger）
  settings.py            設定綱要與網頁設定介面
  platforms/*.py         各平台獨立模組
  www/                   設定介面前端資源
docs/                    技術文件（01 入門 ~ 07 部署）
guide/                   使用者手冊
build_scripts/           PyInstaller 打包腳本
```

### 依賴方向

固定如下，禁止反向引用（完整的模組職責、命名慣例與禁止模式見
`docs/02-development/code-boundaries.md`）：

```
nodriver_tixcraft  ->  platforms/*  ->  nodriver_common  ->  util / settings
```

### 平台與模組對照

| 模組 | 平台 |
|------|------|
| `platforms/tixcraft.py` | 拓元 TixCraft、Ticketmaster SG、添翼 Teamear、獨立音樂 Indievox |
| `platforms/kktix.py` | KKTIX |
| `platforms/ibon.py` | ibon（購票 / 旅遊 / 會展） |
| `platforms/ticketplus.py` | 遠大 TicketPlus |
| `platforms/kham.py` | 寬宏 KHAM、年代售票、UDN 售票網 |
| `platforms/famiticket.py` | 全網 FamiTicket |
| `platforms/cityline.py` | Cityline 買飛 |
| `platforms/hkticketing.py` | HKTicketing 快達票、澳門銀河、Ticketek |
| `platforms/fansigo.py` | FANSI GO |
| `platforms/funone.py` | FunOne |
| `platforms/facebook.py` | Facebook 登入輔助 |

---

## zendriver 關鍵差異（必讀）

完整破壞性變更清單見 `docs/06-api-reference/zendriver_api_guide.md`。最易踩的兩條：

- **禁止 `Config(lang=...)`** — zendriver 的 validator 會擋掉，改用 `browser_args`。
- `tab.remove_handlers(event)` 會移除**全部**同類型 handler（舊 nodriver API 是逐一移除）。

### CDP 使用原則

- **優先使用 CDP 原生方法** — 直接與瀏覽器底層溝通，較不易觸發網站的自動化偵測。
- **JavaScript 僅作輔助** — 只在 CDP 實作超過 50 行、而 JS 少於 10 行時才使用。
- **Shadow DOM 必須用 CDP `DOM.getDocument(pierce=True)`**，JS `querySelector` 無效；
  Cloudflare Turnstile 同樣如此，`document.querySelector` 找不到。
- `tab.evaluate()` 的回傳值在 zendriver 中**已是實際值**，新程式碼不要再套 `parse_nodriver_result()`。
  既有呼叫為無害的 pass-through 遺留，正逐步移除，看到不代表可仿效。
- 傳給瀏覽器的 Promise 主體要包成 IIFE（`(() => { ... })()`）。裸的箭頭函式運算式
  只會回傳函式物件本身，Promise 主體永遠不會執行，等待會靜默失效。

---

## 常見陷阱

外部 PR 最常踩到的問題。每一條都曾在實際的 PR 或 bug 中出現過。

- **`tab.query_selector()` 找不到元素時回傳 `None`，不會拋例外。** 用 `try/except` 判斷元素是否存在
  永遠判斷不出來，要檢查回傳值。
- **`click()` 在按鈕與 checkbox 上不會拋例外。** 呼叫了不代表生效，點選後要驗證狀態確實改變
  （已勾選、彈窗已關閉、頁面已前進），沒變才走 fallback。
- **`tab.reload()` 送出重新載入指令後立刻返回，不等頁面載入完成。** 重新整理後馬上讀 DOM 會讀到空頁。
- **主迴圈約每 50 毫秒跑一輪，同一個動作會被反覆呼叫。** 送出、填值這類有副作用的動作必須有
  防重入狀態（沿用各平台模組既有的 `_state` dict，不要新增模組層級全域變數），失敗也要有重試上限，
  否則錯誤的值會被每秒送出數十次。
- **等待迴圈用 `sleep_with_pause_check` / `asyncio_sleep_with_pause_check`**（`nodriver_common.py`），
  不要用 `tab.sleep()`，否則使用者按暫停無效。
- **填寫輸入框用 `nodriver_common.CONST_NATIVE_INPUT_SETTER_JS`**，不要自己重寫 native setter。
  要檢查它的回傳值，填值失敗就不要送出。
- **`querySelector('A, B')` 回傳文件順序中第一個符合的元素**，不是「優先 A、其次 B」。
  需要優先順序就分兩次查詢。
- **設定鍵可能被多個平台共用**，例如 `contact.credit_card_prefix` 同時被 ibon、TicketPlus、寬宏讀取。
  改動欄位長度、格式或語意之前，先搜尋所有讀取它的平台。
- **自動辨識沒把握時就不要動作。** 無法確認彈窗或欄位的身分時，交還使用者手動處理，
  不要把帳號或卡號填進猜測的欄位。

---

## 程式碼規範

- **除錯輸出一律使用 DebugLogger**，禁止 `if verbose: print()`：

  ```python
  debug = util.create_debug_logger(config_dict)
  debug.log("[TAG] message")
  ```

  原因：DebugLogger 統一處理 verbose 開關與時間戳。

- **`.py` 檔案中禁止使用 emoji。** Windows 主控台預設 cp950，遇到 emoji 會直接編碼失敗。

- **撰寫任何新工具函式前先搜尋 `src/util.py`** — 該函式極可能已存在。
  `util.py` 為所有平台共用，變更簽章或回傳型別前務必評估跨平台影響。

- `util.is_text_match_keyword(keyword, text)` — 第一個參數是 keyword，第二個才是 text。
  Keyword 格式：`"\"kw\""` = 完全符合、`"\"a\",\"b\""` = OR、`"\"a b\""` = AND。

- 套用排除關鍵字前先確認文字非空。比對函式對空字串會回報為相符，
  導致取不到標籤的項目被當成已排除，連帶從回退清單中消失。

- 顯示給使用者的訊息用設定項的 UI 名稱，不用內部鍵名。

- 發行版以 PyInstaller 打包成 Windows 與 macOS 兩個版本。避免引入在 PyInstaller 下會失效、
  需要系統函式庫或只支援單一作業系統的相依套件；新相依套件必須在 `requirement.txt` 中固定版本。

---

## 語言

- 文件、註解與面向使用者的訊息一律使用**繁體中文（台灣用語）**，不使用簡體中文或中國慣用詞。
  常見對照：偵測（非檢測）、比對／相符（非匹配）、記錄（非日誌）、字元（非字符）、
  非同步（非異步）、協定（非協議）、重新導向（非重定向）、整合（非集成）。
- `.py` 新增的註解優先使用英文，並盡量引用階段編號，例如 `# Stage 4: date selection`。
  既有的中文註解不必改寫。emoji 禁令不受此條影響。
- 程式碼識別字、log 標籤、commit 訊息維持英文。
- **例外**：設定介面既有的欄位名稱以 UI 實際文字為準，不因用語偏好改寫。
  目前 UI 使用「刷新」（如「自動刷新頁面間隔」）與「無圖形界面模式」，
  文件提到這些設定時必須沿用，否則使用者在介面上找不到對應欄位。
- 「代碼」只有在指 source code 時才寫成「程式碼」。`優惠代碼`、`會員代碼`、
  `促銷代碼`、`按鍵代碼` 等指的是代號，維持「代碼」。

---

## 12 階段搶票標準

所有平台實作遵循同一組階段順序，禁止改動階段編號與順序：

```
1 環境初始化    2 身分認證      3 頁面監控      4 日期選擇
5 區域選擇      6 票數設定      7 驗證碼處理    8 表單填寫
9 同意條款     10 訂單送出     11 排隊與付款   12 錯誤處理
```

主迴圈依函式名稱路由，新增平台時務必沿用下列字尾：

| 階段 | 字尾 |
|------|------|
| 2. 身分驗證 | `_signin` / `_login` |
| 3. 頁面監控 | `_main` |
| 4. 日期選擇 | `_date_auto_select` |
| 5. 區域選擇 | `_area_auto_select` |
| 6. 票數設定 | `_assign_ticket_number` |
| 7. CAPTCHA | `_verify` / `_captcha` |
| 8. 表單填寫 | `_auto_fill` / `_keyin` |
| 9. 條款同意 | `_agree` |
| 10. 訂單送出 | `_confirm_order` |
| 11. 排隊／付款 | `_check_queue_status` / `_booking` |

完整規格見 `docs/02-development/ticket_automation_standard.md`。
新增平台時，先閱讀 `docs/04-implementation/platform-examples/tixcraft-reference.md` 作為範本，
並依 `docs/02-development/code-boundaries.md` 第 10 節的四個步驟註冊模組。

---

## 測試

- 測試套件由維護者另行維護，公開庫不含 `tests/`。
- 修改過的檔案必須通過 `python -m py_compile`。
- 平台自動化邏輯高度依賴即時 DOM，難以事先寫測試；
  TDD 僅適用於 `util.py` / `settings.py` 的純函式。

---

## 提交規範

使用 [Conventional Commits](https://www.conventionalcommits.org/)，**不含 emoji**：

```
<type>(<scope>): <description>
```

| Type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | 錯誤修復 |
| `docs` | 文件更新 |
| `refactor` | 重構 |
| `perf` | 效能改善 |
| `test` | 測試 |
| `chore` | 維護工作 |

分支命名：`feature/`、`fix/`、`docs/`、`refactor/`。

### 提交前檢查清單

- [ ] PR 內容第一行已寫 `Closes #編號`（或 `Refs #編號`），且該 Issue 記錄了根因
- [ ] 所有修改過的檔案通過 `py_compile`
- [ ] 送出、填值等有副作用的動作有防重入狀態與重試上限
- [ ] `.py` 檔案中沒有 emoji
- [ ] 新的除錯輸出使用 `DebugLogger`
- [ ] 已確認 `src/util.py` 中是否已有可重用的函式
- [ ] 若修改 `util.py`，已評估跨平台影響
- [ ] 新增的設定鍵已在 `src/settings.py` 中宣告
- [ ] 沒有提交 `settings.json`、Cookie、帳號密碼或瀏覽器 profile
- [ ] Commit 訊息遵循 Conventional Commits 且不含 emoji
- [ ] 新增的中文內容為繁體（台灣用語）

---

## 文件索引

| 資源 | 路徑 |
|------|------|
| 專案概觀與安裝 | `docs/01-getting-started/` |
| 開發指南與函式索引 | `docs/02-development/` |
| **程式碼邊界（必讀）** | `docs/02-development/code-boundaries.md` |
| 測試執行指南 | `docs/02-development/testing_execution_guide.md` |
| 12 階段機制詳解 | `docs/03-mechanisms/` |
| 各平台實作範例 | `docs/04-implementation/platform-examples/` |
| zendriver API 指南 | `docs/06-api-reference/zendriver_api_guide.md` |
| PyInstaller 打包 | `docs/07-deployment/` |
| macOS 使用與自行打包 | `guide/macos.md` |
| 使用者手冊 | `guide/README.md` |
