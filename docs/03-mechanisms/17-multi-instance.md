# 機制 17：多開實例（Multi-Instance）

**文件說明**：同時執行多個搶票實例的隔離機制——實例識別、狀態目錄、暫停語意、heartbeat 儀表板與平台限制
**最後更新**：2026-06-13

---

## 概述

「多開」讓使用者同時跑多個搶票實例，涵蓋三種情境：

| 情境 | 範例 | 關鍵需求 |
|------|------|----------|
| 不同平台同時搶 | 一實例搶 TixCraft、一實例搶 iBon | 實例間狀態完全隔離 |
| 同平台不同活動 | 兩個 TixCraft 實例搶不同演唱會 | 各自獨立 homepage 與關鍵字 |
| 不同帳號 | 各實例用不同帳號分散風險 | 各自獨立帳號設定與瀏覽器 profile |

核心結論：**狀態隔離對全部平台一致生效，平台模組零修改**。

---

## 架構：OS 多行程

每個實例 = 一個獨立的 `nodriver_tixcraft.py` 行程 + 一個 Chrome。隔離由作業系統保證。

**為何不用單行程多瀏覽器**：各平台模組（`src/platforms/*.py`）的執行狀態都放在模組層級 `_state` dict（如 tixcraft 的 `area_retry_count`、ibon 的 `queue_it_enter_time`）。若改成單行程內 asyncio 同時控多個瀏覽器，所有平台的模組狀態都要重構成 per-browser 實例化，等於重寫全部平台邏輯。OS 多行程讓平台模組完全不必改。

代價：每實例一個 Chrome 約 400MB+ 記憶體（搶票場景通常 2–4 開，可接受）。

---

## 實例識別（instance id）

行程啟動時於 `main()`（`src/nodriver_tixcraft.py`）推導 instance id，優先序：

```
--instance <name>   >   --input <path> 的檔名 stem   >   "default"
```

- `--input profiles/kktix-a.json` → instance id `kktix-a`
- 檔名為 `settings.json` → 一律映射 `default`（單開回歸行為不變）
- `--instance` 覆寫（同一份 config 想開第二個實例時用，見「重複 RUN」）
- id 格式驗證 `[A-Za-z0-9_-]{1,32}`，防路徑穿越

推導後呼叫 `util.set_instance_id()`；之後全程以 `util.get_instance_id()` 取得。

---

## 狀態目錄結構

```
src/（或 EXE 目錄，= util.get_app_root()）
├── settings.json                  ← default profile，不動
├── MAXBOT_INT28_IDLE.txt          ← default 實例的暫停檔（原位置）
├── heartbeat.txt                  ← default 實例心跳
├── profiles/                      ← 具名 profile 的設定檔
│   ├── kktix-a.json
│   └── tixcraft-b.json
└── instances/                     ← 只放「非 default」實例的狀態檔
    └── kktix-a/
        ├── MAXBOT_INT28_IDLE.txt
        ├── MAXBOT_LAST_URL.txt
        ├── MAXBOT_QUESTION.txt
        ├── MAXBOT_ONLINE_ANSWER.txt
        ├── mcp_port.txt
        └── heartbeat.txt
```

路徑由 `util.get_instance_state_path(filename)` 解析：
- **default** → `app_root/<filename>`（既有 UI、暫停鈕、清理流程零修改，單開行為 100% 不變）
- **具名** → `app_root/instances/<id>/<filename>`（含 `os.makedirs`）

> 不採檔名字尾方案（`MAXBOT_INT28_IDLE_kktix-a.txt`）：app root 會髒亂、清理需模式比對、易誤刪。

---

## 共用狀態函式（全平台隔離的關鍵）

所有平台都透過 `src/nodriver_common.py` 的共用函式存取狀態檔，這些函式一律走 `util.get_instance_state_path`，故隔離對全平台自動生效，**無需逐平台修改**：

