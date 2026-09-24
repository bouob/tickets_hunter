**文件說明**：Chrome 最新版與 nodriver 相容性研究報告（遷移至 zendriver 的歷史背景文件）
**最後更新**：2026-03-14

---

> **[歷史文件]** 本報告撰寫於遷移至 zendriver 前（2025-11）。遷移已完成，現行專案使用 **zendriver**（nodriver 的活躍 fork，支援 Chrome 145+）。本文件保留作歷史參考，不再維護。
>
> 文中引用的行號與統計數字為 2026-03 當時狀態，現已失準，請以檔案名與函式名為準。

---

# Chrome / nodriver 相容性研究報告

## 1. 背景

使用者回報最新版 Chrome 導致搶票程式無法運作。本報告調查可能原因並評估解決方案。

### 現狀

| 項目 | 版本 |
|------|------|
| Chrome 目前穩定版 | **146**（2026-03-10 發布） |
| 專案使用的 nodriver | **0.48.1**（2025-11-09 發布） |
| nodriver 最後 CDP 更新 | 2025-09-06（約 Chrome 130 時期） |
| CDP 協定版本差距 | ~16 個大版本 |

---

## 2. Chrome 近期重大變更（134-146）

### Chrome 134（2025-03-04）
- 移除非標準 `getUserMedia` 音訊限制
- `<select>` 解析器行為變更的棄用試驗

### Chrome 135（2025-04-01）
- 移除 `setInterval` 低於 1ms 的固定夾值限制
- HTTP CORS 重導向時的請求更新行為變更
- 移除舊版 WebXR 方法

### Chrome 136（2025-05）
- `:visited` 連結歷史分割（隱私強化）
- `attr()` CSS 型別重新命名
- HTTP 快取分割鍵更新

### Chrome 137（2025-05-27）
- **`--load-extension` 在品牌版 Chrome 被移除**（僅影響品牌版，Chrome for Testing 不受影響）
- Blob URL 分割（按 Storage Key）
- WebAuthn 錯誤型別變更

### Chrome 138（2025-06-24）
- Media Source Extensions 非同步移除棄用
- WebGPU 配接器屬性棄用

### Chrome 139
- 移除 ISO-2022-JP charset 自動偵測
- 不再支援 macOS 11

### Chrome 140
- 移除 `Purpose: prefetch` 標頭，改用 `Sec-Purpose`
- 棄用 H1 巢狀特殊字體大小規則

### Chrome 141
- Storage Access API 語義調整（嚴格同源政策）
- 移除舊版 Purpose Header

### Chrome 145
- **永久強制使用縮減版 User-Agent 字串**，移除 `UserAgentReduction` 政策
- 縮減版 UA 格式：`Chrome/XXX.0.0.0`（隱藏精確版本號）
- IndexedDB 底層改為 SQLite
- Device Bound Session Credentials

### Chrome 146（2026-03-10）
- Scroll-triggered animations
- Scoped custom element registries

### 與 CDP/自動化相關的關鍵變更

| 變更 | 版本 | 影響 |
|------|------|------|
| `--load-extension` 移除 | 137+ | 品牌版 Chrome 無法用命令列載入擴充功能 |
| `UserAgentReduction` 政策移除 | 145 | UA 永久縮減，無法恢復完整版 |
| CDP 協定持續演進 | 每版 | nodriver 0.48.1 內建的 CDP 定義可能不符 |

---

## 3. nodriver 0.48.1 的問題

### 3.1 CDP 協定版本差距

nodriver 0.48.1 最後一次更新 CDP 定義是 2025-09-06（Chrome ~130）。目前 Chrome 已到 146，差了 ~16 個大版本的 CDP 協定演進。

**影響範圍**：專案中有 267 處 `tab.evaluate()` 呼叫和 244 處 `tab.send(cdp...)` 呼叫，分布在 14 個檔案中。

### 3.2 `Network.setBlockedURLs` 已被標記棄用

`nodriver_tixcraft.py:412-414` 使用此 API 封鎖廣告/追蹤 URL。目前有 try/except 保護，不會崩潰但封鎖可能靜默失效。

替代方案：`Fetch.enable` + request interception。

### 3.3 User-Agent 版本不一致（已修復）

- `nodriver_common.py:48` — 已更新為 Chrome/143.0.0.0
- `util.py:25` — 已更新為 Chrome/143.0.0.0

