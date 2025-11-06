# ddddocr API 使用指南

## 概述

ddddocr 是一個通用的 OCR 識別庫，專門用於識別驗證碼。本指南提供在 MaxBot 專案中使用 ddddocr 的完整參考。

**GitHub**: https://github.com/sml2h3/ddddocr

## 安裝

```bash
pip install ddddocr
```

## 基本使用

### 1. 初始化 OCR 物件

```python
import ddddocr

# 標準模式（推薦在初始化時建立一次，重複使用）
ocr = ddddocr.DdddOcr()

# Beta 模式（替代模型）
ocr = ddddocr.DdddOcr(beta=True)

# 關閉廣告顯示
ocr = ddddocr.DdddOcr(show_ad=False)
```

**重要**: 應該在程式啟動時初始化一次 OCR 物件並重複使用，避免每次識別都重新載入模型。

### 2. 驗證碼識別

```python
# 讀取圖片（bytes 格式）
with open('captcha.jpg', 'rb') as f:
    image_bytes = f.read()

# 執行識別
result = ocr.classification(image_bytes)
print(result)  # 輸出: "AB12"
```

## 字符範圍限定 (set_ranges)

### 預定義範圍

使用 `set_ranges()` 方法可以限定識別的字符範圍，提高準確度：

```python
# 0: 純數字 (0-9)
ocr.set_ranges(0)

# 1: 純小寫英文 (a-z)
ocr.set_ranges(1)

# 2: 純大寫英文 (A-Z)
ocr.set_ranges(2)

# 3: 小寫英文 + 數字 (a-z0-9)
ocr.set_ranges(3)

# 4: 大寫英文 + 數字 (A-Z0-9)
ocr.set_ranges(4)

# 5: 大小寫英文 (a-zA-Z)
ocr.set_ranges(5)

# 6: 大小寫英文 + 數字 (a-zA-Z0-9)
ocr.set_ranges(6)

# 7: 預設全部字符
ocr.set_ranges(7)
```

### 自定義字符集

```python
# 自定義允許的字符
ocr.set_ranges("0123456789ABCDEF")  # 只識別十六進位字符
```

### **重要：set_ranges 正確用法**

⚠️ **`set_ranges()` 必須搭配 `probability=True` 參數使用才會生效！**

```python
# ❌ 錯誤用法 - set_ranges() 不會生效
ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
ocr.set_ranges(0)
result = ocr.classification(image_bytes)  # 仍會輸出字母

# ✅ 正確用法 - 使用 probability=True 並手動提取
ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
ocr.set_ranges(0)  # 限定為純數字

# 使用 probability 模式
result = ocr.classification(image_bytes, probability=True)

# 手動從 probability 結果提取字符
if isinstance(result, dict) and 'probability' in result and 'charsets' in result:
    filtered_result = ""
    for prob_list in result['probability']:
        max_idx = prob_list.index(max(prob_list))
        filtered_result += result['charsets'][max_idx]
    print(filtered_result)  # 只會輸出數字，如: "8651"
```

### MaxBot 使用範例

```python
# ibon 驗證碼是純數字（4位數）
ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
ocr.set_ranges(0)  # 限定為純數字

# 使用 probability 模式識別
result = ocr.classification(image_bytes, probability=True)

# 提取過濾後的結果
if isinstance(result, dict) and 'probability' in result and 'charsets' in result:
    ocr_answer = ""
    for prob_list in result['probability']:
        max_idx = prob_list.index(max(prob_list))
        ocr_answer += result['charsets'][max_idx]
    # ocr_answer 只會包含數字 0-9
```

## classification() 方法參數

### 基本參數

```python
result = ocr.classification(
    img,                    # bytes: 圖片二進位資料（必填）
    png_fix=False,          # bool: 修復透明黑色 PNG 圖片
    probability=False       # bool: 返回機率資訊
)
```

### png_fix 參數

處理透明背景且前景為黑色的 PNG 圖片：

```python
# 如果驗證碼是透明背景的 PNG
result = ocr.classification(image_bytes, png_fix=True)
```

### probability 參數

獲取識別的機率資訊（用於分析識別信心度）：

```python
# 返回完整機率分布
prob_result = ocr.classification(image_bytes, probability=True)

# 可根據機率選擇信心度最高的結果
# prob_result 包含每個字符位置的機率分布
```

## 進階功能

### 1. Beta 模型

Beta 模型提供替代的識別引擎，可能對某些驗證碼有更好的識別率：

```python
# 使用 beta 模型
ocr_beta = ddddocr.DdddOcr(beta=True)

# 比較兩種模型的結果
result_default = ocr.classification(image)
result_beta = ocr_beta.classification(image)
```