| 函式 | 狀態檔 | 用途 |
|------|--------|------|
| `check_and_handle_pause()` / `sleep_with_pause_check()` / `asyncio_sleep_with_pause_check()` | `MAXBOT_INT28_IDLE.txt` | 暫停檢查 |
| `write_last_url_to_file()` | `MAXBOT_LAST_URL.txt` | 狀態列 URL |
| `write_question_to_file()` | `MAXBOT_QUESTION.txt` | 線上答題問題 |
| `util.get_answer_list_from_user_guess_string()` | `MAXBOT_ONLINE_ANSWER.txt` | 線上答題答案（讀） |

例外：`platforms/kktix.py`、`ibon.py`、`tixcraft.py` 的 alert handler 內各有一處**直接** `os.path.exists(暫停檔)`，也已改走 `util.get_instance_state_path`。

瀏覽器層級隔離為天然成立：zendriver 未指定 `user_data_dir` 時每實例自動取得 `%TEMP%/uc_*` 隨機獨立目錄，瀏覽器 prefs / Local State（寫在 `conf.user_data_dir`）與 Cookie（從各自 config 注入）皆獨立。captcha 截圖走記憶體 buffer 不落地，無碰撞。

---

## 暫停語意：per-instance

`check_and_handle_pause()` 只檢查**自己實例**的暫停檔：

- default 實例的暫停檔 = 根目錄 `MAXBOT_INT28_IDLE.txt` → 既有 UI 暫停鈕、`maxbot_idle` / `maxbot_resume` 語意自然變為「只控制 default 實例」
- 具名實例 → `instances/<id>/MAXBOT_INT28_IDLE.txt`
- 不保留「根目錄檔存在 = 全部暫停」的全域層
- 「全部暫停」由 UI 對所有存活實例逐一建各自的暫停檔實現

### idle_keyword 定時排程 per-instance

`change_maxbot_status_by_keyword()`（`src/settings.py`，由 `settgins_gui_timer` 每 0.4s 驅動）遍歷 `list_profile_names()`，對每個 profile `load_json(profile)` 讀其 `advanced.idle_keyword` / `resume_keyword` / `idle_keyword_second` / `resume_keyword_second`，命中時呼叫 `maxbot_idle(profile)` / `maxbot_resume(profile)`。每個實例依**自己 profile** 的關鍵字暫停／恢復自己。

> 序號／自訂 `--instance` 實例（無對應 profile json）不納入關鍵字排程，因其 backing profile 僅啟動器記憶體知道。

---

## heartbeat 與「執行中實例」儀表板

### 心跳寫入（bot 側）

主迴圈（`src/nodriver_tixcraft.py`）每約 5 秒 `touch` `heartbeat.txt`（經 `util.get_instance_state_path`，default 寫根目錄）。平台無關，所有實例一致。

### 總覽（settings 側）

`InstancesHandler`（`/instances`，`src/settings.py`）回傳每個實例的狀態：

- 來源 = `list_instance_ids()`：所有 profile（含 default）∪ `instances/` 下實際存在的目錄（涵蓋 CLI `--instance` 實例）
- `get_instance_status(profile)` 回傳 `{id, alive, paused, last_url}`：
  - `alive` = `heartbeat.txt` 的 mtime 在 **30 秒**內（閾值寬鬆，因 Cloudflare 處理可能卡主迴圈 >10s，太緊會誤判死亡）
  - `paused` = 暫停檔存在
  - `last_url` = 讀 `MAXBOT_LAST_URL.txt`

前端「執行階段」頁籤的「執行中實例」面板每 2 秒輪詢 `/instances`，渲染每列的存活／運行／暫停狀態與執行網址，提供每列暫停／繼續鈕與「全部暫停」（逐一對存活實例打 `/pause?profile=<id>`）。

---

## profile 管理

`profiles/*.json`，每個 profile 是**完整的 settings.json 副本**：

