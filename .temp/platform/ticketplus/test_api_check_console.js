/**
 * TicketPlus API 檢查測試 - 瀏覽器 Console 版本
 *
 * 使用方式：
 * 1. 在 TicketPlus 訂票頁面（/order/...）打開瀏覽器開發者工具（F12）
 * 2. 切換到 Console 標籤
 * 3. 複製並貼上整個檔案的內容
 * 4. 按 Enter 執行
 */

(async function testTicketPlusAPI() {
    console.log("=".repeat(60));
    console.log("TicketPlus API 檢查測試工具 (Console 版本)");
    console.log("=".repeat(60));
    console.log("");

    // 檢查當前 URL
    const currentUrl = window.location.href;
    console.log(`當前 URL: ${currentUrl}`);

    if (!currentUrl.includes('/order/')) {
        console.warn("⚠️ 警告：當前不在訂票頁面 (/order/)，測試結果可能不準確");
    }

    console.log("\n" + "-".repeat(60));
    console.log("開始 API 檢查...");
    console.log("-".repeat(60));

    try {
        // 查找 API URL
        const entries = performance.getEntries();
        console.log(`📊 總共 ${entries.length} 個網路請求`);

        let apiUrl = null;
        let allTicketPlusApis = [];
        let configApis = [];

        for (const entry of entries) {
            if (entry.name && entry.name.includes('apis.ticketplus.com.tw')) {
                allTicketPlusApis.push(entry.name);

                if (entry.name.includes('apis.ticketplus.com.tw/config/api/')) {
                    configApis.push(entry.name);

                    if (entry.name.includes('get?productId=') || entry.name.includes('get?ticketAreaId=')) {
                        apiUrl = entry.name;
                        console.log(`✓ 找到目標 API: ${apiUrl}`);
                    }
                }
            }
        }

        console.log(`\n📡 TicketPlus API 統計:`);
        console.log(`   - 所有 TicketPlus APIs: ${allTicketPlusApis.length} 個`);
        console.log(`   - Config APIs: ${configApis.length} 個`);

        if (allTicketPlusApis.length > 0) {
            console.log(`\n📋 前 5 個 TicketPlus APIs:`);
            allTicketPlusApis.slice(0, 5).forEach((api, i) => {
                console.log(`   ${i + 1}. ${api}`);
            });
            if (allTicketPlusApis.length > 5) {
                console.log(`   ... 還有 ${allTicketPlusApis.length - 5} 個`);
            }
        }

        if (!apiUrl) {
            console.error("❌ 未找到目標 API URL");
            console.log("\n可能的原因：");
            console.log("  1. 頁面尚未載入完成");
            console.log("  2. 不在訂票頁面");
            console.log("  3. API URL 格式已變更");
            console.log("\n建議：重新整理頁面後再試一次");
            return {
                isPending: false,
                reason: 'No API URL found',
                allApis: allTicketPlusApis
            };
        }

        console.log(`\n🔄 正在取得 API 資料...`);
        console.log(`   URL: ${apiUrl}`);

        // 取得產品資訊
        const response = await fetch(apiUrl);
        const data = await response.json();

        console.log(`\n✓ API 回應成功`);
        console.log(`\n📦 完整 API 資料:`);
        console.log(data);

        // 檢查是否為 pending 狀態
        if (data.result && data.result.product && data.result.product.length > 0) {
            const product = data.result.product[0];
            const status = product.status;

            console.log(`\n📊 產品資訊:`);
            console.log(`   - 狀態: ${status}`);
            if (product.name) console.log(`   - 名稱: ${product.name}`);
            if (product.startTime) console.log(`   - 開始時間: ${product.startTime}`);
            if (product.endTime) console.log(`   - 結束時間: ${product.endTime}`);

            const isPending = status === "pending";

            console.log("\n" + "=".repeat(60));
            if (isPending) {
                console.log("🟡 結果: API 狀態為 PENDING");
                console.log("   → 程式會自動重載頁面");
            } else {
                console.log(`🟢 結果: API 狀態為 "${status}" (非 pending)`);
                console.log("   → 程式不會因 API 狀態而重載");
            }
            console.log("=".repeat(60));

            return {
                isPending: isPending,
                reason: isPending ? 'API status pending' : `API status is "${status}"`,
                apiUrl: apiUrl,
                productStatus: status,
                productData: product,
                fullData: data
            };

        } else {
            console.warn("⚠️ API 回應中無產品資料");
            console.log("\n" + "=".repeat(60));
            console.log("🟢 結果: 無產品資料 (非 pending)");
            console.log("   → 程式不會因 API 狀態而重載");
            console.log("=".repeat(60));

            return {
                isPending: false,
                reason: 'No product data in API response',
                apiUrl: apiUrl,
                fullData: data
            };
        }

    } catch (err) {
        console.error("❌ API 檢查錯誤:", err);
        console.log("\n錯誤詳情:");
        console.error(err);

        console.log("\n" + "=".repeat(60));
        console.log("🔴 結果: 發生錯誤");
        console.log("=".repeat(60));

        return {
            isPending: false,
            reason: 'API check error: ' + err.message,
            error: err.toString()
        };
    }
})().then(result => {
    console.log("\n\n📋 測試結果摘要:");
    console.log(result);
    console.log("\n✅ 測試完成！");
});
