/**
 * ERA TICKET (ticket.com.tw) 測試腳本
 * 用於在瀏覽器 Console 中執行，驗證問題和解決方案
 */

// ============================================================
// Q1: 「尚未開賣」按鈕檢測
// ============================================================

/**
 * 檢測「尚未開賣」按鈕並提取開賣時間
 * 在 UTK0201_00.aspx 頁面執行
 */
function detectComingSoonButton() {
    const buttons = document.querySelectorAll('button.btn-event, button.btn');
    const results = [];

    buttons.forEach((btn, i) => {
        const text = btn.innerText.trim();
        const className = btn.className;
        const disabled = btn.disabled;
        const hasDisabledClass = className.includes('disabled');

        if (text.includes('尚未開賣') || text.includes('啟售')) {
            // 提取開賣時間
            const match = text.match(/(\d{4}\/\d{2}\/\d{2})\s*(\d{2}:\d{2}:\d{2})/);
            let saleTime = null;
            let diffSeconds = null;

            if (match) {
                const dateStr = match[1] + ' ' + match[2];
                const saleDate = new Date(dateStr.replace(/\//g, '-'));
                const now = new Date();
                diffSeconds = Math.floor((saleDate - now) / 1000);
                saleTime = dateStr;
            }

            results.push({
                index: i,
                text: text.replace(/\n/g, ' '),
                className: className,
                htmlDisabled: disabled,
                cssDisabled: hasDisabledClass,
                saleTime: saleTime,
                diffSeconds: diffSeconds,
                diffMinutes: diffSeconds ? Math.floor(diffSeconds / 60) : null
            });
        }
    });

    console.log('=== 「尚未開賣」按鈕檢測結果 ===');
    console.table(results);

    if (results.length > 0) {
        const first = results[0];
        if (first.diffSeconds > 0) {
            console.log(`\n開賣時間: ${first.saleTime}`);
            console.log(`距離開賣: ${first.diffMinutes} 分鐘 (${first.diffSeconds} 秒)`);
        } else if (first.diffSeconds <= 0) {
            console.log('\n已過開賣時間，應該可以購票了！');
        }
    } else {
        console.log('\n未找到「尚未開賣」按鈕');
    }

    return results;
}

// ============================================================
// Q2: 座位結構分析
// ============================================================

/**
 * 分析座位結構，檢查「連號」問題
 * 在 UTK0205_.aspx 頁面執行
 */
function analyzeSeatStructure() {
    const availableSeats = document.querySelectorAll('td[title][style*="icon_chair_empty"]');
    const rowMap = {};
    const warnings = [];

    console.log('=== 座位結構分析 ===');
    console.log(`可選座位總數: ${availableSeats.length}`);

    availableSeats.forEach((seat, i) => {
        const title = seat.getAttribute('title');
        const parts = title.split('-');

        if (parts.length >= 3) {
            const area = parts[0];           // 2樓2D區
            const rowStr = parts[1];         // 8排
            const seatStr = parts[2];        // 13號

            const rowNum = parseInt(rowStr.replace('排', ''));
            const seatNum = parseInt(seatStr.replace('號', ''));
            const domRow = seat.parentElement ? seat.parentElement.rowIndex : -1;
            const domCol = seat.cellIndex;

            if (!rowMap[rowNum]) {
                rowMap[rowNum] = {
                    area: area,
                    seats: [],
                    domRows: new Set()
                };
            }

            rowMap[rowNum].seats.push({
                seatNum: seatNum,
                title: title,
                domRow: domRow,
                domCol: domCol,
                element: seat
            });
            rowMap[rowNum].domRows.add(domRow);
        }
    });

    // 分析每排
    console.log('\n--- 各排座位分布 ---');
    for (const [rowNum, data] of Object.entries(rowMap).sort((a, b) => parseInt(a[0]) - parseInt(b[0]))) {
        data.seats.sort((a, b) => a.seatNum - b.seatNum);
        const seatNums = data.seats.map(s => s.seatNum);
        const domRowsArray = [...data.domRows];

        // 檢查連續性
        let isConsecutive = true;
        for (let i = 1; i < seatNums.length; i++) {
            if (seatNums[i] - seatNums[i - 1] > 2) { // 允許奇偶相鄰
                isConsecutive = false;
                break;
            }
        }

        // 檢查是否跨 DOM 行
        if (domRowsArray.length > 1) {
            warnings.push(`第 ${rowNum} 排的座位分布在多個 DOM 行: ${domRowsArray.join(', ')}`);
        }

        console.log(`${rowNum}排: ${seatNums.length} 個座位 [${seatNums.join(', ')}] ${isConsecutive ? '(連續)' : '(不連續)'} DOM行: ${domRowsArray.join(',')}`);
    }

    // 顯示警告
    if (warnings.length > 0) {
        console.warn('\n--- 警告 ---');
        warnings.forEach(w => console.warn(w));
    }

    return { rowMap, warnings };
}

/**
 * 模擬座位選擇邏輯，檢查是否會跨排
 */
function simulateSeatSelection(ticketNumber = 2, allowNonAdjacent = false) {
    const analysis = analyzeSeatStructure();
    const rowMap = analysis.rowMap;

    console.log(`\n=== 模擬選擇 ${ticketNumber} 張票 (${allowNonAdjacent ? '允許不連續' : '需連續'}) ===`);

    // 按排號排序
    const sortedRows = Object.entries(rowMap)
        .map(([rowNum, data]) => ({ rowNum: parseInt(rowNum), ...data }))
        .sort((a, b) => a.rowNum - b.rowNum);

    for (const row of sortedRows) {
        const seats = row.seats;

        if (seats.length < ticketNumber) {
            console.log(`${row.rowNum}排: 座位不足 (${seats.length} < ${ticketNumber})`);
            continue;
        }

        if (!allowNonAdjacent) {
            // 尋找連續座位
            for (let i = 0; i <= seats.length - ticketNumber; i++) {
                let continuous = true;
                for (let j = 0; j < ticketNumber - 1; j++) {
                    const domGap = seats[i + j + 1].domCol - seats[i + j].domCol;
                    if (domGap > 1) {
                        continuous = false;
                        break;
                    }
                }

                if (continuous) {
                    const selected = seats.slice(i, i + ticketNumber);
                    console.log(`\n選中 ${row.rowNum}排:`);
                    selected.forEach(s => console.log(`  - ${s.title} (DOM: row=${s.domRow}, col=${s.domCol})`));

                    // 高亮選中的座位
                    selected.forEach(s => {
                        s.element.style.outline = '3px solid red';
                    });

                    return selected;
                }
            }
            console.log(`${row.rowNum}排: 找不到 ${ticketNumber} 個連續座位`);
        } else {
            // 不連續模式：選擇中間位置
            const startIdx = Math.floor((seats.length - ticketNumber) / 2);
            const selected = seats.slice(startIdx, startIdx + ticketNumber);
            console.log(`\n選中 ${row.rowNum}排 (不連續模式):`);
            selected.forEach(s => console.log(`  - ${s.title}`));

            selected.forEach(s => {
                s.element.style.outline = '3px solid red';
            });

            return selected;
        }
    }

    console.log('\n未找到符合條件的座位');
    return null;
}

// ============================================================
// Q2: 按鈕選擇器測試
// ============================================================

/**
 * 測試「加入購物車」按鈕選擇器
 */
function testCartButtonSelectors() {
    const selectors = [
        'button.sumitButton[onclick*="addShoppingCart1"]',
        'button.btn.sumitButton',
        'button[onclick*="addShoppingCart1"]',
        'button.sumitButton',
        'button.btn-danger.btn-block',
        'input[id$="AddShopingCart"]'
    ];

    console.log('=== 「加入購物車」按鈕選擇器測試 ===');

    selectors.forEach((selector, i) => {
        try {
            const element = document.querySelector(selector);
            if (element) {
                console.log(`[${i + 1}] ${selector}`);
                console.log(`    找到: <${element.tagName.toLowerCase()} class="${element.className}">${element.innerText.substring(0, 30)}...`);
            } else {
                console.log(`[${i + 1}] ${selector} - 未找到`);
            }
        } catch (e) {
            console.log(`[${i + 1}] ${selector} - 錯誤: ${e.message}`);
        }
    });

    // 尋找所有包含「購物車」的按鈕
    console.log('\n--- 包含「購物車」文字的按鈕 ---');
    const allButtons = document.querySelectorAll('button, input[type="submit"], input[type="button"]');
    allButtons.forEach((btn, i) => {
        const text = btn.innerText || btn.value || '';
        if (text.includes('購物車')) {
            console.log(`[${i}] <${btn.tagName.toLowerCase()} class="${btn.className}">${text}`);
        }
    });
}

/**
 * 測試票別按鈕
 */
function testTicketTypeButtons() {
    const buttons = document.querySelectorAll('button[onclick*="setType"]');

    console.log('=== 票別按鈕測試 ===');
    console.log(`找到 ${buttons.length} 個票別按鈕:`);

    buttons.forEach((btn, i) => {
        console.log(`[${i + 1}] ${btn.innerText.trim()} - disabled: ${btn.disabled}, class: ${btn.className}`);
    });
}

// ============================================================
// Q3: 延遲分析
// ============================================================

/**
 * 測量 AJAX 請求時間
 */
function measureAjaxTime() {
    const originalFetch = window.fetch;
    const originalXHR = XMLHttpRequest.prototype.open;

    console.log('=== AJAX 時間測量已啟用 ===');
    console.log('進行操作後會顯示請求時間');

    // 攔截 fetch
    window.fetch = async function (...args) {
        const start = performance.now();
        const response = await originalFetch.apply(this, args);
        const end = performance.now();
        console.log(`[Fetch] ${args[0]} - ${Math.round(end - start)}ms`);
        return response;
    };

    // 攔截 XHR
    XMLHttpRequest.prototype.open = function (...args) {
        this._url = args[1];
        this._startTime = performance.now();
        this.addEventListener('loadend', function () {
            const end = performance.now();
            console.log(`[XHR] ${this._url} - ${Math.round(end - this._startTime)}ms`);
        });
        return originalXHR.apply(this, args);
    };
}

// ============================================================
// 主選單
// ============================================================

console.log(`
=============================================
ERA TICKET 測試腳本
=============================================

可用函數:

Q1 相關:
  detectComingSoonButton()     - 檢測「尚未開賣」按鈕

Q2 相關:
  analyzeSeatStructure()       - 分析座位結構
  simulateSeatSelection(2)     - 模擬選擇 2 張票
  testCartButtonSelectors()    - 測試購物車按鈕選擇器
  testTicketTypeButtons()      - 測試票別按鈕

Q3 相關:
  measureAjaxTime()            - 測量 AJAX 請求時間

直接在 Console 輸入函數名稱執行
=============================================
`);