- `settings.json` 即 default profile，永遠存在，行為不變
- profile 走 `settings.migrate_config` 正常版本遷移，與 `--input` 直接相容
- **settings.json schema 零變更**；UI 目前選的 profile 存瀏覽器 localStorage，不入 schema
- 相關函式（`src/settings.py`）：`get_profile_filepath` / `list_profile_names` / `ProfilesHandler`（list / create / delete）

### 重複 RUN 與序號實例

對已有存活實例的 profile 再按「搶票」：前端偵測 `/instances` 中該 profile 已存活 → 跳確認框（警告 session 互踢）→ 算出下一個空序號（`kktix-2`）→ 呼叫 `/run?profile=<name>&instance=<newid>`。

後端 `RunHandler` 收 `?instance=` → `launch_maxbot(profile, instance_override)` → `util.launch_maxbot(instance=...)` 轉成 `--instance`；`--input` 仍給 profile json，故 bot 以 override 當 instance id、以 profile 設定運行。

### 孤兒清理

`clean_tmp_file()`（settings 啟動時）清除 `instances/` 下「無對應 profile json」的目錄。語意：刪 profile 當下**不**刪 `instances/<id>/`（避免運行中實例因暫停檔消失而意外恢復）；settings 重啟才清。用自訂 `--instance` 名稱（無對應 profile）的 CLI 實例若在 settings 重啟時未運行，其狀態目錄會被當孤兒清掉——CLI 使用者應讓 instance 名與 profile 檔名一致。

---

## 平台限制與風險

- **KKTIX**：2024 後多開多視窗會打亂自身 CF Waiting Room 排隊順序（CF 用 cookie 時間戳排序），且可能被導入 Infinite Queue（假排隊頁）。UI 於偵測 ≥2 個 KKTIX profile 時顯示警告 badge。
- **同帳號 session 互踢**：同帳號同活動多開會被平台踢登入（TixCraft 已知）。安全用法是「一實例一帳號」。UI 對拓元家族（含 ticketmaster）、iBon（Queue-it）等亦顯示對應風險 badge。
- **記憶體**：每實例一個 Chrome 約 400MB+，依機器規格控制開數。
- **改帳號需重啟實例**：帳號/Cookie 不在熱載白名單。

---

## 相關檔案與函式

| 檔案 | 函式 |
|------|------|
| `src/util.py` | `set_instance_id` / `get_instance_id` / `get_instance_state_path` / `launch_maxbot`（`instance=` 參數） |
| `src/nodriver_tixcraft.py` | `main()` 實例 id 推導、heartbeat 寫入、`reload_config`（監看實際載入的設定檔） |
| `src/nodriver_common.py` | `check_and_handle_pause` / `write_last_url_to_file` / `write_question_to_file`（走 instance path） |
| `src/settings.py` | `InstancesHandler` / `list_instance_ids` / `get_instance_status` / `get_instance_state_filepath` / `list_profile_names` / `ProfilesHandler` / `RunHandler` / `launch_maxbot` / `change_maxbot_status_by_keyword` / `clean_tmp_file` |
| `src/www/settings.{html,js}` | profile 分頁列、執行中實例面板、重複 RUN 確認框、風險 badge、答題實例選擇器 |

---

## 相關文件

- 設定檔 Hot Reload（監看實際載入檔）：[14-hot-reload.md](./14-hot-reload.md)
- 頁面監控與購票完成不自動暫停：[03-page-monitoring.md](./03-page-monitoring.md)
- 暫停機制（錯誤處理）：[12-error-handling.md](./12-error-handling.md)
- 使用者操作指南：`guide/settings-guide.md`「多開實例」

---

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| v1.0 | 2026-06-13 | 初版：多開實例機制（Phase 1–3：CLI 隔離、profile UI、heartbeat 儀表板、重複 RUN、per-instance idle_keyword、風險警示） |
