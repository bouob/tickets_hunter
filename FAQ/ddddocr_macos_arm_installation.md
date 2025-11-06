# ddddocr 在 MacOS ARM (M1/M2/M3) 安裝問題

本文件專門解決 Apple Silicon (M1/M2/M3) 晶片 Mac 電腦安裝 ddddocr 時遇到的問題。

---

## 🔍 問題描述

使用 Apple Silicon (M1/M2/M3) 晶片的 Mac 電腦在安裝 `ddddocr` 時，可能會遇到以下錯誤：

```
ERROR: Cannot install ddddocr==1.x.x because these package versions have conflicting dependencies.
```

或是

```
ERROR: Could not find a version that satisfies the requirement onnxruntime
```

---

## 📊 原因分析

**核心問題**：ddddocr 依賴 `onnxruntime` 套件，而早期版本的 onnxruntime 對 ARM64 架構支援不完整。

**技術細節**：
- ddddocr 使用 ONNX Runtime 作為推理引擎
- 早期 onnxruntime 版本僅提供 x86_64 版本
- M1/M2/M3 晶片採用 ARM64 架構，與 x86_64 不相容
- 透過 Rosetta 2 轉譯執行會導致效能下降與相容性問題

---

## ✅ 解決方案

### 方案一：使用 Miniforge3（推薦）

**步驟 1：安裝 Miniforge3**

```bash
# 下載 Miniforge3 for ARM64
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh

# 安裝
bash Miniforge3-MacOSX-arm64.sh

# 初始化
source ~/.zshrc  # 或 source ~/.bash_profile
```

**步驟 2：建立虛擬環境**

```bash
# 建立 Python 3.10 環境（建議版本）
conda create -n tickets_hunter python=3.10
conda activate tickets_hunter
```

**步驟 3：安裝相依套件**

```bash
# 先安裝 onnxruntime（conda 版本對 ARM 支援較好）
conda install -c conda-forge onnxruntime

# 或使用 Homebrew 安裝 onnxruntime
brew install onnxruntime

# 安裝 ddddocr
pip install ddddocr

# 安裝專案其他相依套件
pip install -r requirement.txt
```

**步驟 4：驗證安裝**

```python
# 測試 ddddocr 是否正常運作
python3 -c "import ddddocr; ocr = ddddocr.DdddOcr(); print('ddddocr 安裝成功！')"
```

---

### 方案二：使用官方 onnxruntime（2024 更新）

**重要更新**：自 2024 年起，官方 `onnxruntime` 已提供完整的 ARM64 支援。

**系統需求**：
- macOS 13.0+ (Ventura 或更新版本)
- Python 3.10, 3.11, 3.12, 或 3.13
- 原生 ARM64 Python（非透過 Rosetta 執行）

**安裝步驟**：

```bash
# 確認 Python 是 ARM64 版本
file $(which python3) | grep -q arm64 && echo "Python 為 ARM64 原生版本 ✓" || echo "Python 非 ARM64 版本 ✗"

# 直接安裝（官方已支援 ARM64）
pip install onnxruntime
pip install ddddocr
pip install -r requirement.txt
```

---

### 方案三：使用 Rosetta 2 模式（備用方案）

**適用情境**：當上述方案都失敗時使用。

**缺點**：效能較差，不建議長期使用。

**步驟**：

```bash
# 安裝 Rosetta 2（如尚未安裝）
softwareupdate --install-rosetta --agree-to-license

# 使用 Rosetta 執行 Terminal
# 在 Finder 中找到 Terminal.app
# 右鍵 → 取得資訊 → 勾選「使用 Rosetta 打開」

# 重新開啟 Terminal，安裝 x86_64 版本的 Python
arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
arch -x86_64 brew install python@3.10

# 安裝套件
arch -x86_64 pip3 install ddddocr
arch -x86_64 pip3 install -r requirement.txt
```

---

### 方案四：使用 Rust 版本 ddddocr（進階）

**特色**：預編譯二進位檔，無需處理 Python 相依性問題。

**下載位置**：
- GitHub Release: https://github.com/86maid/ddddocr/releases
- 選擇 `ddddocr-macos-aarch64` 版本

**使用方式**：

```bash
# 下載最新版本
wget https://github.com/86maid/ddddocr/releases/latest/download/ddddocr-macos-aarch64.tar.gz

# 解壓縮
tar -xzvf ddddocr-macos-aarch64.tar.gz

# 執行（需要另外撰寫整合腳本）
./ddddocr --help
```

---

## 🔍 常見錯誤排除

### 錯誤 1：`zsh: illegal hardware instruction`

**原因**：嘗試執行 x86_64 程式在 ARM64 環境下。

**解決**：
```bash
# 確認 Python 架構
python3 -c "import platform; print(platform.machine())"
# 應輸出 'arm64'，如果是 'x86_64' 則需重新安裝原生版本
```

---

### 錯誤 2：`No matching distribution found for onnxruntime`

**原因**：Python 版本不支援或 Python 非 ARM64 版本。

**解決**：
```bash
# 檢查 Python 版本
python3 --version
# 應為 3.10, 3.11, 3.12, 或 3.13

# 檢查 Python 架構
file $(which python3)
# 應包含 'arm64'
```

---

### 錯誤 3：安裝過程需要科學上網工具

**原因**：部分套件下載來源在中國境外。

**解決**：
- 使用 VPN 或代理伺服器
- 使用國內鏡像源（如清華、阿里雲）
- 或等待網路穩定時重試

```bash
# 使用清華鏡像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ddddocr
```

---

## 📚 參考資源

**官方文件**：
- ddddocr GitHub: https://github.com/sml2h3/ddddocr
- ddddocr Issue #67 (M1 安裝): https://github.com/sml2h3/ddddocr/issues/67
- ONNX Runtime 官方文件: https://onnxruntime.ai/docs/install/

**社群討論**：
- Miniforge3 for ARM: https://github.com/conda-forge/miniforge
- onnxruntime-silicon (第三方套件): https://github.com/cansik/onnxruntime-silicon

**注意事項**：
- `onnxruntime-silicon` 套件已過時，官方 `onnxruntime` 現已支援 ARM64
- 建議使用 Python 3.10 以獲得最佳相容性
- 確保 macOS 版本為 13.0 (Ventura) 或更新版本

---

## 🎯 最佳實踐建議

1. **優先使用官方套件**：2024 年後官方 onnxruntime 已完整支援 ARM64
2. **使用 Miniforge3**：比原生 pip 對 ARM 相容性更好
3. **避免 Rosetta 模式**：效能較差且可能產生其他問題
4. **保持系統更新**：macOS 13.0+ 獲得更好的 ARM64 支援
5. **使用虛擬環境**：避免污染系統 Python 環境

---

## 📞 尋求協助

如果以上解決方案無法解決您的問題，請至 [GitHub Issues](https://github.com/bouob/tickets_hunter/issues) 提出問題，並提供：

1. 作業系統版本與架構（macOS/Windows/Linux, ARM64/x86_64）
2. Python 版本（`python3 --version`）
3. 完整錯誤訊息
4. 已嘗試的解決方案

---

*最後更新：2025.01.XX | 由 Claude Code AI 輔助製作*
