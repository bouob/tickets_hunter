# 機制 15：Cloudflare Turnstile 偵測與處理

**文件說明**：說明搶票系統的 Cloudflare Turnstile 偵測機制與 CDP Shadow DOM 穿透點擊實作
**最後更新**：2026-02-15

---

## 概述

當票務平台（KKTIX、TixCraft 等）啟用 Cloudflare 保護時，會出現 Turnstile 驗證
（「驗證您是人類」checkbox）。程式能自動偵測並點擊 checkbox 通過驗證。

## 核心發現

### Turnstile iframe 對 JavaScript 不可見

Cloudflare Turnstile 的 iframe 透過特殊機制注入頁面，**標準 DOM 查詢無法找到**：

```javascript
// 全部返回 null/false：
document.querySelector('iframe[src*="challenges.cloudflare.com"]')  // null
document.querySelector('.cf-turnstile')                              // null
document.querySelectorAll('iframe')  // 只找到無關的 iframe
```

但 **CDP 協議可以找到**：

| 方法 | 能否找到 |
|------|----------|
| `document.querySelector()` | ❌ |
| `shadowRoot` 搜尋 | ❌ |
| CDP `Target.getTargets()` | ✅ |
| CDP `DOM.getDocument(pierce=True)` | ✅ |

### nodriver `verify_cf()` 無效

nodriver 內建的 `verify_cf()` 使用 OpenCV 模板匹配截圖來找 checkbox。
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
    → dispatch_mouse_event 點擊 checkbox (iframe左側30px, 垂直置中)

Method 2: 文字定位                          ← 備用
    → 搜尋頁面上的 "verify you are human" / "驗證您是人類" 等 label 文字
    → 根據 label 位置計算 Turnstile widget 的 checkbox 座標
    → CDP click

Method 3: verify_cf 模板匹配               ← 最後手段（效果差）
```

### 驗證邏輯

點擊後的驗證需要區分兩種場景：

| 場景 | 解決後行為 | 驗證方式 |
|------|-----------|----------|
| 全頁面攔截 | 頁面重導向 | CDP Target 消失 → 偵測返回 False |
| 嵌入式 Turnstile | Widget 顯示「成功!」，頁面不變 | HTML 關鍵字檢查（CDP Target 仍存在） |

**關鍵**：嵌入式 Turnstile 解決後，CDP Target 仍然存在。因此點擊後的驗證
只使用 HTML 活躍指標（`cf-challenge-running` 等），不使用 CDP Target 檢查。

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

## 測試結果（dash.cloudflare.com/login）

```
偵測：CDP Target 找到 challenges.cloudflare.com iframe     ✅ PASS
處理：DOM pierce 定位 iframe → CDP click (575, 701)        ✅ PASS
結果：Turnstile 顯示「成功!」，Log in 按鈕變為可點擊       ✅ PASS
誤報：Google.com 未觸發偵測                                 ✅ PASS
```

## 相關函數

| 函數 | 位置 | 用途 |
|------|------|------|
| `detect_cloudflare_challenge()` | line 350 | 三層偵測 |
| `_find_cf_iframe_in_dom()` | line 413 | DOM 樹遞迴搜尋 CF iframe |
| `_cdp_click()` | line 446 | CDP 滑鼠事件封裝 |
| `handle_cloudflare_challenge()` | line 459 | 三階段處理 |

## 限制

- **需要互動式 Turnstile**：managed 模式（自動通過）不需要處理
- **座標依賴視窗大小**：Turnstile checkbox 固定在 iframe 左側 30px
- **無法處理 CAPTCHA 挑戰**：如果 Turnstile 升級為圖形驗證，需要人工介入
