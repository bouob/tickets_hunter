// 測試修復後的 API 檢查邏輯
// 複製到 Console 執行

(async function() {
    console.log("=".repeat(60));
    console.log("測試修復後的 API 檢查邏輯");
    console.log("=".repeat(60));
    console.log("");

    try {
        // 查找 API URL（新邏輯）
        const entries = performance.getEntries();
        let apiUrl = null;

        for (const entry of entries) {
            if (entry.name && entry.name.includes('apis.ticketplus.com.tw/config/api/')) {
                // 支援舊格式和新格式的 API
                if (entry.name.includes('get?productId=') ||
                    entry.name.includes('get?ticketAreaId=') ||
                    entry.name.includes('get?eventId=')) {
                    apiUrl = entry.name;
                    break;
                }
            }
        }

        if (!apiUrl) {
            console.error("❌ 未找到 API URL");
            return { isPending: false, reason: 'No API URL found' };
        }

        console.log(`✓ 找到 API URL:`);
        console.log(`  ${apiUrl}\n`);

        // 取得產品資訊
        const response = await fetch(apiUrl);
        const data = await response.json();

        console.log("API 回應資料:");
        console.log(data);
        console.log("");

        // 檢查是否為 pending 狀態（新邏輯：支援多種資料結構）
        let isPending = false;
        let reason = 'API status not pending';

        if (data.result) {
            // 檢查 product 欄位（舊格式）
            if (data.result.product && data.result.product.length > 0) {
                console.log(`檢查 product[0].status: ${data.result.product[0].status}`);
                if (data.result.product[0].status === "pending") {
                    isPending = true;
                    reason = 'API status pending (product)';
                }
            }

            // 檢查 session 欄位（新格式可能使用）
            if (data.result.session && data.result.session.length > 0) {
                console.log(`檢查 session[0].status: ${data.result.session[0].status}`);
                if (data.result.session[0].status === "pending") {
                    isPending = true;
                    reason = 'API status pending (session)';
                }
            }

            // 檢查 event 欄位
            if (data.result.event && data.result.event.status) {
                console.log(`檢查 event.status: ${data.result.event.status}`);
                if (data.result.event.status === "pending") {
                    isPending = true;
                    reason = 'API status pending (event)';
                }
            }

            // 檢查 result 直接的 status
            if (data.result.status) {
                console.log(`檢查 result.status: ${data.result.status}`);
                if (data.result.status === "pending") {
                    isPending = true;
                    reason = 'API status pending (result)';
                }
            }
        }

        console.log("\n" + "=".repeat(60));
        if (isPending) {
            console.log("🟡 結果: isPending = TRUE");
            console.log(`   原因: ${reason}`);
            console.log("   → 程式會自動重載頁面");
        } else {
            console.log("🟢 結果: isPending = FALSE");
            console.log(`   原因: ${reason}`);
            console.log("   → 程式不會因 API 狀態而重載");
        }
        console.log("=".repeat(60));

        return { isPending, reason, apiUrl };

    } catch (err) {
        console.error("❌ 測試過程發生錯誤:", err);
        return { isPending: false, reason: 'API check error: ' + err.message };
    }
})().then(result => {
    console.log("\n📋 測試結果摘要:");
    console.log(result);
    console.log("\n✅ 測試完成！");
});
