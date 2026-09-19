# 機制 15：Cloudflare Turnstile 偵測與處理

**文件說明**：說明搶票系統的 Cloudflare Turnstile 偵測機制與 CDP Shadow DOM 穿透點擊實作
**最後更新**：2026-09-10

---

## 概述

當票務平台（KKTIX、TixCraft 等）啟用 Cloudflare 保護時，會出現 Turnstile 驗證
（「驗證您是人類」checkbox）。程式能自動偵測並點擊 checkbox 通過驗證。

## 核心發現

### Turnstile iframe 對 JavaScript 不可見

Cloudflare Turnstile 的 iframe 透過特殊機制注入頁面，**標準 DOM 查詢找不到 iframe**：

```javascript
// iframe 一律查不到：
document.querySelector('iframe[src*="challenges.cloudflare.com"]')  // null
document.querySelectorAll('iframe')  // 只找到無關的 iframe

// 容器則視平台而定，不能當作判斷依據：
document.querySelector('.cf-turnstile')   // KKTIX 登入頁查得到，Cityline 登入頁是 null
```

**容器查得到不代表能拿它定位**。KKTIX 登入頁的 `.cf-turnstile` 是表單全寬
（實測 580x72），widget 本身只有 300x65，用容器座標會點在空白處。座標一律取自
iframe 的 box model。也不要拿容器 class 當「有沒有挑戰」的判斷依據——見下方
「驗證邏輯」，點擊後的成功判定本來就不該先分類挑戰形態。

但 **CDP 協議可以找到**：

| 方法 | 能否找到 |
|------|----------|
| `document.querySelector()` | ❌ |
| `shadowRoot` 搜尋 | ❌ |
| CDP `Target.getTargets()` | ✅ |
| CDP `DOM.getDocument(pierce=True)` | ✅ |

### `verify_cf()` 無效

zendriver 繼承自 nodriver 的 `verify_cf()` 使用 OpenCV 模板匹配截圖來找 checkbox。
在實際 Cloudflare 頁面上**完全無效**（返回 None，checkbox 不會被點擊）。

## 架構設計

### 偵測層級（`detect_cloudflare_challenge()`）

```
Layer 1: CDP Target.getTargets()     ← 最可靠，能找到隱形 iframe
Layer 2: JS querySelector             ← 快速，部分場景有效
Layer 3: HTML 關鍵字                   ← 全頁面攔截型 CF 的備用偵測
```

### 處理策略（`handle_cloudflare_challenge()`）

```
Method 1: CDP DOM pierce + getBoxModel    ← 主要方法，已驗證成功
    → DOM.getDocument(depth=-1, pierce=True) 穿透隱形邊界找到 iframe
    → DOM.getBoxModel(nodeId) 取得精確像素座標
    → dispatch_mouse_event 點擊 checkbox (iframe 寬度 15% 處, 垂直置中)

Method 2: 文字定位                          ← 備用
    → 搜尋頁面上的 "verify you are human" / "驗證您是人類" 等 label 文字
    → 根據 label 位置計算 Turnstile widget 的 checkbox 座標
    → CDP click

Method 3: verify_cf 模板匹配               ← 最後手段（效果差）
```

### 驗證邏輯

點擊後**不預先判斷挑戰形態**，改為接受任何一種成功訊號（`wait_for_challenge_cleared()`）：

| 訊號 | 對應場景 |
|------|----------|
| response 欄位出現 token | 嵌入式 widget 原地解開 |
| response 欄位消失 | 頁面已離開挑戰 |
| URL 改變 | 同上，從另一側觀察到 |

**為什麼不先分類**：response 欄位在嵌入式 widget 與全頁攔截頁上**都存在**，但只有
前者會把 token 填進去——後者是導向離開。曾經用「有沒有這個欄位」來分類，於是每個
中繼頁都被判成失敗，失敗又觸發 reload，把剛通過的驗證洗掉。zendriver 的 `verify_cf`
同樣把「input 消失」視為成功，理由相同。

兩個一併記住的陷阱：

- CDP Target 在嵌入式 Turnstile 解決後仍然存在，所以「Target 消失」對它恆為假。
- `cf-challenge-running`、`cf-browser-verification` 這些 HTML 活躍指標只出現在全頁
  攔截頁，嵌入式 widget 從頭到尾都不會有——用它們驗證嵌入式挑戰會**恆為「已解決」**，
  點擊一送出就回報成功。

response 欄位有兩個可能的 name，兩個都要查（`read_turnstile_response()`）：

```
input[name="cf-turnstile-response"]     一般 Turnstile
input[name="cf_challenge_response"]     部分挑戰用底線版
```

**點擊後不 reload**。重載一個還在結算的挑戰會讓它重來，在中繼頁上更可能丟掉已經
拿到的通行。失敗就讓外層 retry 重新點。

token 本身的判讀：未解時 `value` 為空字串，解開後是數百字元的字串，中間長度視為
殘留而非通過（門檻見 `CONST_TURNSTILE_MIN_TOKEN_LENGTH`）。

