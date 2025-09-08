#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KKTIX 專用 Chrome Debug 啟動工具
專門為 KKTIX 搶票建立獨立的 Chrome Debug 實例
"""

import os
import sys
import time
import json
import subprocess
import requests
import webbrowser

def find_chrome_path():
    """找尋 Chrome 執行檔路徑"""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Google\Chrome\Application\chrome.exe')
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    return None

def find_available_debug_port():
    """找尋可用的除錯端口"""
    import socket
    
    # 嘗試的端口範圍
    ports_to_try = [9223, 9224, 9225, 9222]  # 9222 放最後，優先用其他端口
    
    for port in ports_to_try:
        try:
            # 檢查端口是否已被占用
            response = requests.get(f"http://localhost:{port}/json", timeout=1)
            if response.status_code == 200:
                print(f"端口 {port} 已有 Chrome 實例運行")
                continue
        except requests.exceptions.RequestException:
            # 端口沒有回應，表示可以使用
            return port
    
    # 如果都被占用，使用隨機端口
    import random
    return random.randint(9230, 9240)

def start_chrome_debug():
    """啟動 Chrome Debug 模式"""
    chrome_path = find_chrome_path()
    if not chrome_path:
        print("找不到 Chrome 瀏覽器")
        return False
    
    # 找尋可用的除錯端口
    debug_port = find_available_debug_port()
    print(f"啟動 Chrome Debug 模式（端口: {debug_port}）...")
    
    # 使用時間戳確保目錄唯一
    import time
    timestamp = int(time.time())
    debug_dir = os.path.join(os.environ.get('TEMP', ''), f'maxbot_chrome_{timestamp}')
    
    cmd = [
        chrome_path,
        f'--remote-debugging-port={debug_port}',
        f'--user-data-dir={debug_dir}',
        '--no-first-run',
        '--disable-features=TranslateUI',
        '--new-window'  # 強制開新視窗
    ]
    
    try:
        # 啟動 Chrome（背景執行）
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Chrome Debug 模式啟動中...")
        
        # 等待 Chrome 啟動
        for i in range(10):
            try:
                response = requests.get(f"http://localhost:{debug_port}/json", timeout=2)
                if response.status_code == 200:
                    print(f"Chrome Debug 模式就緒 ({i+1}秒)")
                    # 將端口號保存到檔案供主程式讀取
                    with open('maxbot_chrome_port.txt', 'w') as f:
                        f.write(str(debug_port))
                    return debug_port
            except:
                pass
            time.sleep(1)
            print(f"等待 Chrome 啟動... ({i+1}/10)")
        
        print("Chrome 啟動較慢，但應該可以繼續")
        # 仍然保存端口號
        with open('maxbot_chrome_port.txt', 'w') as f:
            f.write(str(debug_port))
        return debug_port
        
    except Exception as e:
        print(f"Chrome 啟動失敗: {e}")
        return False

def load_settings():
    """載入設定檔案"""
    settings_files = ['settings.json', 'MAXBOT_CONFIG.json']
    
    for filename in settings_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                continue
    return None




def main():
    """主程式"""
    print("KKTIX Chrome Debug 啟動工具")
    print("="*40)
    
    # 啟動 Chrome Debug 模式
    debug_port = start_chrome_debug()
    if not debug_port:
        print("Chrome Debug 模式啟動失敗")
        input("按 Enter 鍵退出...")
        return
    
    print(f"\nChrome Debug 模式已啟動（端口: {debug_port}）")
    print("接下來請:")
    print("1. 在新開的 Chrome 中前往 KKTIX 網站")
    print("2. 完成登入")
    print("\n保持此 Chrome 視窗開啟，程式會自動連接")
    
    print("\nChrome Debug 模式設定完成！")
    print("接下來請手動執行設定介面:")
    print("   網頁版: python settings.py") 
    print("   桌面版: python settings_old.py")
    
    input("\n按 Enter 鍵退出...")

if __name__ == "__main__":
    main()