### 3.4 `enabled_labs_experiments` 過時

`nodriver_common.py:973-978` 寫入的實驗性功能旗標在新版 Chrome 可能已不存在：
```
history-journeys@4
memory-saver-multi-state-mode@1
modal-memory-saver@1
read-anything@2
```

### 3.5 nodriver 維護狀態

- PyPI 最後發布：2025-11-09（0.48.1）
- GitHub main branch 最後 commit：2025-11-09
- **已超過 4 個月無更新**，基本停止維護

---

## 4. nodriver `flatten` 分支（作者新開發）

### 發現

作者在 `flatten` 分支有新的活動：

| 日期 | Commit | 內容 |
|------|--------|------|
| 2025-12-26 | `b33173e` | 開始 flat mode 實驗 |
| 2026-03-07 | `4c37499` | 切換到 flat mode，修改 23 個檔案 |
| 2026-03-11 | `8eb2940` | 修復 browser.targets/tabs，重構命名 |

### flat mode 是什麼？

作者將架構「扁平化」，整合 `connection_flat.py` 和 `tab_flat.py` 到主模組。

> *"switched to flat mode. this opens a lot of possibilities. the most requested one is inspecting iframes, as well as clicking verification boxes :)"*

### 包含的改進

- **iframe 檢查**和**驗證框點擊**支援
- 更新 16 個 CDP 模組（animation、audits、browser、dom、network 等）
- 新增 `smart_card_emulation.py` CDP 模組
- `browser.children` 重新命名為 `browser._targets`
- `browser.tabs` 改為 property

### 風險評估

- **未發布到 PyPI**，僅在 GitHub `flatten` branch
- **有 API breaking change**（`children` -> `_targets`）
- 僅 4 個 commit，測試不足

### 安裝方式（測試用）

```bash
pip install git+https://github.com/ultrafunkamsterdam/nodriver@flatten
```

---

## 5. zendriver 替代方案評估

### 基本資訊

| 項目 | nodriver | zendriver |
|------|----------|-----------|
| 最新版本 | 0.48.1（2025-11-09） | 0.15.3（2026-03-12） |
| 維護狀態 | 停止 | 活躍（28 位貢獻者） |
| CDP 更新 | 停在 Chrome ~130 | 持續跟進 |
| API 相容性 | -- | 幾乎 drop-in replacement |
| 程式碼品質 | 無 linting | ruff + mypy + pytest + CI/CD |
| 文件 | 基本 | MkDocs Material |

### API 相容性

zendriver 是 nodriver 的 fork，API 幾乎完全相容。遷移方式：

```python
# 之前
import nodriver as uc
from nodriver import cdp
from nodriver.core.config import Config

# 之後
import zendriver as uc
from zendriver import cdp
from zendriver.core.config import Config
```

### zendriver 額外功能

- `disable_webrtc` / `disable_webgl` 配置選項（防洩漏）
- 截圖 API（`Tab.screenshot_b64`、`Element.screenshot_b64`）
- PDF 列印（`Tab.print_to_pdf`）
- 請求/回應攔截
- 增強鍵盤輸入（修飾鍵支援）
- Docker 支援
- 修復 `Tab.query_selector` race condition（stale documents）

### zendriver CI/CD 驗證機制

| Workflow | 觸發條件 | 內容 |
|----------|---------|------|
| **test** | push/PR（`.py` 變動） | pytest + 覆蓋率，**Ubuntu + Windows** 雙平台 |
| **lint** | push/PR（`.py` 變動） | ruff（程式碼風格）+ mypy（型別檢查） |
| **docs** | push/PR | MkDocs 文件建置 |
| **publish** | tag push | 建置 wheel → 發布 PyPI（無測試 gate） |

測試涵蓋：browser 啟動/關閉、tab 操作、鍵盤輸入、多瀏覽器實例、React 受控輸入、反偵測驗證（browserscan）。
測試腳本會先偵測系統上的 Chrome 路徑和版本，用真實 Chrome 跑整合測試（不是 mock）。
CDP 協定定義更新是手動用 `scripts/generate_cdp.py` 執行。

### API 精確對照表（已驗證）

#### 100% 相容（不需改動）

