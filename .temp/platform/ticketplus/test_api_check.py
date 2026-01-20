"""
TicketPlus API 檢查測試工具

用途：獨立測試 TicketPlus 的 API pending 狀態檢查邏輯
使用方式：
    python test_api_check.py
"""

import asyncio
import nodriver as uc
import sys
import os

# 加入父目錄以便導入 config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

async def test_ticketplus_api_check():
    """測試 TicketPlus API 檢查"""

    print("=" * 60)
    print("TicketPlus API 檢查測試工具")
    print("=" * 60)
    print()

    # 啟動瀏覽器
    print("[1/4] 啟動瀏覽器...")
    browser = await uc.start(headless=False)
    tab = await browser.get('https://ticketplus.com.tw')

    # 等待用戶手動導航到訂票頁面
    print("[2/4] 請在瀏覽器中：")
    print("   1. 登入 TicketPlus 帳號")
    print("   2. 選擇一個活動")
    print("   3. 進入訂票頁面（/order/...）")
    print()
    input("按 Enter 鍵繼續測試... (確保已進入訂票頁面)")

    # 檢查當前 URL
    current_url = await tab.evaluate('window.location.href')
    print(f"\n當前 URL: {current_url}")

    if '/order/' not in current_url.lower():
        print("警告：當前不在訂票頁面，測試結果可能不準確")

    print("\n[3/4] 執行 API 檢查...")
    print("-" * 60)

    # API 檢查的 JavaScript（與原始程式碼相同）
    js_check_api = '''
    (async function() {
        try {
            console.log("=== API 檢查開始 ===");

            // 查找 API URL
            const entries = performance.getEntries();
            console.log(`總共 ${entries.length} 個網路請求`);

            let apiUrl = null;
            let allTicketPlusApis = [];

            for (const entry of entries) {
                if (entry.name && entry.name.includes('apis.ticketplus.com.tw')) {
                    allTicketPlusApis.push(entry.name);

                    if (entry.name.includes('apis.ticketplus.com.tw/config/api/')) {
                        if (entry.name.includes('get?productId=') || entry.name.includes('get?ticketAreaId=')) {
                            apiUrl = entry.name;
                            console.log(`找到目標 API: ${apiUrl}`);
                        }
                    }
                }
            }

            console.log(`找到 ${allTicketPlusApis.length} 個 TicketPlus API 請求`);

            if (!apiUrl) {
                return {
                    isPending: false,
                    reason: 'No API URL found',
                    allApis: allTicketPlusApis,
                    totalEntries: entries.length
                };
            }

            console.log(`正在取得 API 資料: ${apiUrl}`);

            // 取得產品資訊
            const response = await fetch(apiUrl);
            const data = await response.json();

            console.log("API 回應資料:", data);

            // 檢查是否為 pending 狀態
            if (data.result && data.result.product && data.result.product.length > 0) {
                const status = data.result.product[0].status;
                console.log(`產品狀態: ${status}`);

                if (status === "pending") {
                    return {
                        isPending: true,
                        reason: 'API status pending',
                        apiUrl: apiUrl,
                        productStatus: status,
                        fullData: data
                    };
                } else {
                    return {
                        isPending: false,
                        reason: `API status is "${status}" (not pending)`,
                        apiUrl: apiUrl,
                        productStatus: status,
                        fullData: data
                    };
                }
            } else {
                return {
                    isPending: false,
                    reason: 'No product data in API response',
                    apiUrl: apiUrl,
                    fullData: data
                };
            }

        } catch (err) {
            console.error("API 檢查錯誤:", err);
            return {
                isPending: false,
                reason: 'API check error: ' + err.message,
                error: err.toString()
            };
        }
    })();
    '''

    # 執行 JavaScript
    result = await tab.evaluate(js_check_api)

    # 顯示結果
    print("\n[4/4] 測試結果")
    print("=" * 60)

    if isinstance(result, dict):
        print(f"✓ API 檢查完成")
        print()
        print(f"  isPending: {result.get('isPending', 'N/A')}")
        print(f"  原因: {result.get('reason', 'N/A')}")

        if 'apiUrl' in result:
            print(f"\n  API URL: {result['apiUrl']}")

        if 'productStatus' in result:
            print(f"  產品狀態: {result['productStatus']}")

        if 'allApis' in result:
            print(f"\n  找到的 TicketPlus APIs ({len(result['allApis'])} 個):")
            for i, api in enumerate(result['allApis'][:5], 1):
                print(f"    {i}. {api}")
            if len(result['allApis']) > 5:
                print(f"    ... 還有 {len(result['allApis']) - 5} 個")

        if 'totalEntries' in result:
            print(f"\n  總網路請求數: {result['totalEntries']}")

        if 'fullData' in result and result['fullData']:
            print(f"\n  完整 API 資料:")
            import json
            print(json.dumps(result['fullData'], indent=2, ensure_ascii=False)[:500] + "...")

    elif isinstance(result, list):
        print(f"✗ 返回類型錯誤: list (預期 dict)")
        print(f"  值: {result}")
    else:
        print(f"✗ 返回類型錯誤: {type(result)}")
        print(f"  值: {result}")

    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)

    # 保持瀏覽器開啟
    input("\n按 Enter 鍵關閉瀏覽器...")

    await browser.stop()

if __name__ == "__main__":
    try:
        asyncio.run(test_ticketplus_api_check())
    except KeyboardInterrupt:
        print("\n測試中斷")
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()
