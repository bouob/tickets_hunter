// TicketPlus API 檢查 - 簡化版（可直接貼到 Console）
// 使用方式：複製整個內容 → 貼到 Console → 按 Enter

(async function() {
    console.log("=== TicketPlus API 檢查開始 ===\n");

    // 1. 查找 API URL
    const entries = performance.getEntries();
    console.log(`總網路請求數: ${entries.length}`);

    let apiUrl = null;
    const allApis = [];

    for (const entry of entries) {
        if (entry.name && entry.name.includes('apis.ticketplus.com.tw/config/api/')) {
            allApis.push(entry.name);
            if (entry.name.includes('get?productId=') || entry.name.includes('get?ticketAreaId=')) {
                apiUrl = entry.name;
            }
        }
    }

    console.log(`找到 ${allApis.length} 個 config API`);
    if (allApis.length > 0) {
        console.log("API URLs:");
        allApis.forEach((url, i) => console.log(`  ${i+1}. ${url}`));
    }

    if (!apiUrl) {
        console.error("❌ 未找到目標 API");
        console.log("\n建議：重新整理頁面後再試");
        return;
    }

    console.log(`\n✓ 目標 API: ${apiUrl}\n`);

    // 2. 取得 API 資料
    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        console.log("API 回應資料:");
        console.log(data);

        // 3. 檢查產品狀態
        if (data.result && data.result.product && data.result.product.length > 0) {
            const status = data.result.product[0].status;
            console.log(`\n產品狀態: ${status}`);

            if (status === "pending") {
                console.log("\n🟡 結果: 狀態為 PENDING");
                console.log("   → 程式會自動重載頁面");
            } else {
                console.log(`\n🟢 結果: 狀態為 "${status}" (非 pending)`);
                console.log("   → 程式不會因 API 狀態而重載");
            }
        } else {
            console.log("\n⚠️ API 回應中無產品資料");
        }

    } catch (err) {
        console.error("❌ API 請求錯誤:", err);
    }

    console.log("\n=== 測試完成 ===");
})();