| API | 說明 |
|-----|------|
| `uc.start(conf)` | 簽章新增 `browser`, `user_agent` 參數，但為 keyword-only，不影響 |
| `Config(browser_args, lang, headless, browser_executable_path)` | 參數相同 |
| `Config(host, port)` | MCP 連線模式相同 |
| `conf.user_data_dir` | 屬性存在 |
| `conf.add_extension()` | 方法存在 |
| `tab.evaluate()` | 方法存在（預設值差異見下方） |
| `tab.send()` | 方法存在 |
| `tab.query_selector()` / `tab.query_selector_all()` | 方法存在 |
| `tab.find()` / `tab.get()` / `tab.reload()` / `tab.sleep()` | 方法存在 |
| `tab.js_dumps()` / `tab.get_content()` / `tab.set_window_size()` | 方法存在 |
| `tab.close()` / `tab.mouse_click()` / `tab.mouse_move()` | 方法存在 |
| `tab.add_handler()` | 方法存在 |
| `tab.verify_cf()` | 方法存在 |
| `driver.stop()` | 方法存在 |
| `cdp.dom.*` 全部 | get_document, perform_search, get_box_model, resolve_node, scroll_into_view_if_needed 等 |
| `cdp.input_.*` 全部 | dispatch_mouse_event, dispatch_key_event, MouseButton enum |
| `cdp.page.*` 全部 | JavascriptDialogOpening, handle_java_script_dialog, capture_screenshot |
| `cdp.target.*` / `cdp.runtime.*` / `cdp.dom_snapshot.*` | 全部存在 |

#### 需要遷移的 Breaking Changes（共 5 項）

| # | 變更 | nodriver | zendriver | 影響位置 | 難度 |
|---|------|----------|-----------|---------|------|
| 1 | 事件迴圈 | `uc.loop().run_until_complete()` | `asyncio.run()`（`loop()` 已棄用） | `nodriver_tixcraft.py:799`, `fetch_tixcraft_captcha.py` | 簡單 |
| 2 | CDP 改名 | `cdp.network.set_blocked_ur_ls()` | `cdp.network.set_blocked_urls()` | `nodriver_tixcraft.py:414` | 改名 |
| 3 | Handler 改名 | `tab.remove_handler()` | `tab.remove_handlers()`（複數） | `ibon.py` 等 | 改名 |
| 4 | evaluate 預設值 | `return_by_value=False`（回傳 RemoteObject） | `return_by_value=True`（回傳實際值） | 267 處要審查 | 見分析 |
| 5 | Config lang 預設 | `"en-US"` | `None` | 0 處（已明確傳入） | 無影響 |

#### Breaking Change #4 風險分析

zendriver 的 `return_by_value=True` 預設值**反而更符合我們的使用方式**：
- 267 處 `tab.evaluate()` 大多直接拿結果做比較（`if result:`, `result == "xxx"`）
- 專案已有 `convert_remote_object()` 和 `parse_nodriver_result()` 處理 RemoteObject 轉換
- 遷移後這些轉換函式收到實際值會直接原樣回傳，不會壞
- **結論**：大機率無需逐一修改，但需煙霧測試確認

#### 現有 Bug 修正機會

`nodriver_common.py:922` 的 `Config(no_sandbox=no_sandbox)` 在兩邊都被 `**kwargs` 靜默吞掉，sandbox 設定**從未生效**。遷移時應修正為 `Config(sandbox=not no_sandbox)`。

#### zendriver 新增可用功能

| 功能 | 說明 | 對專案的價值 |
|------|------|-------------|
| `disable_webrtc=True` | Config 參數，防 WebRTC IP 洩漏 | 提升反偵測 |
| `disable_webgl=False` | Config 參數 | 可選 |
| `Tab.screenshot_b64()` | 截圖 API | 簡化 OCR 流程 |
| `Tab.wait_for()` | 等待條件成立 | 簡化輪詢邏輯 |
| `Tab.intercept()` | 請求攔截 | 可替代 `set_blocked_urls` |
| `Tab.xpath()` | XPath 選擇器 | 新增選擇方式 |
| `Tab.back()` / `Tab.forward()` | 導航 | 便利方法 |
| `CookieJar` | Cookie 管理 | 可能更方便 |
| query_selector race condition 修復 | stale documents 處理 | 提升穩定性 |

---

## 6. 遷移規劃

### 6.1 遷移執行步驟