### 2. 自定義模型導入

```python
ocr = ddddocr.DdddOcr(
    det=False,
    ocr=False,
    import_onnx_path="custom_model.onnx",
    charsets_path="charsets.json"
)
```

## 性能優化建議

### 1. 全局初始化

```python
# 不推薦：每次識別都初始化
def bad_ocr(image):
    ocr = ddddocr.DdddOcr()  # 每次都載入模型，效能差
    return ocr.classification(image)

# 推薦：全局初始化一次
_ocr = ddddocr.DdddOcr()

def good_ocr(image):
    return _ocr.classification(image)
```

### 2. 字符範圍限定

限定字符範圍可以：
- 提高識別準確度
- 減少誤判（例如 O 和 0 的混淆）
- 加快識別速度

```python
# ibon/tixcraft 驗證碼通常是純數字
ocr.set_ranges(0)
```

### 3. 圖片預處理

雖然 ddddocr 不需要預處理，但某些情況下預處理仍有幫助：

```python
from PIL import Image, ImageEnhance
import io

def preprocess_image(image_bytes):
    # 轉為 PIL Image
    img = Image.open(io.BytesIO(image_bytes))

    # 轉灰階
    img = img.convert('L')

    # 增強對比
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    # 轉回 bytes
    output = io.BytesIO()
    img.save(output, format='PNG')
    return output.getvalue()
```

## MaxBot 實作範例

### Chrome/Selenium 版本

```python
# 初始化（全局）
ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
ocr.set_ranges(0)  # ibon 純數字

# Canvas 擷取驗證碼
driver.set_script_timeout(1)
form_verifyCode_base64 = driver.execute_async_script("""
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');
    var img = document.getElementById('captcha_img');
    canvas.height = img.naturalHeight;
    canvas.width = img.naturalWidth;
    context.drawImage(img, 0, 0);
    callback = arguments[arguments.length - 1];
    callback(canvas.toDataURL());
""")

# 識別
if form_verifyCode_base64:
    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
    ocr_answer = ocr.classification(img_base64)
    print(f"OCR Result: {ocr_answer}")
```

### NoDriver 版本

```python
# 初始化（全局）
ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
ocr.set_ranges(0)  # ibon 純數字

# HTTP 下載驗證碼圖片
import requests

# 取得瀏覽器 cookies
cookies_dict = {}
cookies_list = await tab.send(cdp.network.get_cookies())
if cookies_list and cookies_list.cookies:
    for cookie in cookies_list.cookies:
        cookies_dict[cookie.name] = cookie.value

# 下載圖片
response = requests.get(
    captcha_url,
    cookies=cookies_dict,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': page_url
    }
)

if response.status_code == 200:
    img_bytes = response.content
    ocr_answer = ocr.classification(img_bytes)
    print(f"OCR Result: {ocr_answer}")
```

## 常見問題

### Q1: 為什麼識別率不高？

**解決方案**:
1. 使用 `set_ranges()` 限定字符範圍
2. 嘗試 `beta=True` 模型
3. 檢查圖片品質（解析度、清晰度）
4. 考慮圖片預處理

### Q2: 記憶體佔用過高？

**解決方案**:
- 確保只初始化一次 OCR 物件（全局變數）
- 不要在迴圈中重複初始化

### Q3: 某些字符經常誤判？

**解決方案**:
```python
# 排除容易混淆的字符
# 例如：排除 O 和 0, I 和 1
ocr.set_ranges("23456789ABCDEFGHJKLMNPQRSTUVWXYZ")
```

### Q4: 如何判斷識別信心度？

**解決方案**:
```python
# 使用 probability 參數
prob_result = ocr.classification(image, probability=True)
# 分析機率分布，信心度低的結果可以選擇重試
```

## 參考資源

- **官方 GitHub**: https://github.com/sml2h3/ddddocr
- **作者**: sml2h3
- **License**: MIT
- **Python 支援**: 3.6 - 3.12
- **依賴**: onnxruntime

## 版本資訊

- **當前使用版本**: 檢查 `pip show ddddocr`
- **更新方式**: `pip install --upgrade ddddocr`

## 注意事項

1. **初始化成本**: 載入模型需要時間和記憶體，務必重複使用同一個 OCR 物件
2. **字符範圍**: 使用 `set_ranges()` 是提升準確度的最佳方法
3. **Beta 模型**: 並非在所有情況下都更好，需實際測試
4. **圖片格式**: 支援常見格式（JPEG, PNG, BMP 等）
5. **ARM 架構**: 某些 ARM 平台可能不支援，需要檢查 onnxruntime 相容性

---

**最後更新**: 2025-10-28