## 主迴圈整合

```
主迴圈（每 50ms）
    ↓
URL 變更 → cloudflare_checked = False
    ↓
cloudflare_checked == False?
    ├─ 執行 detect_cloudflare_challenge()
    ├─ 偵測到 → handle_cloudflare_challenge() → continue
    └─ 未偵測到 → 進入平台路由（KKTIX / TixCraft / ...）
```

效能考量：偵測只在 URL 變更時執行一次，不影響 50ms 迴圈效能。

### 登入頁例外

Cityline 與 KKTIX 的登入頁不走主迴圈這條路——`is_cityline_login_page()` 或
`is_kktix_login_page()` 命中時直接把 `cloudflare_checked` 設為 True。

那裡的 Turnstile 屬於登入表單本身，不是全頁阻擋。若讓主迴圈處理，它會按自己的
節奏點 checkbox，可能在平台模組填完帳密與送出之間把 widget 消耗掉。處理權因此
歸 `nodriver_kktix_signin` 與 `nodriver_cityline_login`，由它們在自己的流程中解掉
（詳見機制 02）。

代價是登入頁的 Cloudflare 中繼頁也沒有別人會管，所以 `nodriver_kktix_signin`
的輪詢中途會自行清一次。

## 測試結果

早期驗證（dash.cloudflare.com/login）：

```
偵測：CDP Target 找到 challenges.cloudflare.com iframe     PASS
處理：DOM pierce 定位 iframe → CDP click (575, 701)        PASS
結果：Turnstile 顯示「成功!」，Log in 按鈕變為可點擊       PASS
誤報：Google.com 未觸發偵測                                 PASS
```

token 驗證改版後的實測（2026-09-08，兩個實際呼叫端）：

```
KKTIX 登入頁    widget 300x65（容器 580x72）→ token len 794 @ 0.75s
                handle_cloudflare_challenge 回 True @ 0.81s
Cityline 登入頁 .cf-turnstile 在 JS 查不到、token 欄位查得到
                token len 773 @ 0.75s，回 True @ 0.84s
無 Turnstile 頁 has_turnstile_token_field 回 False，token 輪詢回空字串
                （不會誤報成功）
```

點擊位置 A/B（2026-09-10，真實 KKTIX 登入頁，每次重載後點一次）：

```
固定 30px 偏移   2/3 成功
寬度 15% 比例    3/3 成功
```

樣本小，結論只到「比例法不比固定偏移差」。真正該記住的是**兩種都會偶爾一次點不
開**——單次點擊本來就有失敗率，成功與否要靠上面的驗證邏輯判斷，不能假設點了就過。


## 相關函式

| 函式 | 位置 | 用途 |
|------|------|------|
| `detect_cloudflare_challenge()` | `src/nodriver_common.py` | 三層偵測 |
| `handle_cloudflare_challenge()` | `src/nodriver_common.py` | 三階段處理與驗證 |
| `solve_turnstile_checkbox()` | `src/nodriver_common.py` | CDP pierce 定位 iframe 並點擊 checkbox；回傳「是否派送了點擊」，不宣稱挑戰已解 |
| `wait_for_challenge_cleared()` | `src/nodriver_common.py` | 點擊後的成功判定：token / 欄位消失 / URL 改變，任一即通過 |
| `read_turnstile_response()` | `src/nodriver_common.py` | 讀 response 欄位（兩種 name 都查），回傳 (存在, 值)；導航中不拋錯 |
| `has_turnstile_token_field()` | `src/nodriver_common.py` | 頁面是否有 response 欄位 |
| `wait_for_turnstile_token()` | `src/nodriver_common.py` | 輪詢 token；先讀再等，已解的 widget 不必空等一輪。送出表單前確保 token 用 |
| `cdp_click_at()` | `src/nodriver_common.py` | CDP 滑鼠事件封裝；帶 `buttons`（按下 1、放開 0）與 `force`（0.5 / 0），KKTIX 登入送出鈕也用它 |
| `_find_cf_iframe_in_dom()` | `src/nodriver_common.py` | DOM 樹遞迴搜尋 CF iframe（模組私有） |

平台模組需要的是 `solve_turnstile_checkbox()` 加上其中一種驗證：送出表單前確保
token 用 `wait_for_turnstile_token()`，單純想知道挑戰過了沒用
`wait_for_challenge_cleared()`。都不必自行走 DOM 樹。

## 限制

- **需要互動式 Turnstile**：managed 模式（自動通過）不需要處理
- **座標必須取自 iframe 的 box model**：checkbox 位於 iframe 寬度 15% 處、垂直置中。
  不能用 `.cf-turnstile` 容器的 `getBoundingClientRect`——KKTIX 登入頁實測容器是
  580x72，widget 本身只有 300x65，用容器座標會點在空白處。iframe 本身對
  `querySelector` 不可見，只有 `DOM.getDocument(pierce=True)` 找得到。
- **無法處理 CAPTCHA 挑戰**：如果 Turnstile 升級為圖形驗證，需要人工介入