#### Phase 1：準備（不改功能）
1. `pip install zendriver==0.15.3` -- 先安裝確認可用
2. 確認 zendriver 的 CDP 模組清單完整
3. 搜尋並確認所有 `remove_handler` 的使用位置

#### Phase 2：Import 替換（13 個檔案）
4. `requirement.txt`：`nodriver==0.48.1` -> `zendriver==0.15.3`
5. `src/nodriver_tixcraft.py:28-29`：import 替換
6. `src/nodriver_common.py:16-17`：import 替換
7. 8 個 `src/platforms/*.py`：import 替換

#### Phase 3：Breaking Changes 修復（4 處）
9. `nodriver_tixcraft.py:799`：`uc.loop()` -> `asyncio.run()`
10. `nodriver_tixcraft.py:414`：`set_blocked_ur_ls` -> `set_blocked_urls`
11. `ibon.py` 等：`remove_handler` -> `remove_handlers`
12. `nodriver_common.py:922`：`no_sandbox` -> `sandbox`（Bug 修正）

#### Phase 4：PyInstaller 更新
13. `build_scripts/nodriver_tixcraft.spec:35-37`：hiddenimports 更新

#### Phase 5：驗證
14. `py_compile` 全部檔案
15. 煙霧測試：`timeout 30 python -u src/nodriver_tixcraft.py --input src/settings.json`
16. 手動測試至少 1 個平台的完整流程

#### Phase 6：文件更新
18. `docs/06-api-reference/nodriver_api_guide.md`：API 參考更新
19. `docs/02-development/structure.md`：函式索引更新

### 6.2 需要修改的完整檔案清單

| 類別 | 檔案 | 修改內容 |
|------|------|---------|
| 依賴 | `requirement.txt` | `nodriver==0.48.1` -> `zendriver==0.15.3` |
| Import | `src/nodriver_tixcraft.py:28-29` | `import zendriver as uc` / `from zendriver import cdp` |
| Import | `src/nodriver_common.py:16-17` | `from zendriver import cdp` / `from zendriver.core.config import Config` |
| Import | `src/platforms/facebook.py:6` | `from zendriver import cdp` |
| Import | `src/platforms/fansigo.py:10` | `from zendriver import cdp` |
| Import | `src/platforms/ibon.py:17` | `from zendriver import cdp` |
| Import | `src/platforms/hkticketing.py:14` | `from zendriver import cdp` |
| Import | `src/platforms/ticketplus.py:11` | `from zendriver import cdp` |
| Import | `src/platforms/kham.py:19` | `from zendriver import cdp` |
| Import | `src/platforms/kktix.py:18` | `from zendriver import cdp` |
| Import | `src/platforms/tixcraft.py:23` | `from zendriver import cdp` |
| Import | `src/platforms/cityline.py` | 確認是否有 cdp import |
| Import | `src/platforms/famiticket.py` | 確認是否有 cdp import |
| Import | `src/platforms/funone.py:58` | `from nodriver import cdp`（函式內 import） |
| 事件迴圈 | `src/nodriver_tixcraft.py:799` | `asyncio.run(main(args))` |
| CDP 改名 | `src/nodriver_tixcraft.py:414` | `set_blocked_urls` |
| Handler | `src/platforms/ibon.py` 等 | `remove_handlers` |
| Bug 修正 | `src/nodriver_common.py:922` | `sandbox=not no_sandbox` |
| PyInstaller | `build_scripts/nodriver_tixcraft.spec:35-37` | hiddenimports |
| 文件 | `docs/06-api-reference/nodriver_api_guide.md` | API 參考 |

### 6.3 復原計畫

若遷移失敗：
1. `git checkout -- requirement.txt src/ build_scripts/`
2. `pip install nodriver==0.48.1`
3. 煙霧測試確認還原

---

## 7. 專案 nodriver API 使用統計

### 使用頻率

| API 類別 | 呼叫次數 | 優先順序 |
|---------|---------|--------|
| `tab.evaluate()` | 267 | 最高 |
| `tab.send(cdp...)` | 244 | 最高 |
| `tab.query_selector*()` | 166 | 最高 |
| `tab.get()` | ~80 | 高 |
| `tab.reload()` | ~50 | 中 |
| `tab.sleep()` | ~50 | 中 |
| `cdp.dom.*` | 44 | 中 |
| `cdp.page.*` | ~20 | 中 |
| `cdp.network.*` | ~15 | 中 |
| `cdp.input_.*` | 10 | 低 |
| `cdp.dom_snapshot.*` | 8 | 低 |
| `cdp.target.*` | 1 | 低 |

