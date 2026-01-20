// 測試新發現的 API 格式
// 複製到 Console 執行

(async function() {
    console.log("=== 測試新 API 格式 ===\n");

    // 查找新格式的 API
    const entries = performance.getEntries();
    let targetApi = null;

    for (const entry of entries) {
        if (entry.name && entry.name.includes('apis.ticketplus.com.tw/config/api/v1/get?eventId=')) {
            targetApi = entry.name;
            console.log(`找到 API: ${targetApi}\n`);
            break;
        }
    }

    if (!targetApi) {
        console.error("❌ 未找到 eventId API");
        return;
    }

    // 取得 API 資料
    try {
        const response = await fetch(targetApi);
        const data = await response.json();

        console.log("API 完整回應:");
        console.log(data);
        console.log("\n");

        // 檢查各種可能的狀態欄位
        if (data.result) {
            console.log("result 內容:");
            console.log(data.result);
            console.log("\n");

            // 檢查是否有 status 欄位
            if (data.result.status) {
                console.log(`✓ 找到 result.status: ${data.result.status}`);
            }

            // 檢查 product 欄位
            if (data.result.product) {
                console.log("✓ 找到 result.product:");
                console.log(data.result.product);
                if (Array.isArray(data.result.product) && data.result.product[0]) {
                    console.log(`  - product[0].status: ${data.result.product[0].status}`);
                }
            }

            // 檢查 session 欄位
            if (data.result.session) {
                console.log("✓ 找到 result.session:");
                console.log(data.result.session);
                if (Array.isArray(data.result.session) && data.result.session[0]) {
                    console.log(`  - session[0].status: ${data.result.session[0].status}`);
                }
            }

            // 檢查 event 欄位
            if (data.result.event) {
                console.log("✓ 找到 result.event:");
                console.log(data.result.event);
                if (data.result.event.status) {
                    console.log(`  - event.status: ${data.result.event.status}`);
                }
            }
        }

        console.log("\n=== 測試完成 ===");
        console.log("請將上述輸出提供給開發者分析");

    } catch (err) {
        console.error("❌ API 請求錯誤:", err);
    }
})();