### 各檔案 API 分布

| 檔案 | 主要 API | 特色 |
|------|---------|------|
| `nodriver_tixcraft.py` | `uc.start()`、`cdp.network.*` | 啟動、Cookie 管理 |
| `nodriver_common.py` | `cdp.dom.*`、`cdp.input_.*` | 共用工具、Cloudflare Turnstile |
| `ibon.py` | `cdp.dom.*`、`cdp.dom_snapshot.*` | 大量 DOM 搜尋和快照 |
| `kham.py` | `tab.evaluate()`、`cdp.dom.*` | 高頻 JS 執行（70 次） |
| `hkticketing.py` | `tab.evaluate()` | 高頻 JS 執行（39 次） |
| `tixcraft.py` | `cdp.page.JavascriptDialogOpening` | Alert 處理 |
| `kktix.py` | `tab.evaluate()`、`cdp.page.*` | JS + Alert |
| `famiticket.py` | `tab.evaluate()` | JS 執行（20 次） |
| `funone.py` | `tab.evaluate()` | JS 執行（18 次） |

### 關鍵使用模式

#### 模式 1：基本導航和查詢
```python
tab = await driver.get(url)
element = await tab.query_selector('selector')
text = await tab.evaluate('document.querySelector("...").textContent')
```

#### 模式 2：Cloudflare Turnstile 處理
```python
doc = await tab.send(cdp.dom.get_document(depth=-1, pierce=True))
box = await tab.send(cdp.dom.get_box_model(node_id=iframe_node))
await tab.send(cdp.input_.dispatch_mouse_event(type_="mousePressed", x=..., y=...))
```

#### 模式 3：Alert 自動接受
```python
tab.add_handler(cdp.page.JavascriptDialogOpening, handler)
await tab.send(cdp.page.handle_java_script_dialog(accept=True))
```

#### 模式 4：DOM 文字搜尋（ibon 特有）
```python
search_id, count = await tab.send(cdp.dom.perform_search(query="text", include_user_agent_shadow_dom=True))
node_ids = await tab.send(cdp.dom.get_search_results(search_id, 0, count))
await tab.send(cdp.dom.discard_search_results(search_id))
```

#### 模式 5：OCR 快照
```python
documents, strings = await tab.send(cdp.dom_snapshot.capture_snapshot(computed_styles=[]))
screenshot = await tab.send(cdp.page.capture_screenshot(format_='png'))
```

---

## 8. 建議方案

### 短期（已完成）
- [x] 統一 User-Agent 版本號為 Chrome/143.0.0.0

### 中期（推薦方案排序）

| 優先 | 方案 | 風險 | 工作量 | 說明 |
|------|------|------|--------|------|
| 1 | 遷移到 zendriver | 中 | 中 | API 幾乎相容，CDP 持續更新 |
| 2 | 安裝 nodriver flatten branch | 中 | 低 | 作者有修復 iframe/驗證框，但未正式發布 |
| 3 | 手動更新 CDP 定義 | 低 | 中 | 用 `generate_cdp.py` 從最新 Chrome 協定重新生成 |

### 長期
- 追蹤 nodriver flatten branch 是否合併到 main 並行布
- 評估 zendriver 的長期穩定性
- 考慮建立 Chrome 版本鎖定機制（`chrome_downloader.py` 加版本上限）

---

## 9. 參考資料

- [nodriver PyPI](https://pypi.org/project/nodriver/) -- 最後版本 0.48.1
- [nodriver flatten branch](https://github.com/ultrafunkamsterdam/nodriver/tree/flatten) -- 作者新開發
- [zendriver GitHub](https://github.com/cdpdriver/zendriver) -- 活躍維護的 fork
- [zendriver Release Notes](https://zendriver.dev/release-notes/)
- [Chrome 145 CDP Bug Report](https://discuss.ai.google.dev/t/bug-browser-cdp-mode-broken-on-windows-with-chrome-145/127170)
- [Chrome 137 --load-extension 移除](https://github.com/seleniumbase/SeleniumBase/issues/3771)
- [Chrome Release Notes](https://developer.chrome.com/release-notes)
- [Chrome User-Agent Reduction](https://www.chromium.org/updates/ua-reduction/)
