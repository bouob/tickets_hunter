#!/usr/bin/env python3
#encoding=utf-8
try:
    # for Python2
    import tkMessageBox as messagebox
    import ttk
    from Tkinter import *
except ImportError:
    # for Python3
    try:
        import tkinter.font as tkfont
        from tkinter import *
        from tkinter import messagebox, ttk
        from tkinter.filedialog import asksaveasfilename
    except Exception as e:
        pass

import asyncio
import base64
import json
import os
import platform
import ssl
import subprocess
import sys
import threading
import time
import warnings
import webbrowser
from datetime import datetime

import pyperclip
import tornado
from tornado.web import Application
from urllib3.exceptions import InsecureRequestWarning

import util

try:
    import ddddocr
except Exception as exc:
    pass

CONST_APP_VERSION = "MaxBot (2024.04.08)"

CONST_MAXBOT_ANSWER_ONLINE_FILE = "MAXBOT_ONLINE_ANSWER.txt"
CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_EXTENSION_NAME = "Maxbotplus_1.0.0"
CONST_MAXBOT_EXTENSION_STATUS_JSON = "status.json"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_QUESTION_FILE = "MAXBOT_QUESTION.txt"

CONST_SERVER_PORT = 16888

CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_CENTER = "center"
CONST_RANDOM = "random"
CONST_SELECT_ORDER_DEFAULT = CONST_RANDOM
CONST_SELECT_OPTIONS_DEFAULT = (CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_CENTER, CONST_RANDOM)
CONST_EXCLUDE_DEFAULT = "\"輪椅\",\"身障\",\"身心 障礙\",\"Restricted View\",\"燈柱遮蔽\",\"視線不完整\""
CONST_CAPTCHA_SOUND_FILENAME_DEFAULT = "ding-dong.wav"
CONST_HOMEPAGE_DEFAULT = "https://tixcraft.com"

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

CONST_WEBDRIVER_TYPE_SELENIUM = "selenium"
CONST_WEBDRIVER_TYPE_UC = "undetected_chromedriver"
CONST_WEBDRIVER_TYPE_DP = "DrissionPage"
CONST_WEBDRIVER_TYPE_NODRIVER = "nodriver"

CONST_SUPPORTED_SITES = ["https://kktix.com"
    ,"https://tixcraft.com (拓元)"
    ,"https://ticketmaster.sg"
    #,"https://ticketmaster.com"
    ,"https://teamear.tixcraft.com/ (添翼)"
    ,"https://www.indievox.com/ (獨立音樂)"
    ,"https://www.famiticket.com.tw (全網)"
    ,"https://ticket.ibon.com.tw/"
    ,"https://kham.com.tw/ (寬宏)"
    ,"https://ticket.com.tw/ (年代)"
    ,"https://tickets.udnfunlife.com/ (udn售票網)"
    ,"https://ticketplus.com.tw/ (遠大)"
    ,"===[香港或南半球的系統]==="
    ,"http://www.urbtix.hk/ (城市)"
    ,"https://www.cityline.com/ (買飛)"
    ,"https://hotshow.hkticketing.com/ (快達票)"
    ,"https://ticketing.galaxymacau.com/ (澳門銀河)"
    ,"http://premier.ticketek.com.au"
    ]

warnings.simplefilter('ignore',InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

translate={}

URL_DONATE = 'https://max-everyday.com/about/#donate'
URL_HELP = 'https://max-everyday.com/2018/03/tixcraft-bot/'
URL_RELEASE = 'https://github.com/max32002/tixcraft_bot/releases'
URL_FB = 'https://www.facebook.com/maxbot.ticket'
URL_CHROME_DRIVER = 'https://chromedriver.chromium.org/'
URL_FIREFOX_DRIVER = 'https://github.com/mozilla/geckodriver/releases'
URL_EDGE_DRIVER = 'https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/'

GLOBAL_SERVER_SHUTDOWN = False

def load_translate():
    translate = {}
    en_us={}
    en_us["homepage"] = 'Homepage'
    en_us["browser"] = 'Browser'
    en_us["language"] = 'Language'
    en_us["ticket_number"] = 'Ticker Number'

    en_us["enable"] = 'Enable'
    en_us["recommand_enable"] = "Recommended to enable"

    en_us["auto_press_next_step_button"] = 'KKTIX Press Next Step Button'
    en_us["auto_fill_ticket_number"] = 'Auto Fill Ticket Number'
    en_us["and"] = 'And with'

    en_us["local_dictionary"] = 'Local Dictionary'
    en_us["remote_url"] = 'Remote URL'
    en_us["server_url"] = 'Server URL'
    en_us["auto_guess_options"] = 'Guess Options in Question'
    en_us["user_guess_string"] = 'Fill Answers in Question'
    en_us["preview"] = 'Preview'
    en_us["question"] = 'Question'
    en_us["answer"] = 'Answer'

    en_us["date_auto_select"] = 'Date Auto Select'
    en_us["date_select_order"] = 'Date select order'
    en_us["date_keyword"] = 'Date Keyword'
    en_us["pass_date_is_sold_out"] = 'Pass date is sold out'
    en_us["auto_reload_coming_soon_page"] = 'Reload coming soon page'
    en_us["auto_reload_page_interval"] = 'Reload page interval(sec.)'
    en_us["kktix_status_api"] = 'KKTIX status API'
    en_us["max_dwell_time"] = 'KKTIX dwell time(sec.)'
    en_us["reset_browser_interval"] = 'Reset browser interval(sec.)'
    en_us["proxy_server_port"] = 'Proxy IP:PORT'
    en_us["window_size"] = 'Window size'

    en_us["area_select_order"] = 'Area select order'
    en_us["area_keyword"] = 'Area Keyword'
    en_us["area_auto_select"] = 'Area Auto Select'
    en_us["keyword_exclude"] = 'Keyword Exclude'
    en_us["keyword_usage"] = 'Each keyword need double quotes, separated by comma,\nUse space in keyword as AND logic.\nAppend ,\"\" to match all.'

    en_us["ocr_captcha"] = 'OCR captcha'
    en_us["ocr_captcha_ddddocr_beta"] = 'ddddocr beta'
    en_us["ocr_captcha_force_submit"] = 'Away from keyboard'
    en_us["ocr_captcha_image_source"] = 'OCR image source'
    en_us["ocr_captcha_not_support_arm"] = 'ddddocr only supports Intel CPU'
    en_us["webdriver_type"] = 'WebDriver type'
    en_us["headless"] = 'Headless mode'
    # Make the operation more talkative
    en_us["verbose"] = 'Verbose mode'
    en_us["running_status"] = 'Running Status'
    en_us["running_url"] = 'Running URL'
    en_us["system_clock"] = 'System Clock'
    en_us["idle_keyword"] = 'Idle Keyword'
    en_us["resume_keyword"] = 'Resume Keyword'
    en_us["idle_keyword_second"] = 'Idle Keyword (second)'
    en_us["resume_keyword_second"] = 'Resume Keyword (second)'
    
    en_us["status_idle"] = 'Idle'
    en_us["status_paused"] = 'Paused'
    en_us["status_enabled"] = 'Enabled'
    en_us["status_running"] = 'Running'

    en_us["idle"] = 'Idle'
    en_us["resume"] = 'Resume'

    en_us["preference"] = 'Preference'
    en_us["advanced"] = 'Advanced'
    en_us["verification_word"] = "Verification"
    en_us["maxbot_server"] = 'Server'
    en_us["autofill"] = 'Autofill'
    en_us["runtime"] = 'Runtime'
    en_us["about"] = 'About'

    en_us["run"] = 'Run'
    en_us["save"] = 'Save'
    en_us["exit"] = 'Close'
    en_us["copy"] = 'Copy'
    en_us["restore_defaults"] = 'Restore Defaults'
    en_us["config_launcher"] = 'Launcher'
    en_us["done"] = 'Done'

    en_us["tixcraft_sid"] = 'Tixcraft family cookie SID'
    en_us["ibon_ibonqware"] = 'ibon cookie ibonqware'
    en_us["facebook_account"] = 'Facebook account'
    en_us["kktix_account"] = 'KKTIX account'
    en_us["fami_account"] = 'FamiTicket account'
    en_us["cityline_account"] = 'cityline account'
    en_us["urbtix_account"] = 'URBTIX account'
    en_us["hkticketing_account"] = 'HKTICKETING account'
    en_us["kham_account"] = 'KHAM account'
    en_us["ticket_account"] = 'TICKET account'
    en_us["udn_account"] = 'UDN account'
    en_us["ticketplus_account"] = 'TicketPlus account'

    en_us["password"] = 'Password'
    en_us["facebook_password"] = 'Facebook password'
    en_us["kktix_password"] = 'KKTIX password'
    en_us["fami_password"] = 'FamiTicket password'
    en_us["cityline_password"] = 'cityline password'
    en_us["urbtix_password"] = 'URBTIX password'
    en_us["hkticketing_password"] = 'HKTICKETING password'
    en_us["kham_password"] = 'KHAM password'
    en_us["ticket_password"] = 'TICKET password'
    en_us["udn_password"] = 'UDN password'
    en_us["ticketplus_password"] = 'TicketPlus password'
    en_us["save_password_alert"] = 'Saving passwords to config file may expose your passwords.'

    en_us["play_ticket_sound"] = 'Play sound when ticketing'
    en_us["play_order_sound"] = 'Play sound when ordering'
    en_us["play_sound_filename"] = 'sound filename'
    
    en_us["chrome_extension"] = "Chrome Browser Extension"
    en_us["disable_adjacent_seat"] = "Disable Adjacent Seat"
    en_us["hide_some_image"] = "Hide Some Images"
    en_us["block_facebook_network"] = "Block Facebook Network"

    en_us["maxbot_slogan"] = 'MaxBot is a FREE and open source bot program. Wish you good luck.'
    en_us["donate"] = 'Donate'
    en_us["help"] = 'Help'
    en_us["release"] = 'Release'

    zh_tw={}
    zh_tw["homepage"] = '售票網站'
    zh_tw["browser"] = '瀏覽器'
    zh_tw["language"] = '語言'
    zh_tw["ticket_number"] = '門票張數'

    zh_tw["enable"] = '啟用'
    zh_tw["recommand_enable"] = "建議啟用"
    zh_tw["auto_press_next_step_button"] = 'KKTIX點選下一步按鈕'
    zh_tw["auto_fill_ticket_number"] = '自動輸入張數'
    zh_tw["and"] = '而且（同列）'

    zh_tw["local_dictionary"] = '使用者自定字典'
    zh_tw["remote_url"] = '遠端網址'
    zh_tw["server_url"] = '伺服器網址'
    zh_tw["auto_guess_options"] = '自動猜測驗證問題'
    zh_tw["user_guess_string"] = '驗證問題中的答案清單'
    zh_tw["preview"] = '預覽'
    zh_tw["question"] = '驗證問題'
    zh_tw["answer"] = '答案'

    zh_tw["date_auto_select"] = '日期自動點選'
    zh_tw["date_select_order"] = '日期排序方式'
    zh_tw["date_keyword"] = '日期關鍵字'
    zh_tw["pass_date_is_sold_out"] = '避開「搶購一空」的日期'
    zh_tw["auto_reload_coming_soon_page"] = '自動刷新倒數中的日期頁面'
    zh_tw["auto_reload_page_interval"] = '自動刷新頁面間隔(秒)'
    zh_tw["kktix_status_api"] = 'KKTIX購票狀態API'
    zh_tw["max_dwell_time"] = 'KKTIX購票最長停留(秒)'
    zh_tw["reset_browser_interval"] = '重新啟動瀏覽器間隔(秒)'
    zh_tw["proxy_server_port"] = 'Proxy IP:PORT'
    zh_tw["window_size"] = '瀏覽器視窗大小'

    zh_tw["area_select_order"] = '區域排序方式'
    zh_tw["area_keyword"] = '區域關鍵字'
    zh_tw["area_auto_select"] = '區域自動點選'
    zh_tw["keyword_exclude"] = '排除關鍵字'
    zh_tw["keyword_usage"] = '每組關鍵字需要雙引號, 用逗號分隔, \n在關鍵字中使用空格作為 AND 邏輯。\n加入 ,\"\" 代表符合所有關鍵字'

    zh_tw["ocr_captcha"] = '猜測驗證碼'
    zh_tw["ocr_captcha_ddddocr_beta"] = 'ddddocr beta'
    zh_tw["ocr_captcha_force_submit"] = '掛機模式'
    zh_tw["ocr_captcha_image_source"] = 'OCR圖片取得方式'
    zh_tw["ocr_captcha_not_support_arm"] = 'ocr 只支援 Intel CPU'
    zh_tw["webdriver_type"] = 'WebDriver類別'
    zh_tw["headless"] = '無圖形界面模式'
    zh_tw["verbose"] = '輸出詳細除錯訊息'
    zh_tw["running_status"] = '執行狀態'
    zh_tw["running_url"] = '執行網址'
    zh_tw["system_clock"] = '系統時鐘'
    zh_tw["idle_keyword"] = '暫停關鍵字'
    zh_tw["resume_keyword"] = '接續關鍵字'
    zh_tw["idle_keyword_second"] = '暫停關鍵字(秒)'
    zh_tw["resume_keyword_second"] = '接續關鍵字(秒)'

    zh_tw["status_idle"] = '閒置中'
    zh_tw["status_paused"] = '已暫停'
    zh_tw["status_enabled"] = '已啟用'
    zh_tw["status_running"] = '執行中'

    zh_tw["idle"] = '暫停搶票'
    zh_tw["resume"] = '接續搶票'

    zh_tw["preference"] = '偏好設定'
    zh_tw["advanced"] = '進階設定'
    zh_tw["verification_word"] = "驗證問題"
    zh_tw["maxbot_server"] = '伺服器'
    zh_tw["autofill"] = '自動填表單'
    zh_tw["runtime"] = '執行階段'
    zh_tw["about"] = '關於'

    zh_tw["run"] = '搶票'
    zh_tw["save"] = '存檔'
    zh_tw["exit"] = '關閉'
    zh_tw["copy"] = '複製'
    zh_tw["restore_defaults"] = '恢復預設值'
    zh_tw["config_launcher"] = '設定檔管理'
    zh_tw["done"] = '完成'

    zh_tw["tixcraft_sid"] = '拓元家族 cookie SID'
    zh_tw["ibon_ibonqware"] = 'ibon cookie ibonqware'
    zh_tw["facebook_account"] = 'Facebook 帳號'
    zh_tw["kktix_account"] = 'KKTIX 帳號'
    zh_tw["fami_account"] = 'FamiTicket 帳號'
    zh_tw["cityline_account"] = 'cityline 帳號'
    zh_tw["urbtix_account"] = 'URBTIX 帳號'
    zh_tw["hkticketing_account"] = 'HKTICKETING 帳號'
    zh_tw["kham_account"] = '寬宏 帳號'
    zh_tw["ticket_account"] = '年代 帳號'
    zh_tw["udn_account"] = 'UDN 帳號'
    zh_tw["ticketplus_account"] = '遠大 帳號'

    zh_tw["password"] = '密碼'
    zh_tw["facebook_password"] = 'Facebook 密碼'
    zh_tw["kktix_password"] = 'KKTIX 密碼'
    zh_tw["fami_password"] = 'FamiTicket 密碼'
    zh_tw["cityline_password"] = 'cityline 密碼'
    zh_tw["urbtix_password"] = 'URBTIX 密碼'
    zh_tw["hkticketing_password"] = 'HKTICKETING 密碼'
    zh_tw["kham_password"] = '寬宏 密碼'
    zh_tw["ticket_password"] = '年代 密碼'
    zh_tw["udn_password"] = 'UDN 密碼'
    zh_tw["ticketplus_password"] = '遠大 密碼'
    zh_tw["save_password_alert"] = '將密碼保存到設定檔中可能會讓您的密碼被盜。'

    zh_tw["play_ticket_sound"] = '有票時播放音效'
    zh_tw["play_order_sound"] = '訂購時播放音效'
    zh_tw["play_sound_filename"] = '音效檔'
    
    zh_tw["chrome_extension"] = "Chrome 瀏覽器擴充功能"
    zh_tw["disable_adjacent_seat"] = "允許不連續座位"
    zh_tw["hide_some_image"] = "隱藏部份圖片"
    zh_tw["block_facebook_network"] = "擋掉 Facebook 連線"

    zh_tw["maxbot_slogan"] = 'MaxBot是一個免費、開放原始碼的搶票機器人。\n祝您搶票成功。'
    zh_tw["donate"] = '打賞'
    zh_tw["release"] = '所有可用版本'
    zh_tw["help"] = '使用教學'

    zh_cn={}
    zh_cn["homepage"] = '售票网站'
    zh_cn["browser"] = '浏览器'
    zh_cn["language"] = '语言'
    zh_cn["ticket_number"] = '门票张数'

    zh_cn["enable"] = '启用'
    zh_cn["recommand_enable"] = "建议启用"

    zh_cn["auto_press_next_step_button"] = 'KKTIX自动点选下一步按钮'
    zh_cn["auto_fill_ticket_number"] = '自动输入张数'
    zh_cn["and"] = '而且（同列）'

    zh_cn["local_dictionary"] = '本地字典'
    zh_cn["remote_url"] = '远端网址'
    zh_cn["server_url"] = '服务器地址'
    zh_cn["auto_guess_options"] = '自动猜测验证问题'
    zh_cn["user_guess_string"] = '验证问题的答案列表'
    zh_cn["preview"] = '预览'
    zh_cn["question"] = '验证问题'
    zh_cn["answer"] = '答案'

    zh_cn["date_auto_select"] = '日期自动点选'
    zh_cn["date_select_order"] = '日期排序方式'
    zh_cn["date_keyword"] = '日期关键字'
    zh_cn["pass_date_is_sold_out"] = '避开“抢购一空”的日期'
    zh_cn["auto_reload_coming_soon_page"] = '自动刷新倒数中的日期页面'
    zh_cn["auto_reload_page_interval"] = '重新加载间隔(秒)'
    zh_cn["kktix_status_api"] = 'KKTIX购票状态API'
    zh_cn["max_dwell_time"] = '购票网页最长停留(秒)'
    zh_cn["reset_browser_interval"] = '重新启动浏览器间隔(秒)'
    zh_cn["proxy_server_port"] = 'Proxy IP:PORT'
    zh_cn["window_size"] = '浏览器窗口大小'

    zh_cn["area_select_order"] = '区域排序方式'
    zh_cn["area_keyword"] = '区域关键字'
    zh_cn["area_auto_select"] = '区域自动点选'
    zh_cn["keyword_exclude"] = '排除关键字'
    zh_cn["keyword_usage"] = '每组关键字需要双引号, 用逗号分隔, \n在关键字中使用空格作为 AND 逻辑。\n附加 ,\"\" 以匹配所有结果。'

    zh_cn["ocr_captcha"] = '猜测验证码'
    zh_cn["ocr_captcha_ddddocr_beta"] = 'ddddocr beta'
    zh_cn["ocr_captcha_force_submit"] = '挂机模式'
    zh_cn["ocr_captcha_image_source"] = 'OCR图像源'
    zh_cn["ocr_captcha_not_support_arm"] = 'ddddocr 仅支持 Intel CPU'
    zh_cn["webdriver_type"] = 'WebDriver类别'
    zh_cn["headless"] = '无图形界面模式'
    zh_cn["verbose"] = '输出详细除错讯息'
    zh_cn["running_status"] = '执行状态'
    zh_cn["running_url"] = '执行网址'
    zh_cn["system_clock"] = '系统时钟'
    zh_cn["idle_keyword"] = '暂停关键字'
    zh_cn["resume_keyword"] = '接续关键字'
    zh_cn["idle_keyword_second"] = '暂停关键字(秒)'
    zh_cn["resume_keyword_second"] = '接续关键字(秒)'
    
    zh_cn["status_idle"] = '闲置中'
    zh_cn["status_paused"] = '已暂停'
    zh_cn["status_enabled"] = '已启用'
    zh_cn["status_running"] = '执行中'

    zh_cn["idle"] = '暂停抢票'
    zh_cn["resume"] = '接续抢票'

    zh_cn["preference"] = '偏好设定'
    zh_cn["advanced"] = '进阶设定'
    zh_cn["verification_word"] = "验证字"
    zh_cn["maxbot_server"] = '伺服器'
    zh_cn["autofill"] = '自动填表单'
    zh_cn["runtime"] = '运行'
    zh_cn["about"] = '关于'
    zh_cn["copy"] = '复制'

    zh_cn["run"] = '抢票'
    zh_cn["save"] = '存档'
    zh_cn["exit"] = '关闭'
    zh_cn["copy"] = '复制'
    zh_cn["restore_defaults"] = '恢复默认值'
    zh_cn["config_launcher"] = '设定档管理'
    zh_cn["done"] = '完成'

    zh_cn["tixcraft_sid"] = '拓元家族 cookie SID'
    zh_cn["ibon_ibonqware"] = 'ibon cookie ibonqware'
    zh_cn["facebook_account"] = 'Facebook 帐号'
    zh_cn["kktix_account"] = 'KKTIX 帐号'
    zh_cn["fami_account"] = 'FamiTicket 帐号'
    zh_cn["cityline_account"] = 'cityline 帐号'
    zh_cn["urbtix_account"] = 'URBTIX 帐号'
    zh_cn["hkticketing_account"] = 'HKTICKETING 帐号'
    zh_cn["kham_account"] = '宽宏 帐号'
    zh_cn["ticket_account"] = '年代 帐号'
    zh_cn["udn_account"] = 'UDN 帐号'
    zh_cn["ticketplus_account"] = '远大 帐号'

    zh_cn["password"] = '密码'
    zh_cn["facebook_password"] = 'Facebook 密码'
    zh_cn["kktix_password"] = 'KKTIX 密码'
    zh_cn["fami_password"] = 'FamiTicket 密码'
    zh_cn["cityline_password"] = 'cityline 密码'
    zh_cn["urbtix_password"] = 'URBTIX 密码'
    zh_cn["hkticketing_password"] = 'HKTICKETING 密码'
    zh_cn["kham_password"] = '宽宏 密码'
    zh_cn["ticket_password"] = '年代 密码'
    zh_cn["udn_password"] = 'UDN 密码'
    zh_cn["ticketplus_password"] = '远大 密码'
    zh_cn["save_password_alert"] = '将密码保存到文件中可能会暴露您的密码。'

    zh_cn["play_ticket_sound"] = '有票时播放音效'
    zh_cn["play_order_sound"] = '订购时播放音效'
    zh_cn["play_sound_filename"] = '音效档'
    
    zh_cn["chrome_extension"] = "Chrome 浏览器扩展程序"
    zh_cn["disable_adjacent_seat"] = "允许不连续座位"
    zh_cn["hide_some_image"] = "隐藏一些图像"
    zh_cn["block_facebook_network"] = "擋掉 Facebook 連線"

    zh_cn["maxbot_slogan"] = 'MaxBot 是一个免费的开源机器人程序。\n祝您抢票成功。'
    zh_cn["donate"] = '打赏'
    zh_cn["help"] = '使用教学'
    zh_cn["release"] = '所有可用版本'

    ja_jp={}
    ja_jp["homepage"] = 'ホームページ'
    ja_jp["browser"] = 'ブラウザ'
    ja_jp["language"] = '言語'
    ja_jp["ticket_number"] = '枚数'

    ja_jp["enable"] = '有効'
    ja_jp["recommand_enable"] = "有効化を推奨"

    ja_jp["auto_press_next_step_button"] = 'KKTIX次を自動で押す'
    ja_jp["auto_fill_ticket_number"] = '枚数自動入力'
    ja_jp["and"] = 'そして（同列）'

    ja_jp["local_dictionary"] = 'ローカル辞書'
    ja_jp["remote_url"] = 'リモートURL'
    ja_jp["server_url"] = 'サーバーURL'
    ja_jp["auto_guess_options"] = '自動推測検証問題'
    ja_jp["user_guess_string"] = '検証用の質問の回答リスト'
    ja_jp["preview"] = 'プレビュー'
    ja_jp["question"] = '質問'
    ja_jp["answer"] = '答え'

    ja_jp["date_auto_select"] = '日付自動選択'
    ja_jp["date_select_order"] = '日付のソート方法'
    ja_jp["date_keyword"] = '日付キーワード'
    ja_jp["pass_date_is_sold_out"] = '「売り切れ」公演を避ける'
    ja_jp["auto_reload_coming_soon_page"] = '公開予定のページをリロード'
    ja_jp["auto_reload_page_interval"] = 'リロード間隔(秒)'
    ja_jp["kktix_status_api"] = 'KKTIX status API'
    ja_jp["max_dwell_time"] = '最大滞留時間(秒)'
    ja_jp["reset_browser_interval"] = 'ブラウザの再起動間隔（秒）'
    ja_jp["proxy_server_port"] = 'Proxy IP:PORT'
    ja_jp["window_size"] = 'ウィンドウサイズ'

    ja_jp["area_select_order"] = 'エリアソート方法'
    ja_jp["area_keyword"] = 'エリアキーワード'
    ja_jp["area_auto_select"] = 'エリア自動選択'
    ja_jp["keyword_exclude"] = '除外キーワード'
    ja_jp["keyword_usage"] = '各キーワードはカンマで区切られた二重引用符が必要です。\nキーワード内のスペースを AND ロジックとして使用します。\nすべてに一致するように ,\"\" を追加します。'

    ja_jp["ocr_captcha"] = 'キャプチャを推測する'
    ja_jp["ocr_captcha_ddddocr_beta"] = 'ddddocr beta'
    ja_jp["ocr_captcha_force_submit"] = 'キーボードから離れて'
    ja_jp["ocr_captcha_image_source"] = 'OCR 画像ソース'
    ja_jp["ocr_captcha_not_support_arm"] = 'Intel CPU のみをサポートします'
    ja_jp["webdriver_type"] = 'WebDriverタイプ'
    ja_jp["headless"] = 'ヘッドレスモード'
    ja_jp["verbose"] = '詳細モード'
    ja_jp["running_status"] = 'スターテス'
    ja_jp["running_url"] = '現在の URL'
    ja_jp["system_clock"] = 'システムクロック'
    ja_jp["idle_keyword"] = 'アイドルキーワード'
    ja_jp["resume_keyword"] = '再起動キーワード'
    ja_jp["idle_keyword_second"] = 'アイドルキーワード（秒）'
    ja_jp["resume_keyword_second"] = '再起動キーワード（秒）'
    
    ja_jp["status_idle"] = 'アイドル状態'
    ja_jp["status_paused"] = '一時停止'
    ja_jp["status_enabled"] = '有効'
    ja_jp["status_running"] = 'ランニング'

    ja_jp["idle"] = 'アイドル'
    ja_jp["resume"] = '再起動'

    ja_jp["preference"] = '設定'
    ja_jp["advanced"] = '高度な設定'
    ja_jp["verification_word"] = "確認の言葉"
    ja_jp["maxbot_server"] = 'サーバ'
    ja_jp["autofill"] = 'オートフィル'
    ja_jp["runtime"] = 'ランタイム'
    ja_jp["about"] = '情報'

    ja_jp["run"] = 'チケットを取る'
    ja_jp["save"] = '保存'
    ja_jp["exit"] = '閉じる'
    ja_jp["copy"] = 'コピー'
    ja_jp["restore_defaults"] = 'デフォルトに戻す'
    ja_jp["config_launcher"] = 'ランチャー'
    ja_jp["done"] = '終わり'

    ja_jp["tixcraft_sid"] = '拓元家 cookie SID'
    ja_jp["ibon_ibonqware"] = 'ibon cookie ibonqware'
    ja_jp["facebook_account"] = 'Facebookのアカウント'
    ja_jp["kktix_account"] = 'KKTIXのアカウント'
    ja_jp["fami_account"] = 'FamiTicketのアカウント'
    ja_jp["cityline_account"] = 'citylineのアカウント'
    ja_jp["urbtix_account"] = 'URBTIXのアカウント'
    ja_jp["hkticketing_account"] = 'HKTICKETINGのアカウント'
    ja_jp["kham_account"] = 'KHAMのアカウント'
    ja_jp["ticket_account"] = 'TICKETのアカウント'
    ja_jp["udn_account"] = 'UDNのアカウント'
    ja_jp["ticketplus_account"] = '遠大のアカウント'

    ja_jp["password"] = 'パスワード'
    ja_jp["facebook_password"] = 'Facebookのパスワード'
    ja_jp["kktix_password"] = 'KKTIXのパスワード'
    ja_jp["fami_password"] = 'FamiTicketのパスワード'
    ja_jp["cityline_password"] = 'citylineのパスワード'
    ja_jp["urbtix_password"] = 'URBTIXのパスワード'
    ja_jp["hkticketing_password"] = 'HKTICKETINGのパスワード'
    ja_jp["kham_password"] = 'KHAMのパスワード'
    ja_jp["ticket_password"] = 'TICKETのパスワード'
    ja_jp["udn_password"] = 'UDNのパスワード'
    ja_jp["ticketplus_password"] = '遠大のパスワード'
    ja_jp["save_password_alert"] = 'パスワードをファイルに保存すると、パスワードが公開される可能性があります。'

    ja_jp["play_ticket_sound"] = '有票時に音を鳴らす'
    ja_jp["play_order_sound"] = '注文時に音を鳴らす'
    ja_jp["play_sound_filename"] = 'サウンドファイル'
    
    ja_jp["chrome_extension"] = "Chrome ブラウザ拡張機能"
    ja_jp["disable_adjacent_seat"] = "連続しない座席も可"
    ja_jp["hide_some_image"] = "一部の画像を非表示にする"
    ja_jp["block_facebook_network"] = "Facebookをブロックする"

    ja_jp["maxbot_slogan"] = 'MaxBot は無料のオープン ソース ボット プログラムです。チケットの成功をお祈りします。'
    ja_jp["donate"] = '寄付'
    ja_jp["help"] = '利用方法'
    ja_jp["release"] = 'リリース'

    translate['en_us']=en_us
    translate['zh_tw']=zh_tw
    translate['zh_cn']=zh_cn
    translate['ja_jp']=ja_jp
    return translate

def get_default_config():
    config_dict={}

    config_dict["homepage"] = CONST_HOMEPAGE_DEFAULT
    config_dict["browser"] = "chrome"
    config_dict["language"] = "English"
    config_dict["ticket_number"] = 2
    config_dict["ocr_captcha"] = {}
    config_dict["ocr_captcha"]["enable"] = True
    config_dict["ocr_captcha"]["beta"] = True
    config_dict["ocr_captcha"]["force_submit"] = True
    config_dict["ocr_captcha"]["image_source"] = CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS
    config_dict["webdriver_type"] = CONST_WEBDRIVER_TYPE_UC

    if util.is_arm():
        config_dict["ocr_captcha"]["enable"] = False
        config_dict["ocr_captcha"]["force_submit"] = False

    config_dict["date_auto_select"] = {}
    config_dict["date_auto_select"]["enable"] = True
    config_dict["date_auto_select"]["date_keyword"] = ""
    config_dict["date_auto_select"]["mode"] = CONST_SELECT_ORDER_DEFAULT

    config_dict["area_auto_select"] = {}
    config_dict["area_auto_select"]["enable"] = True
    config_dict["area_auto_select"]["mode"] = CONST_SELECT_ORDER_DEFAULT
    config_dict["area_auto_select"]["area_keyword"] = ""
    config_dict["keyword_exclude"] = CONST_EXCLUDE_DEFAULT

    config_dict['kktix']={}
    config_dict["kktix"]["auto_press_next_step_button"] = True
    config_dict["kktix"]["auto_fill_ticket_number"] = True

    config_dict['tixcraft']={}
    config_dict["tixcraft"]["pass_date_is_sold_out"] = True
    config_dict["tixcraft"]["auto_reload_coming_soon_page"] = True

    config_dict['advanced']={}

    config_dict['advanced']['play_sound']={}
    config_dict["advanced"]["play_sound"]["ticket"] = True
    config_dict["advanced"]["play_sound"]["order"] = True
    config_dict["advanced"]["play_sound"]["filename"] = CONST_CAPTCHA_SOUND_FILENAME_DEFAULT

    config_dict["advanced"]["tixcraft_sid"] = ""
    config_dict["advanced"]["ibonqware"] = ""
    config_dict["advanced"]["facebook_account"] = ""
    config_dict["advanced"]["kktix_account"] = ""
    config_dict["advanced"]["fami_account"] = ""
    config_dict["advanced"]["cityline_account"] = ""
    config_dict["advanced"]["urbtix_account"] = ""
    config_dict["advanced"]["hkticketing_account"] = ""
    config_dict["advanced"]["kham_account"] = ""
    config_dict["advanced"]["ticket_account"] = ""
    config_dict["advanced"]["udn_account"] = ""
    config_dict["advanced"]["ticketplus_account"] = ""

    config_dict["advanced"]["facebook_password"] = ""
    config_dict["advanced"]["kktix_password"] = ""
    config_dict["advanced"]["fami_password"] = ""
    config_dict["advanced"]["urbtix_password"] = ""
    config_dict["advanced"]["cityline_password"] = ""
    config_dict["advanced"]["hkticketing_password"] = ""
    config_dict["advanced"]["kham_password"] = ""
    config_dict["advanced"]["ticket_password"] = ""
    config_dict["advanced"]["udn_password"] = ""
    config_dict["advanced"]["ticketplus_password"] = ""

    config_dict["advanced"]["facebook_password_plaintext"] = ""
    config_dict["advanced"]["kktix_password_plaintext"] = ""
    config_dict["advanced"]["fami_password_plaintext"] = ""
    config_dict["advanced"]["urbtix_password_plaintext"] = ""
    config_dict["advanced"]["cityline_password_plaintext"] = ""
    config_dict["advanced"]["hkticketing_password_plaintext"] = ""
    config_dict["advanced"]["kham_password_plaintext"] = ""
    config_dict["advanced"]["ticket_password_plaintext"] = ""
    config_dict["advanced"]["udn_password_plaintext"] = ""
    config_dict["advanced"]["ticketplus_password_plaintext"] = ""

    config_dict["advanced"]["chrome_extension"] = True
    config_dict["advanced"]["disable_adjacent_seat"] = False
    config_dict["advanced"]["hide_some_image"] = False
    config_dict["advanced"]["block_facebook_network"] = False

    config_dict["advanced"]["headless"] = False
    config_dict["advanced"]["verbose"] = False
    config_dict["advanced"]["auto_guess_options"] = True
    config_dict["advanced"]["user_guess_string"] = ""
    config_dict["advanced"]["remote_url"] = "http://127.0.0.1:%d/" % (CONST_SERVER_PORT)

    config_dict["advanced"]["auto_reload_page_interval"] = 0
    config_dict["advanced"]["reset_browser_interval"] = 0
    config_dict["advanced"]["kktix_status_api"] = False
    config_dict["advanced"]["max_dwell_time"] = 60
    config_dict["advanced"]["proxy_server_port"] = ""
    config_dict["advanced"]["window_size"] = "480,1024"

    config_dict["advanced"]["idle_keyword"] = ""
    config_dict["advanced"]["resume_keyword"] = ""
    config_dict["advanced"]["idle_keyword_second"] = ""
    config_dict["advanced"]["resume_keyword_second"] = ""

    return config_dict

def read_last_url_from_file():
    ret = ""
    if os.path.exists(CONST_MAXBOT_LAST_URL_FILE):
        with open(CONST_MAXBOT_LAST_URL_FILE, "r") as text_file:
            ret = text_file.readline()
    return ret

def load_json():
    app_root = util.get_app_root()

    # overwrite config path.
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
    else:
        config_dict = get_default_config()
    return config_filepath, config_dict

def btn_restore_defaults_clicked(language_code):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)
    if os.path.exists(str(config_filepath)):
        try:
            os.unlink(str(config_filepath))
        except Exception as exc:
            print(exc)
            pass

    config_dict = get_default_config()
    messagebox.showinfo(translate[language_code]["restore_defaults"], translate[language_code]["done"])

    global root
    load_GUI(root, config_dict)

def do_maxbot_idle():
    app_root = util.get_app_root()
    idle_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
    with open(CONST_MAXBOT_INT28_FILE, "w") as text_file:
        text_file.write("")

def btn_idle_clicked(language_code):
    do_maxbot_idle()
    update_maxbot_runtime_status()

def do_maxbot_resume():
    app_root = util.get_app_root()
    idle_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
    for i in range(3):
         util.force_remove_file(idle_filepath)

def btn_resume_clicked(language_code):
    do_maxbot_resume()
    update_maxbot_runtime_status()

def btn_launcher_clicked(language_code):
    Root_Dir = ""
    save_ret = btn_save_act(slience_mode=True)
    if save_ret:
        script_name = "config_launcher"
        threading.Thread(target=util.launch_maxbot, args=(script_name,)).start()

def btn_save_clicked():
    btn_save_act()

def btn_save_act(slience_mode=False):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    config_dict = get_default_config()
    language_code = get_language_code_by_name(config_dict["language"])

    # read user input
    global combo_homepage
    global combo_browser
    global combo_language
    global combo_ticket_number

    global chk_state_auto_press_next_step_button
    global chk_state_auto_fill_ticket_number
    global txt_user_guess_string

    global chk_state_date_auto_select
    global txt_date_keyword
    global chk_state_area_auto_select
    global txt_area_keyword
    global txt_keyword_exclude
    global txt_remote_url

    global combo_date_auto_select_mode
    global combo_area_auto_select_mode

    global chk_state_pass_date_is_sold_out
    global chk_state_auto_reload_coming_soon_page
    global txt_auto_reload_page_interval
    global chk_status_kktix_status_api
    global txt_max_dwell_time
    global txt_reset_browser_intervalv
    global txt_proxy_server_port
    global txt_window_size

    global txt_tixcraft_sid
    global txt_ibon_ibonqware
    global txt_facebook_account
    global txt_kktix_account
    global txt_fami_account
    global txt_cityline_account
    global txt_urbtix_account
    global txt_hkticketing_account
    global txt_kham_account
    global txt_ticket_account
    global txt_udn_account
    global txt_ticketplus_account

    global txt_facebook_password
    global txt_kktix_password
    global txt_fami_password
    global txt_cityline_password
    global txt_urbtix_password
    global txt_hkticketing_password
    global txt_kham_password
    global txt_ticket_password
    global txt_udn_password
    global txt_ticketplus_password

    global chk_state_play_ticket_sound
    global chk_state_play_order_sound
    global txt_play_sound_filename
    global chk_state_ocr_captcha
    global chk_state_ocr_captcha_ddddocr_beta
    global chk_state_ocr_captcha_force_submit
    global chk_state_chrome_extension
    global chk_state_adjacent_seat
    global chk_state_hide_some_image
    global chk_state_block_facebook_network

    global chk_state_headless
    global chk_state_verbose
    global chk_state_auto_guess_options
    global combo_ocr_captcha_image_source
    global combo_webdriver_type

    global txt_idle_keyword
    global txt_resume_keyword
    global txt_idle_keyword_second
    global txt_resume_keyword_second

    is_all_data_correct = True

    if is_all_data_correct:
        if combo_homepage.get().strip()=="":
            is_all_data_correct = False
            messagebox.showerror("Error", "Please enter homepage")
        else:
            homepage_domain = combo_homepage.get().strip()
            if ' (' in homepage_domain:
                homepage_domain = homepage_domain.split(' (')[0]
            config_dict["homepage"] = homepage_domain

    if is_all_data_correct:
        if combo_browser.get().strip()=="":
            is_all_data_correct = False
            messagebox.showerror("Error", "Please select a browser: chrome or firefox")
        else:
            config_dict["browser"] = combo_browser.get().strip()

    if is_all_data_correct:
        if combo_language.get().strip()=="":
            is_all_data_correct = False
            messagebox.showerror("Error", "Please select a language")
        else:
            config_dict["language"] = combo_language.get().strip()
            # display as new language.
            language_code = get_language_code_by_name(config_dict["language"])

    if is_all_data_correct:
        if combo_ticket_number.get().strip()=="":
            is_all_data_correct = False
            messagebox.showerror("Error", "Please select a value")
        else:
            config_dict["ticket_number"] = int(combo_ticket_number.get().strip())

    if is_all_data_correct:
        config_dict["kktix"]["auto_press_next_step_button"] = bool(chk_state_auto_press_next_step_button.get())
        config_dict["kktix"]["auto_fill_ticket_number"] = bool(chk_state_auto_fill_ticket_number.get())

        config_dict["date_auto_select"]["enable"] = bool(chk_state_date_auto_select.get())
        config_dict["date_auto_select"]["mode"] = combo_date_auto_select_mode.get().strip()

        date_keyword = txt_date_keyword.get("1.0",END).strip()
        date_keyword = util.format_config_keyword_for_json(date_keyword)
        config_dict["date_auto_select"]["date_keyword"] = date_keyword

        config_dict["tixcraft"]["pass_date_is_sold_out"] = bool(chk_state_pass_date_is_sold_out.get())
        config_dict["tixcraft"]["auto_reload_coming_soon_page"] = bool(chk_state_auto_reload_coming_soon_page.get())

        area_keyword = txt_area_keyword.get("1.0",END).strip()
        area_keyword = util.format_config_keyword_for_json(area_keyword)

        keyword_exclude = txt_keyword_exclude.get("1.0",END).strip()
        keyword_exclude = util.format_config_keyword_for_json(keyword_exclude)

        user_guess_string = txt_user_guess_string.get("1.0",END).strip()
        user_guess_string = util.format_config_keyword_for_json(user_guess_string)

        remote_url = txt_remote_url.get("1.0",END).strip()
        remote_url = util.format_config_keyword_for_json(remote_url)

        idle_keyword = txt_idle_keyword.get("1.0",END).strip()
        idle_keyword = util.format_config_keyword_for_json(idle_keyword)

        resume_keyword = txt_resume_keyword.get("1.0",END).strip()
        resume_keyword = util.format_config_keyword_for_json(resume_keyword)

        idle_keyword_second = txt_idle_keyword_second.get("1.0",END).strip()
        idle_keyword_second = util.format_config_keyword_for_json(idle_keyword_second)

        resume_keyword_second = txt_resume_keyword_second.get("1.0",END).strip()
        resume_keyword_second = util.format_config_keyword_for_json(resume_keyword_second)

        # test keyword format.
        if is_all_data_correct:
            if len(area_keyword) > 0:
                try:
                    test_array = json.loads("["+ area_keyword +"]")
                except Exception as exc:
                    print(exc)
                    messagebox.showinfo(translate[language_code]["save"], "Error:" + translate[language_code]["area_keyword"])
                    is_all_data_correct = False

        if is_all_data_correct:
            if len(keyword_exclude) > 0:
                try:
                    test_array = json.loads("["+ keyword_exclude +"]")
                except Exception as exc:
                    print(exc)
                    messagebox.showinfo(translate[language_code]["save"], "Error:" + translate[language_code]["keyword_exclude"])
                    is_all_data_correct = False

        if is_all_data_correct:
            if len(user_guess_string) > 0:
                try:
                    test_array = json.loads("["+ user_guess_string +"]")
                except Exception as exc:
                    print(exc)
                    messagebox.showinfo(translate[language_code]["save"], "Error:" + translate[language_code]["user_guess_string"])
                    is_all_data_correct = False

        if is_all_data_correct:
            if len(remote_url) > 0:
                try:
                    test_array = json.loads("["+ remote_url +"]")
                except Exception as exc:
                    print(exc)
                    messagebox.showinfo(translate[language_code]["save"], "Error:" + translate[language_code]["remote_url"])
                    is_all_data_correct = False

        if is_all_data_correct:
            if len(idle_keyword) > 0:
                try:
                    test_array = json.loads("["+ idle_keyword +"]")
                except Exception as exc:
                    print(exc)
                    messagebox.showinfo(translate[language_code]["save"], "Error:" + translate[language_code]["idle_keyword"])
                    is_all_data_correct = False

        if is_all_data_correct:
            if len(resume_keyword) > 0:
                try:
                    test_array = json.loads("["+ resume_keyword +"]")
                except Exception as exc:
                    print(exc)
                    messagebox.showinfo(translate[language_code]["save"], "Error:" + translate[language_code]["resume_keyword"])
                    is_all_data_correct = False

        if is_all_data_correct:
            if len(idle_keyword_second) > 0:
                try:
                    test_array = json.loads("["+ idle_keyword_second +"]")
                except Exception as exc:
                    print(exc)
                    messagebox.showinfo(translate[language_code]["save"], "Error:" + translate[language_code]["idle_keyword_second"])
                    is_all_data_correct = False

        if is_all_data_correct:
            if len(resume_keyword_second) > 0:
                try:
                    test_array = json.loads("["+ resume_keyword_second +"]")
                except Exception as exc:
                    print(exc)
                    messagebox.showinfo(translate[language_code]["save"], "Error:" + translate[language_code]["resume_keyword_second"])
                    is_all_data_correct = False

        if is_all_data_correct:
            config_dict["area_auto_select"]["area_keyword"] = area_keyword
            config_dict["keyword_exclude"] = keyword_exclude
            config_dict["advanced"]["user_guess_string"] = user_guess_string
            config_dict["advanced"]["remote_url"] = remote_url
            
            config_dict["advanced"]["idle_keyword"] = idle_keyword
            config_dict["advanced"]["resume_keyword"] = resume_keyword
            config_dict["advanced"]["idle_keyword_second"] = idle_keyword_second
            config_dict["advanced"]["resume_keyword_second"] = resume_keyword_second

            txt_idle_keyword.delete(1.0, "end")
            txt_resume_keyword.delete(1.0, "end")
            txt_idle_keyword_second.delete(1.0, "end")
            txt_resume_keyword_second.delete(1.0, "end")

            txt_idle_keyword.insert("1.0", config_dict["advanced"]["idle_keyword"].strip())
            txt_resume_keyword.insert("1.0", config_dict["advanced"]["resume_keyword"].strip())
            txt_idle_keyword_second.insert("1.0", config_dict["advanced"]["idle_keyword_second"].strip())
            txt_resume_keyword_second.insert("1.0", config_dict["advanced"]["resume_keyword_second"].strip())

    if is_all_data_correct:
        config_dict["area_auto_select"]["enable"] = bool(chk_state_area_auto_select.get())
        config_dict["area_auto_select"]["mode"] = combo_area_auto_select_mode.get().strip()

        config_dict["advanced"]["play_sound"]["ticket"] = bool(chk_state_play_ticket_sound.get())
        config_dict["advanced"]["play_sound"]["order"] = bool(chk_state_play_order_sound.get())
        config_dict["advanced"]["play_sound"]["filename"] = txt_play_sound_filename.get().strip()

        config_dict["advanced"]["tixcraft_sid"] = txt_tixcraft_sid.get().strip()
        config_dict["advanced"]["ibonqware"] = txt_ibon_ibonqware.get().strip()
        
        config_dict["advanced"]["facebook_account"] = txt_facebook_account.get().strip()
        config_dict["advanced"]["kktix_account"] = txt_kktix_account.get().strip()
        config_dict["advanced"]["fami_account"] = txt_fami_account.get().strip()
        config_dict["advanced"]["cityline_account"] = txt_cityline_account.get().strip()
        config_dict["advanced"]["urbtix_account"] = txt_urbtix_account.get().strip()
        config_dict["advanced"]["hkticketing_account"] = txt_hkticketing_account.get().strip()
        config_dict["advanced"]["kham_account"] = txt_kham_account.get().strip()
        config_dict["advanced"]["ticket_account"] = txt_ticket_account.get().strip()
        config_dict["advanced"]["udn_account"] = txt_udn_account.get().strip()
        config_dict["advanced"]["ticketplus_account"] = txt_ticketplus_account.get().strip()

        config_dict["advanced"]["facebook_password"] = txt_facebook_password.get().strip()
        config_dict["advanced"]["kktix_password"] = txt_kktix_password.get().strip()
        config_dict["advanced"]["fami_password"] = txt_fami_password.get().strip()
        config_dict["advanced"]["cityline_password"] = txt_cityline_password.get().strip()
        config_dict["advanced"]["urbtix_password"] = txt_urbtix_password.get().strip()
        config_dict["advanced"]["hkticketing_password"] = txt_hkticketing_password.get().strip()
        config_dict["advanced"]["kham_password"] = txt_kham_password.get().strip()
        config_dict["advanced"]["ticket_password"] = txt_ticket_password.get().strip()
        config_dict["advanced"]["udn_password"] = txt_udn_password.get().strip()
        config_dict["advanced"]["ticketplus_password"] = txt_ticketplus_password.get().strip()

        config_dict["advanced"]["tixcraft_sid"] = config_dict["advanced"]["tixcraft_sid"]
        config_dict["advanced"]["ibonqware"] = config_dict["advanced"]["ibonqware"]

        config_dict["advanced"]["facebook_password"] = util.encryptMe(config_dict["advanced"]["facebook_password"])
        config_dict["advanced"]["kktix_password"] = util.encryptMe(config_dict["advanced"]["kktix_password"])
        config_dict["advanced"]["fami_password"] = util.encryptMe(config_dict["advanced"]["fami_password"])
        config_dict["advanced"]["cityline_password"] = util.encryptMe(config_dict["advanced"]["cityline_password"])
        config_dict["advanced"]["urbtix_password"] = util.encryptMe(config_dict["advanced"]["urbtix_password"])
        config_dict["advanced"]["hkticketing_password"] = util.encryptMe(config_dict["advanced"]["hkticketing_password"])
        config_dict["advanced"]["kham_password"] = util.encryptMe(config_dict["advanced"]["kham_password"])
        config_dict["advanced"]["ticket_password"] = util.encryptMe(config_dict["advanced"]["ticket_password"])
        config_dict["advanced"]["udn_password"] = util.encryptMe(config_dict["advanced"]["udn_password"])
        config_dict["advanced"]["ticketplus_password"] = util.encryptMe(config_dict["advanced"]["ticketplus_password"])

        config_dict["advanced"]["chrome_extension"] = bool(chk_state_chrome_extension.get())
        config_dict["advanced"]["disable_adjacent_seat"] = bool(chk_state_adjacent_seat.get())
        config_dict["advanced"]["hide_some_image"] = bool(chk_state_hide_some_image.get())
        config_dict["advanced"]["block_facebook_network"] = bool(chk_state_block_facebook_network.get())

        config_dict["ocr_captcha"] = {}
        config_dict["ocr_captcha"]["enable"] = bool(chk_state_ocr_captcha.get())
        config_dict["ocr_captcha"]["beta"] = bool(chk_state_ocr_captcha_ddddocr_beta.get())
        config_dict["ocr_captcha"]["force_submit"] = bool(chk_state_ocr_captcha_force_submit.get())
        config_dict["ocr_captcha"]["image_source"] = combo_ocr_captcha_image_source.get().strip()

        if util.is_arm():
            config_dict["ocr_captcha"]["enable"] = False
            config_dict["ocr_captcha"]["force_submit"] = False

        config_dict["webdriver_type"] = combo_webdriver_type.get().strip()
        config_dict["advanced"]["headless"] = bool(chk_state_headless.get())
        #config_dict["advanced"]["verbose"] = bool(chk_state_verbose.get())

        config_dict["advanced"]["auto_guess_options"] = bool(chk_state_auto_guess_options.get())

        config_dict["advanced"]["auto_reload_page_interval"] = float(txt_auto_reload_page_interval.get().strip())
        config_dict["advanced"]["kktix_status_api"] = bool(chk_state_kktix_status_api.get())
        config_dict["advanced"]["max_dwell_time"] = int(txt_max_dwell_time.get().strip())
        config_dict["advanced"]["reset_browser_interval"] = int(txt_reset_browser_interval.get().strip())
        config_dict["advanced"]["proxy_server_port"] = txt_proxy_server_port.get().strip()
        config_dict["advanced"]["window_size"] = txt_window_size.get().strip()

        if config_dict["advanced"]["max_dwell_time"] > 0:
            if config_dict["advanced"]["max_dwell_time"] < 15:
                config_dict["advanced"]["max_dwell_time"] = 15

        if config_dict["advanced"]["reset_browser_interval"] > 0:
            if config_dict["advanced"]["reset_browser_interval"] < 20:
                # min value is 20 seconds.
                config_dict["advanced"]["reset_browser_interval"] = 20


    # save config.
    if is_all_data_correct:
        if not slience_mode:
            #messagebox.showinfo(translate[language_code]["save"], translate[language_code]["done"])
            file_to_save = asksaveasfilename(initialdir=app_root , initialfile=CONST_MAXBOT_CONFIG_FILE, defaultextension=".json", filetypes=[("json Documents","*.json"),("All Files","*.*")])
            if not file_to_save is None:
                if len(file_to_save) > 0:
                    print("save as to:", file_to_save)
                    util.save_json(config_dict, file_to_save)
        else:
            # slience
            util.save_json(config_dict, config_filepath)

    return is_all_data_correct


def btn_run_clicked(language_code):
    print('run button pressed.')
    Root_Dir = ""
    save_ret = btn_save_act(slience_mode=True)
    print("save config result:", save_ret)
    if save_ret:
        launch_maxbot()

def launch_maxbot():
    global launch_counter
    if "launch_counter" in globals():
        launch_counter += 1
    else:
        launch_counter = 0
    
    webdriver_type = ""
    global combo_webdriver_type
    if 'combo_webdriver_type' in globals():
        webdriver_type = combo_webdriver_type.get().strip()

    script_name = "chrome_tixcraft"
    if webdriver_type == CONST_WEBDRIVER_TYPE_NODRIVER:
        script_name = "nodriver_tixcraft"

    global txt_window_size
    window_size = txt_window_size.get().strip()
    if len(window_size) > 0:
        if "," in window_size:
            size_array = window_size.split(",")
            target_width = int(size_array[0])
            target_left = target_width * launch_counter
            #print("target_left:", target_left)
            if target_left >= 1440:
                launch_counter = 0
            window_size = window_size + "," + str(launch_counter)
            #print("window_size:", window_size)

    threading.Thread(target=util.launch_maxbot, args=(script_name,"","","","",window_size,)).start()

def show_preview_text():
    if os.path.exists(CONST_MAXBOT_ANSWER_ONLINE_FILE):
        answer_text = ""
        with open(CONST_MAXBOT_ANSWER_ONLINE_FILE, "r") as text_file:
            answer_text = text_file.readline()

        answer_text = util.format_config_keyword_for_json(answer_text)

        date_array = []
        try:
            date_array = json.loads("["+ answer_text +"]")
        except Exception as exc:
            date_array = []

        global lbl_online_dictionary_preview_data
        if 'lbl_online_dictionary_preview_data' in globals():
            try:
                lbl_online_dictionary_preview_data.config(text=','.join(date_array))
            except Exception as exc:
                pass

def btn_preview_text_clicked():
    global txt_remote_url
    remote_url = ""
    if 'txt_remote_url' in globals():
        try:
            remote_url = txt_remote_url.get("1.0",END).strip()
        except Exception as exc:
            pass
    remote_url = util.format_config_keyword_for_json(remote_url)

    if len(remote_url) > 0:
        url_array = []
        try:
            url_array = json.loads("["+ remote_url +"]")
        except Exception as exc:
            url_array = []

        force_write = False
        if len(url_array)==1:
            force_write = True
        for each_url in url_array:
            #print("new_remote_url:", new_remote_url)
            is_write_to_file = util.save_url_to_file(each_url, CONST_MAXBOT_ANSWER_ONLINE_FILE, force_write=force_write)
            if is_write_to_file:
                break
    show_preview_text()


def btn_open_text_server_clicked():
    global tab4
    global tabControl
    tabControl.select(tab4)

def btn_preview_sound_clicked():
    global txt_play_sound_filename
    new_sound_filename = txt_play_sound_filename.get().strip()
    #print("new_sound_filename:", new_sound_filename)
    app_root = util.get_app_root()
    new_sound_filename = os.path.join(app_root, new_sound_filename)
    util.play_mp3_async(new_sound_filename)

def open_url(url):
    webbrowser.open_new(url)

def btn_exit_clicked():
    root.destroy()

def btn_donate_clicked():
    webbrowser.open(URL_DONATE)

def btn_help_clicked():
    webbrowser.open(URL_HELP)

def callbackLanguageOnChange(event):
    applyNewLanguage()

def get_language_code_by_name(new_language):
    language_code = "en_us"
    if u'繁體中文' in new_language:
        language_code = 'zh_tw'
    if u'簡体中文' in new_language:
        language_code = 'zh_cn'
    if u'日本語' in new_language:
        language_code = 'ja_jp'
    #print("new language code:", language_code)

    return language_code

def applyNewLanguage():
    global combo_language
    new_language = combo_language.get().strip()
    #print("new language value:", new_language)

    language_code=get_language_code_by_name(new_language)

    global lbl_homepage
    global lbl_browser
    global lbl_language
    global lbl_ticket_number

    # for kktix
    global lbl_auto_press_next_step_button
    global lbl_auto_fill_ticket_number
    global lbl_user_guess_string_description
    global lbl_user_guess_string

    # for tixcraft
    global lbl_date_auto_select
    global lbl_date_auto_select_mode
    global lbl_date_keyword
    global lbl_area_auto_select
    global lbl_area_auto_select_mode
    global lbl_area_keyword
    global lbl_keyword_exclude
    global lbl_keyword_usage

    global lbl_pass_date_is_sold_out
    global lbl_auto_reload_coming_soon_page
    global lbl_ocr_captcha
    global lbl_ocr_captcha_ddddocr_beta
    global lbl_ocr_captcha_force_submit
    global lbl_ocr_captcha_image_source
    global lbl_ocr_captcha_not_support_arm
    global lbl_webdriver_type
    global lbl_headless
    global lbl_verbose
    global lbl_auto_guess_options

    global lbl_maxbot_status
    global lbl_maxbot_last_url
    global lbl_system_clock
    global lbl_idle_keyword
    global lbl_resume_keyword
    global lbl_idle_keyword_second
    global lbl_resume_keyword_second

    # for checkbox
    global chk_auto_press_next_step_button
    global chk_auto_fill_ticket_number
    global chk_date_auto_select
    global chk_area_auto_select
    global chk_pass_date_is_sold_out
    global chk_auto_reload_coming_soon_page
    global chk_play_ticket_sound
    global chk_play_order_sound
    global chk_ocr_captcha
    global chk_ocr_captcha_ddddocr_beta
    global chk_ocr_captcha_force_submit
    global chk_chrome_extension
    global chk_adjacent_seat
    global chk_hide_some_image
    global chk_block_facebook_network

    global chk_headless
    global chk_verbose
    global lbl_remote_url
    global lbl_server_url
    global lbl_online_dictionary_preview
    global lbl_question
    global lbl_answer
    global chk_auto_guess_options

    global tabControl

    global lbl_slogan
    global lbl_help
    global lbl_donate
    global lbl_release

    global lbl_chrome_extension
    global lbl_adjacent_seat
    global lbl_hide_some_image
    global lbl_block_facebook_network

    global lbl_hide_some_image_recommand
    global lbl_block_facebook_network_recommand

    global lbl_auto_reload_page_interval
    global lbl_kktix_status_api
    global lbl_max_dwell_time
    global lbl_reset_browser_interval
    global lbl_proxy_server_port
    global lbl_window_size

    lbl_homepage.config(text=translate[language_code]["homepage"])
    lbl_browser.config(text=translate[language_code]["browser"])
    lbl_language.config(text=translate[language_code]["language"])
    lbl_ticket_number.config(text=translate[language_code]["ticket_number"])

    lbl_auto_press_next_step_button.config(text=translate[language_code]["auto_press_next_step_button"])
    lbl_auto_fill_ticket_number.config(text=translate[language_code]["auto_fill_ticket_number"])
    lbl_user_guess_string_description.config(text=translate[language_code]["user_guess_string"])
    lbl_user_guess_string.config(text=translate[language_code]["local_dictionary"])

    lbl_date_auto_select.config(text=translate[language_code]["date_auto_select"])
    lbl_date_auto_select_mode.config(text=translate[language_code]["date_select_order"])
    lbl_date_keyword.config(text=translate[language_code]["date_keyword"])
    lbl_area_auto_select.config(text=translate[language_code]["area_auto_select"])
    lbl_area_auto_select_mode.config(text=translate[language_code]["area_select_order"])
    lbl_area_keyword.config(text=translate[language_code]["area_keyword"])
    lbl_keyword_exclude.config(text=translate[language_code]["keyword_exclude"])
    lbl_keyword_usage.config(text=translate[language_code]["keyword_usage"])
    lbl_pass_date_is_sold_out.config(text=translate[language_code]["pass_date_is_sold_out"])
    lbl_auto_reload_coming_soon_page.config(text=translate[language_code]["auto_reload_coming_soon_page"])
    lbl_ocr_captcha.config(text=translate[language_code]["ocr_captcha"])
    lbl_ocr_captcha_ddddocr_beta.config(text=translate[language_code]["ocr_captcha_ddddocr_beta"])
    lbl_ocr_captcha_force_submit.config(text=translate[language_code]["ocr_captcha_force_submit"])
    lbl_ocr_captcha_image_source.config(text=translate[language_code]["ocr_captcha_image_source"])
    lbl_ocr_captcha_not_support_arm.config(text=translate[language_code]["ocr_captcha_not_support_arm"])
    lbl_webdriver_type.config(text=translate[language_code]["webdriver_type"])
    lbl_chrome_extension.config(text=translate[language_code]["chrome_extension"])
    lbl_adjacent_seat.config(text=translate[language_code]["disable_adjacent_seat"])
    lbl_hide_some_image.config(text=translate[language_code]["hide_some_image"])
    lbl_block_facebook_network.config(text=translate[language_code]["block_facebook_network"])

    lbl_hide_some_image_recommand.config(text=translate[language_code]["recommand_enable"])
    lbl_block_facebook_network_recommand.config(text=translate[language_code]["recommand_enable"])

    lbl_auto_reload_page_interval.config(text=translate[language_code]["auto_reload_page_interval"])
    lbl_kktix_status_api.config(text=translate[language_code]["kktix_status_api"])
    lbl_max_dwell_time.config(text=translate[language_code]["max_dwell_time"])
    lbl_reset_browser_interval.config(text=translate[language_code]["reset_browser_interval"])
    lbl_proxy_server_port.config(text=translate[language_code]["proxy_server_port"])
    lbl_window_size.config(text=translate[language_code]["window_size"])

    lbl_headless.config(text=translate[language_code]["headless"])
    lbl_verbose.config(text=translate[language_code]["verbose"])

    lbl_remote_url.config(text=translate[language_code]["remote_url"])
    lbl_server_url.config(text=translate[language_code]["server_url"])
    lbl_online_dictionary_preview.config(text=translate[language_code]["preview"])
    lbl_auto_guess_options.config(text=translate[language_code]["auto_guess_options"])
    lbl_question.config(text=translate[language_code]["question"])
    lbl_answer.config(text=translate[language_code]["answer"])

    lbl_maxbot_status.config(text=translate[language_code]["running_status"])
    lbl_maxbot_last_url.config(text=translate[language_code]["running_url"])
    lbl_system_clock.config(text=translate[language_code]["system_clock"])
    lbl_idle_keyword.config(text=translate[language_code]["idle_keyword"])
    lbl_resume_keyword.config(text=translate[language_code]["resume_keyword"])
    lbl_idle_keyword_second.config(text=translate[language_code]["idle_keyword_second"])
    lbl_resume_keyword_second.config(text=translate[language_code]["resume_keyword_second"])

    chk_auto_press_next_step_button.config(text=translate[language_code]["enable"])
    chk_auto_fill_ticket_number.config(text=translate[language_code]["enable"])
    chk_date_auto_select.config(text=translate[language_code]["enable"])
    chk_area_auto_select.config(text=translate[language_code]["enable"])
    chk_pass_date_is_sold_out.config(text=translate[language_code]["enable"])
    chk_auto_reload_coming_soon_page.config(text=translate[language_code]["enable"])
    chk_play_ticket_sound.config(text=translate[language_code]["enable"])
    chk_play_order_sound.config(text=translate[language_code]["enable"])
    chk_ocr_captcha.config(text=translate[language_code]["enable"])
    chk_ocr_captcha_ddddocr_beta.config(text=translate[language_code]["enable"])
    chk_ocr_captcha_force_submit.config(text=translate[language_code]["enable"])
    chk_chrome_extension.config(text=translate[language_code]["enable"])
    chk_adjacent_seat.config(text=translate[language_code]["enable"])
    chk_hide_some_image.config(text=translate[language_code]["enable"])
    chk_block_facebook_network.config(text=translate[language_code]["enable"])

    chk_headless.config(text=translate[language_code]["enable"])
    chk_verbose.config(text=translate[language_code]["enable"])
    chk_auto_guess_options.config(text=translate[language_code]["enable"])

    tabControl.tab(0, text=translate[language_code]["preference"])
    tabControl.tab(1, text=translate[language_code]["advanced"])
    tabControl.tab(2, text=translate[language_code]["verification_word"])
    tabControl.tab(3, text=translate[language_code]["maxbot_server"])
    tabControl.tab(4, text=translate[language_code]["autofill"])
    tabControl.tab(5, text=translate[language_code]["runtime"])
    tabControl.tab(6, text=translate[language_code]["about"])

    global lbl_tixcraft_sid
    global lbl_ibon_ibonqware
    global lbl_facebook_account
    global lbl_kktix_account
    global lbl_fami_account
    global lbl_cityline_account
    global lbl_urbtix_account
    global lbl_hkticketing_account
    global lbl_kham_account
    global lbl_ticket_account
    global lbl_udn_account
    global lbl_ticketplus_account

    global lbl_password
    global lbl_facebook_password
    global lbl_kktix_password
    global lbl_fami_password
    global lbl_cityline_password
    global lbl_urbtix_password
    global lbl_hkticketing_password
    global lbl_kham_password
    global lbl_ticket_password
    global lbl_udn_password
    global lbl_ticketplus_password

    global lbl_save_password_alert

    global lbl_play_ticket_sound
    global lbl_play_order_sound
    global lbl_play_sound_filename

    lbl_tixcraft_sid.config(text=translate[language_code]["tixcraft_sid"])
    lbl_ibon_ibonqware.config(text=translate[language_code]["ibon_ibonqware"])
    lbl_facebook_account.config(text=translate[language_code]["facebook_account"])
    lbl_kktix_account.config(text=translate[language_code]["kktix_account"])
    lbl_fami_account.config(text=translate[language_code]["fami_account"])
    lbl_cityline_account.config(text=translate[language_code]["cityline_account"])
    lbl_urbtix_account.config(text=translate[language_code]["urbtix_account"])
    lbl_hkticketing_account.config(text=translate[language_code]["hkticketing_account"])
    lbl_kham_account.config(text=translate[language_code]["kham_account"])
    lbl_ticket_account.config(text=translate[language_code]["ticket_account"])
    lbl_udn_account.config(text=translate[language_code]["udn_account"])
    lbl_ticketplus_account.config(text=translate[language_code]["ticketplus_account"])

    lbl_password.config(text=translate[language_code]["password"])
    #lbl_facebook_password.config(text=translate[language_code]["facebook_password"])
    #lbl_kktix_password.config(text=translate[language_code]["kktix_password"])
    #lbl_cityline_password.config(text=translate[language_code]["cityline_password"])
    #lbl_urbtix_password.config(text=translate[language_code]["urbtix_password"])
    #lbl_hkticketing_password.config(text=translate[language_code]["hkticketing_password"])
    #lbl_kham_password.config(text=translate[language_code]["kham_password"])
    #lbl_ticket_password.config(text=translate[language_code]["ticket_password"])
    #lbl_ticketplus_password.config(text=translate[language_code]["ticketplus_password"])

    lbl_save_password_alert.config(text=translate[language_code]["save_password_alert"])

    lbl_play_ticket_sound.config(text=translate[language_code]["play_ticket_sound"])
    lbl_play_order_sound.config(text=translate[language_code]["play_order_sound"])
    lbl_play_sound_filename.config(text=translate[language_code]["play_sound_filename"])

    lbl_slogan.config(text=translate[language_code]["maxbot_slogan"])
    lbl_help.config(text=translate[language_code]["help"])
    lbl_donate.config(text=translate[language_code]["donate"])
    lbl_release.config(text=translate[language_code]["release"])

    global btn_run
    global btn_save
    global btn_exit
    global btn_restore_defaults
    global btn_launcher

    global btn_idle
    global btn_resume

    btn_run.config(text=translate[language_code]["run"])
    btn_save.config(text=translate[language_code]["save"])
    if btn_exit:
        btn_exit.config(text=translate[language_code]["exit"])
    btn_restore_defaults.config(text=translate[language_code]["restore_defaults"])
    btn_launcher.config(text=translate[language_code]["config_launcher"])

    btn_idle.config(text=translate[language_code]["idle"])
    btn_resume.config(text=translate[language_code]["resume"])

def callbackHomepageOnChange(event):
    showHideBlocks()

def callbackDateAutoOnChange():
    showHideTixcraftBlocks()

def callbackAreaAutoOnChange():
    showHideAreaBlocks()

def showHideBlocks():
    global UI_PADDING_X

    global frame_group_kktix
    global frame_group_kktix_index
    global frame_group_tixcraft
    global frame_group_tixcraft_index

    global combo_homepage

    new_homepage = ""
    if 'combo_homepage' in globals():
        new_homepage = combo_homepage.get().strip()
        #print("new homepage value:", new_homepage)

    BLOCK_STYLE_TIXCRAFT = 0
    BLOCK_STYLE_KKTIX = 1
    STYLE_KKTIX_DOMAIN_LIST = ['kktix']

    global combo_webdriver_type
    if 'combo_webdriver_type' in globals():
        if 'cityline.com' in new_homepage:
            combo_webdriver_type.set("nodriver")

    show_block_index = BLOCK_STYLE_TIXCRAFT
    for domain_name in STYLE_KKTIX_DOMAIN_LIST:
        if domain_name in new_homepage:
            show_block_index = BLOCK_STYLE_KKTIX

    if 'frame_group_kktix' in globals():
        if show_block_index == BLOCK_STYLE_KKTIX:
            frame_group_kktix.grid(column=0, row=frame_group_kktix_index, padx=UI_PADDING_X)
            frame_group_tixcraft.grid_forget()
        else:
            frame_group_tixcraft.grid(column=0, row=frame_group_tixcraft_index, padx=UI_PADDING_X)
            frame_group_kktix.grid_forget()

        showHideTixcraftBlocks()

def showHideOcrCaptchaWithSubmit():
    global chk_state_ocr_captcha
    is_ocr_captcha_enable = bool(chk_state_ocr_captcha.get())

    global ocr_captcha_force_submit_index
    global lbl_ocr_captcha_force_submit
    global chk_ocr_captcha_force_submit

    global lbl_ocr_captcha_ddddocr_beta
    global chk_ocr_captcha_ddddocr_beta

    if is_ocr_captcha_enable:
        # show.
        lbl_ocr_captcha_force_submit.grid(column=0, row=ocr_captcha_force_submit_index, sticky = E)
        chk_ocr_captcha_force_submit.grid(column=1, row=ocr_captcha_force_submit_index, sticky = W)

        lbl_ocr_captcha_ddddocr_beta.grid(column=0, row=ocr_captcha_force_submit_index-1, sticky = E)
        chk_ocr_captcha_ddddocr_beta.grid(column=1, row=ocr_captcha_force_submit_index-1, sticky = W)
    else:
        # hide
        lbl_ocr_captcha_force_submit.grid_forget()
        chk_ocr_captcha_force_submit.grid_forget()

        lbl_ocr_captcha_ddddocr_beta.grid_forget()
        chk_ocr_captcha_ddddocr_beta.grid_forget()

# purpose: show detail blocks if master field is enable.
def showHideTixcraftBlocks():
    # for tixcraft show/hide enable.
    global chk_state_date_auto_select

    global date_auto_select_mode_index
    global lbl_date_auto_select_mode
    global combo_date_auto_select_mode

    global date_keyword_index
    global lbl_date_keyword
    global txt_date_keyword

    is_date_set_to_enable = bool(chk_state_date_auto_select.get())

    if is_date_set_to_enable:
        # show
        lbl_date_auto_select_mode.grid(column=0, row=date_auto_select_mode_index, sticky = E)
        combo_date_auto_select_mode.grid(column=1, row=date_auto_select_mode_index, sticky = W)

        lbl_date_keyword.grid(column=0, row=date_keyword_index, sticky = E+N)
        txt_date_keyword.grid(column=1, row=date_keyword_index, sticky = W)
    else:
        # hide
        lbl_date_auto_select_mode.grid_forget()
        combo_date_auto_select_mode.grid_forget()

        lbl_date_keyword.grid_forget()
        txt_date_keyword.grid_forget()


# purpose: show detail of area block.
def showHideAreaBlocks():
    # for tixcraft show/hide enable.
    global chk_state_area_auto_select

    global area_auto_select_mode_index
    global lbl_area_auto_select_mode
    global combo_area_auto_select_mode

    area_keyword_index = area_auto_select_mode_index + 1
    keyword_exclude_index = area_auto_select_mode_index + 2

    global lbl_area_keyword
    global txt_area_keyword

    global lbl_keyword_exclude
    global txt_keyword_exclude

    is_area_set_to_enable = bool(chk_state_area_auto_select.get())

    if is_area_set_to_enable:
        # show
        lbl_area_auto_select_mode.grid(column=0, row=area_auto_select_mode_index, sticky = E)
        combo_area_auto_select_mode.grid(column=1, row=area_auto_select_mode_index, sticky = W)

        lbl_area_keyword.grid(column=0, row=area_keyword_index, sticky = E+N)
        txt_area_keyword.grid(column=1, row=area_keyword_index, sticky = W)

        lbl_keyword_exclude.grid(column=0, row=keyword_exclude_index, sticky = E+N)
        txt_keyword_exclude.grid(column=1, row=keyword_exclude_index, sticky = W)

    else:
        # hide
        lbl_area_auto_select_mode.grid_forget()
        combo_area_auto_select_mode.grid_forget()

        lbl_area_keyword.grid_forget()
        txt_area_keyword.grid_forget()

        lbl_keyword_exclude.grid_forget()
        txt_keyword_exclude.grid_forget()


def on_homepage_configure(event):
    font = tkfont.nametofont(str(event.widget.cget('font')))
    width = font.measure(CONST_SUPPORTED_SITES[len(CONST_SUPPORTED_SITES)-1] + "0") - event.width
    style = ttk.Style()
    style.configure('TCombobox', postoffset=(0,0,width,0))

def PreferenctTab(root, config_dict, language_code, UI_PADDING_X):
    # output config:
    print("setting app version:", CONST_APP_VERSION)
    print("python version:", platform.python_version())
    print("platform:", platform.platform())

    global lbl_homepage
    global lbl_ticket_number

    global lbl_kktix
    global lbl_tixcraft

    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    # first row need padding Y
    lbl_homepage = Label(frame_group_header, text=translate[language_code]['homepage'])
    lbl_homepage.grid(column=0, row=group_row_count, sticky = E)

    global combo_homepage
    combo_homepage = ttk.Combobox(frame_group_header, width=30)
    combo_homepage['values'] = CONST_SUPPORTED_SITES
    combo_homepage.set(config_dict["homepage"])
    combo_homepage.bind("<<ComboboxSelected>>", callbackHomepageOnChange)
    #combo_homepage.bind('<Configure>', on_homepage_configure)
    combo_homepage.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    lbl_ticket_number = Label(frame_group_header, text=translate[language_code]['ticket_number'])
    lbl_ticket_number.grid(column=0, row=group_row_count, sticky = E)

    global combo_ticket_number
    # for text format.
    # PS: some user keyin wrong type. @_@;
    '''
    global combo_ticket_number_value
    combo_ticket_number_value = StringVar(frame_group_header, value=ticket_number)
    combo_ticket_number = Entry(frame_group_header, width=30, textvariable = combo_ticket_number_value)
    combo_ticket_number.grid(column=1, row=group_row_count, sticky = W)
    '''
    combo_ticket_number = ttk.Combobox(frame_group_header, state="readonly", width=30)
    combo_ticket_number['values']= ("1","2","3","4","5","6","7","8","9","10","11","12")
    #combo_ticket_number.current(0)
    combo_ticket_number.set(str(config_dict["ticket_number"]))
    combo_ticket_number.grid(column=1, row=group_row_count, sticky = W)

    frame_group_header.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)

    row_count+=1

    # for sub group KKTix.
    global frame_group_kktix
    frame_group_kktix = Frame(root)
    group_row_count = 0

    # start sub group...
    group_row_count+=1

    global lbl_auto_press_next_step_button
    lbl_auto_press_next_step_button = Label(frame_group_kktix, text=translate[language_code]['auto_press_next_step_button'])
    lbl_auto_press_next_step_button.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_auto_press_next_step_button
    chk_state_auto_press_next_step_button = BooleanVar()
    chk_state_auto_press_next_step_button.set(config_dict["kktix"]["auto_press_next_step_button"])

    global chk_auto_press_next_step_button
    chk_auto_press_next_step_button = Checkbutton(frame_group_kktix, text=translate[language_code]['enable'], variable=chk_state_auto_press_next_step_button)
    chk_auto_press_next_step_button.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_auto_fill_ticket_number
    lbl_auto_fill_ticket_number = Label(frame_group_kktix, text=translate[language_code]['auto_fill_ticket_number'])
    lbl_auto_fill_ticket_number.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_auto_fill_ticket_number
    chk_state_auto_fill_ticket_number = BooleanVar()
    chk_state_auto_fill_ticket_number.set(config_dict["kktix"]["auto_fill_ticket_number"])

    global chk_auto_fill_ticket_number
    chk_auto_fill_ticket_number = Checkbutton(frame_group_kktix, text=translate[language_code]['enable'], variable=chk_state_auto_fill_ticket_number)
    chk_auto_fill_ticket_number.grid(column=1, row=group_row_count, sticky = W)

    global frame_group_kktix_index
    frame_group_kktix_index = row_count
    #PS: don't need show when onload(), because show/hide block will load again.
    #frame_group_kktix.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)

    row_count+=1

    # for sub group tixcraft.
    global frame_group_tixcraft
    frame_group_tixcraft = Frame(root)
    group_row_count = 0

    # start sub group.
    group_row_count+=1

    global lbl_date_auto_select
    lbl_date_auto_select = Label(frame_group_tixcraft, text=translate[language_code]['date_auto_select'])
    lbl_date_auto_select.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_date_auto_select
    chk_state_date_auto_select = BooleanVar()
    chk_state_date_auto_select.set(config_dict["date_auto_select"]["enable"])

    global chk_date_auto_select
    chk_date_auto_select = Checkbutton(frame_group_tixcraft, text=translate[language_code]['enable'], variable=chk_state_date_auto_select, command=callbackDateAutoOnChange)
    chk_date_auto_select.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global date_auto_select_mode_index
    date_auto_select_mode_index = group_row_count

    global lbl_date_auto_select_mode
    lbl_date_auto_select_mode = Label(frame_group_tixcraft, text=translate[language_code]['date_select_order'])
    lbl_date_auto_select_mode.grid(column=0, row=date_auto_select_mode_index, sticky = E)

    global combo_date_auto_select_mode
    combo_date_auto_select_mode = ttk.Combobox(frame_group_tixcraft, state="readonly", width=30)
    combo_date_auto_select_mode['values']= CONST_SELECT_OPTIONS_DEFAULT
    combo_date_auto_select_mode.set(config_dict["date_auto_select"]["mode"])
    combo_date_auto_select_mode.grid(column=1, row=date_auto_select_mode_index, sticky = W)

    group_row_count+=1

    global date_keyword_index
    date_keyword_index = group_row_count

    global lbl_date_keyword
    lbl_date_keyword = Label(frame_group_tixcraft, text=translate[language_code]['date_keyword'])
    lbl_date_keyword.grid(column=0, row=date_keyword_index, sticky = E+N)

    global txt_date_keyword
    txt_date_keyword = Text(frame_group_tixcraft, width=30, height=4)
    txt_date_keyword.grid(column=1, row=group_row_count, sticky = W)
    txt_date_keyword.insert("1.0", config_dict["date_auto_select"]["date_keyword"].strip())

    group_row_count+=1

    global lbl_pass_date_is_sold_out
    lbl_pass_date_is_sold_out = Label(frame_group_tixcraft, text=translate[language_code]['pass_date_is_sold_out'])
    lbl_pass_date_is_sold_out.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_pass_date_is_sold_out
    chk_state_pass_date_is_sold_out = BooleanVar()
    chk_state_pass_date_is_sold_out.set(config_dict["tixcraft"]["pass_date_is_sold_out"])

    global chk_pass_date_is_sold_out
    chk_pass_date_is_sold_out = Checkbutton(frame_group_tixcraft, text=translate[language_code]['enable'], variable=chk_state_pass_date_is_sold_out)
    chk_pass_date_is_sold_out.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_auto_reload_coming_soon_page
    lbl_auto_reload_coming_soon_page = Label(frame_group_tixcraft, text=translate[language_code]['auto_reload_coming_soon_page'])
    lbl_auto_reload_coming_soon_page.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_auto_reload_coming_soon_page
    chk_state_auto_reload_coming_soon_page = BooleanVar()
    chk_state_auto_reload_coming_soon_page.set(config_dict["tixcraft"]["auto_reload_coming_soon_page"])

    global chk_auto_reload_coming_soon_page
    chk_auto_reload_coming_soon_page = Checkbutton(frame_group_tixcraft, text=translate[language_code]['enable'], variable=chk_state_auto_reload_coming_soon_page)
    chk_auto_reload_coming_soon_page.grid(column=1, row=group_row_count, sticky = W)

    # final flush.
    global frame_group_tixcraft_index
    frame_group_tixcraft_index = row_count
    #PS: don't need show when onload(), because show/hide block will load again.
    #frame_group_tixcraft.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)

    row_count += 1

    showHideBlocks()

    # for area block.
    global frame_group_area
    frame_group_area = Frame(root)
    group_row_count = 0

    global lbl_area_auto_select
    lbl_area_auto_select = Label(frame_group_area, text=translate[language_code]['area_auto_select'])
    lbl_area_auto_select.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_area_auto_select
    chk_state_area_auto_select = BooleanVar()
    chk_state_area_auto_select.set(config_dict["area_auto_select"]["enable"])

    global chk_area_auto_select
    chk_area_auto_select = Checkbutton(frame_group_area, text=translate[language_code]['enable'], variable=chk_state_area_auto_select, command=callbackAreaAutoOnChange)
    chk_area_auto_select.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global area_auto_select_mode_index
    area_auto_select_mode_index = group_row_count

    global lbl_area_auto_select_mode
    lbl_area_auto_select_mode = Label(frame_group_area, text=translate[language_code]['area_auto_select'])
    lbl_area_auto_select_mode.grid(column=0, row=area_auto_select_mode_index, sticky = E)

    global combo_area_auto_select_mode
    combo_area_auto_select_mode = ttk.Combobox(frame_group_area, state="readonly", width=30)
    combo_area_auto_select_mode['values']= CONST_SELECT_OPTIONS_DEFAULT
    combo_area_auto_select_mode.set(config_dict["area_auto_select"]["mode"])
    combo_area_auto_select_mode.grid(column=1, row=area_auto_select_mode_index, sticky = W)

    group_row_count+=1

    global lbl_area_keyword
    lbl_area_keyword = Label(frame_group_area, text=translate[language_code]['area_keyword'])
    lbl_area_keyword.grid(column=0, row=group_row_count, sticky = E+N)

    global txt_area_keyword
    txt_area_keyword = Text(frame_group_area, width=30, height=4)
    txt_area_keyword.grid(column=1, row=group_row_count, sticky = W)
    txt_area_keyword.insert("1.0", config_dict["area_auto_select"]["area_keyword"].strip())

    group_row_count+=1

    global lbl_keyword_exclude
    lbl_keyword_exclude = Label(frame_group_area, text=translate[language_code]['keyword_exclude'])
    lbl_keyword_exclude.grid(column=0, row=group_row_count, sticky = E+N)

    global txt_keyword_exclude
    txt_keyword_exclude = Text(frame_group_area, width=30, height=4)
    txt_keyword_exclude.grid(column=1, row=group_row_count, sticky = W)
    txt_keyword_exclude.insert("1.0", config_dict["keyword_exclude"].strip())

    group_row_count+=1

    global lbl_keyword_usage
    lbl_keyword_usage = Label(frame_group_area, text=translate[language_code]['keyword_usage'])
    lbl_keyword_usage.grid(column=1, row=group_row_count, sticky = W)

    # flush
    frame_group_area.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)

    showHideAreaBlocks()

def AdvancedTab(root, config_dict, language_code, UI_PADDING_X):
    browser_options = ("chrome","firefox","edge","safari","brave")
    webdriver_type_options = (CONST_WEBDRIVER_TYPE_SELENIUM, CONST_WEBDRIVER_TYPE_UC)

    not_support_python_version = ["3.6.", "3.7.", "3.8."]
    is_current_version_after_3_9 = True
    for not_support_ver in not_support_python_version:
        current_version = platform.python_version()
        if current_version[:4] == not_support_ver :
            is_current_version_after_3_9 = False
            break
    if is_current_version_after_3_9:
        webdriver_type_options = (CONST_WEBDRIVER_TYPE_SELENIUM, CONST_WEBDRIVER_TYPE_UC, CONST_WEBDRIVER_TYPE_NODRIVER)
        pass

    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    # assign default value.
    play_sound_filename = config_dict["advanced"]["play_sound"]["filename"].strip()
    if play_sound_filename is None:
        play_sound_filename = ""
    if len(play_sound_filename)==0:
        play_sound_filename = play_sound_filename_default

    global lbl_browser
    lbl_browser = Label(frame_group_header, text=translate[language_code]['browser'])
    lbl_browser.grid(column=0, row=group_row_count, sticky = E)

    global combo_browser
    combo_browser = ttk.Combobox(frame_group_header, state="readonly", width=30)
    combo_browser['values']= browser_options
    combo_browser.set(config_dict['browser'])
    combo_browser.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_language
    lbl_language = Label(frame_group_header, text=translate[language_code]['language'])
    lbl_language.grid(column=0, row=group_row_count, sticky = E)

    global combo_language
    combo_language = ttk.Combobox(frame_group_header, state="readonly", width=30)
    combo_language['values']= ("English","繁體中文","簡体中文","日本語")
    combo_language.set(config_dict['language'])
    combo_language.bind("<<ComboboxSelected>>", callbackLanguageOnChange)
    combo_language.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_ocr_captcha_image_source
    lbl_ocr_captcha_image_source = Label(frame_group_header, text=translate[language_code]['ocr_captcha_image_source'])
    lbl_ocr_captcha_image_source.grid(column=0, row=group_row_count, sticky = E)

    global combo_ocr_captcha_image_source
    combo_ocr_captcha_image_source = ttk.Combobox(frame_group_header, state="readonly", width=30)
    combo_ocr_captcha_image_source['values']= (CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER, CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS)
    combo_ocr_captcha_image_source.set(config_dict["ocr_captcha"]["image_source"])
    combo_ocr_captcha_image_source.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_webdriver_type
    lbl_webdriver_type = Label(frame_group_header, text=translate[language_code]['webdriver_type'])
    lbl_webdriver_type.grid(column=0, row=group_row_count, sticky = E)

    global combo_webdriver_type
    combo_webdriver_type = ttk.Combobox(frame_group_header, state="readonly", width=30)
    combo_webdriver_type['values']= webdriver_type_options
    combo_webdriver_type.set(config_dict["webdriver_type"])
    combo_webdriver_type.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_play_ticket_sound
    lbl_play_ticket_sound = Label(frame_group_header, text=translate[language_code]['play_ticket_sound'])
    lbl_play_ticket_sound.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_play_ticket_sound
    chk_state_play_ticket_sound = BooleanVar()
    chk_state_play_ticket_sound.set(config_dict["advanced"]["play_sound"]["ticket"])

    global chk_play_ticket_sound
    chk_play_ticket_sound = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_play_ticket_sound)
    chk_play_ticket_sound.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_play_order_sound
    lbl_play_order_sound = Label(frame_group_header, text=translate[language_code]['play_order_sound'])
    lbl_play_order_sound.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_play_order_sound
    chk_state_play_order_sound = BooleanVar()
    chk_state_play_order_sound.set(config_dict["advanced"]["play_sound"]["order"])

    global chk_play_order_sound
    chk_play_order_sound = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_play_order_sound)
    chk_play_order_sound.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_play_sound_filename
    lbl_play_sound_filename = Label(frame_group_header, text=translate[language_code]['play_sound_filename'])
    lbl_play_sound_filename.grid(column=0, row=group_row_count, sticky = E)

    global txt_play_sound_filename
    txt_play_sound_filename_value = StringVar(frame_group_header, value=play_sound_filename)
    txt_play_sound_filename = Entry(frame_group_header, width=30, textvariable = txt_play_sound_filename_value)
    txt_play_sound_filename.grid(column=1, row=group_row_count, sticky = W)

    icon_play_filename = "icon_play_1.gif"
    icon_play_img = PhotoImage(file=icon_play_filename)

    lbl_icon_play = Label(frame_group_header, image=icon_play_img, cursor="hand2")
    lbl_icon_play.image = icon_play_img
    lbl_icon_play.grid(column=2, row=group_row_count, sticky = W)
    lbl_icon_play.bind("<Button-1>", lambda e: btn_preview_sound_clicked())

    group_row_count +=1

    global lbl_auto_reload_page_interval
    lbl_auto_reload_page_interval = Label(frame_group_header, text=translate[language_code]['auto_reload_page_interval'])
    lbl_auto_reload_page_interval.grid(column=0, row=group_row_count, sticky = E)

    global txt_auto_reload_page_interval
    txt_auto_reload_page_interval_value = StringVar(frame_group_header, value=config_dict["advanced"]["auto_reload_page_interval"])
    txt_auto_reload_page_interval = Entry(frame_group_header, width=30, textvariable = txt_auto_reload_page_interval_value)
    txt_auto_reload_page_interval.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_kktix_status_api
    lbl_kktix_status_api = Label(frame_group_header, text=translate[language_code]['kktix_status_api'])
    lbl_kktix_status_api.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_kktix_status_api
    chk_state_kktix_status_api = BooleanVar()
    chk_state_kktix_status_api.set(config_dict["advanced"]["kktix_status_api"])

    global chk_kktix_status_api
    chk_kktix_status_api = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_kktix_status_api)
    chk_kktix_status_api.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_max_dwell_time
    lbl_max_dwell_time = Label(frame_group_header, text=translate[language_code]['max_dwell_time'])
    lbl_max_dwell_time.grid(column=0, row=group_row_count, sticky = E)

    global txt_max_dwell_time
    txt_max_dwell_time_value = StringVar(frame_group_header, value=config_dict["advanced"]["max_dwell_time"])
    txt_max_dwell_time = Entry(frame_group_header, width=30, textvariable = txt_max_dwell_time_value)
    txt_max_dwell_time.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_reset_browser_interval
    lbl_reset_browser_interval = Label(frame_group_header, text=translate[language_code]['reset_browser_interval'])
    lbl_reset_browser_interval.grid(column=0, row=group_row_count, sticky = E)

    global txt_reset_browser_interval
    txt_reset_browser_interval_value = StringVar(frame_group_header, value=config_dict["advanced"]["reset_browser_interval"])
    txt_reset_browser_interval = Entry(frame_group_header, width=30, textvariable = txt_reset_browser_interval_value)
    txt_reset_browser_interval.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_proxy_server_port
    lbl_proxy_server_port = Label(frame_group_header, text=translate[language_code]['proxy_server_port'])
    lbl_proxy_server_port.grid(column=0, row=group_row_count, sticky = E)

    global txt_proxy_server_port
    txt_proxy_server_port_value = StringVar(frame_group_header, value=config_dict["advanced"]["proxy_server_port"])
    txt_proxy_server_port = Entry(frame_group_header, width=30, textvariable = txt_proxy_server_port_value)
    txt_proxy_server_port.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_window_size
    lbl_window_size = Label(frame_group_header, text=translate[language_code]['window_size'])
    lbl_window_size.grid(column=0, row=group_row_count, sticky = E)

    global txt_window_size
    txt_window_size_value = StringVar(frame_group_header, value=config_dict["advanced"]["window_size"])
    txt_window_size = Entry(frame_group_header, width=30, textvariable = txt_window_size_value)
    txt_window_size.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_chrome_extension
    lbl_chrome_extension = Label(frame_group_header, text=translate[language_code]['chrome_extension'])
    lbl_chrome_extension.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_chrome_extension
    chk_state_chrome_extension = BooleanVar()
    chk_state_chrome_extension.set(config_dict["advanced"]["chrome_extension"])

    global chk_chrome_extension
    chk_chrome_extension = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_chrome_extension)
    chk_chrome_extension.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_adjacent_seat
    lbl_adjacent_seat = Label(frame_group_header, text=translate[language_code]['disable_adjacent_seat'])
    lbl_adjacent_seat.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_adjacent_seat
    chk_state_adjacent_seat = BooleanVar()
    chk_state_adjacent_seat.set(config_dict["advanced"]["disable_adjacent_seat"])

    global chk_adjacent_seat
    chk_adjacent_seat = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_adjacent_seat)
    chk_adjacent_seat.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_hide_some_image
    lbl_hide_some_image = Label(frame_group_header, text=translate[language_code]['hide_some_image'])
    lbl_hide_some_image.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_hide_some_image
    chk_state_hide_some_image = BooleanVar()
    chk_state_hide_some_image.set(config_dict["advanced"]["hide_some_image"])

    global chk_hide_some_image
    chk_hide_some_image = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_hide_some_image)
    chk_hide_some_image.grid(column=1, row=group_row_count, sticky = W)

    global lbl_hide_some_image_recommand
    lbl_hide_some_image_recommand = Label(frame_group_header, text=translate[language_code]['recommand_enable'])
    lbl_hide_some_image_recommand.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_block_facebook_network
    lbl_block_facebook_network = Label(frame_group_header, text=translate[language_code]['block_facebook_network'])
    lbl_block_facebook_network.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_block_facebook_network
    chk_state_block_facebook_network = BooleanVar()
    chk_state_block_facebook_network.set(config_dict["advanced"]["block_facebook_network"])

    global chk_block_facebook_network
    chk_block_facebook_network = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_block_facebook_network)
    chk_block_facebook_network.grid(column=1, row=group_row_count, sticky = W)

    global lbl_block_facebook_network_recommand
    lbl_block_facebook_network_recommand = Label(frame_group_header, text=translate[language_code]['recommand_enable'])
    lbl_block_facebook_network_recommand.grid(column=2, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_headless
    lbl_headless = Label(frame_group_header, text=translate[language_code]['headless'])
    lbl_headless.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_headless
    chk_state_headless = BooleanVar()
    chk_state_headless.set(config_dict['advanced']["headless"])

    global chk_headless
    chk_headless = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_headless)
    chk_headless.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_verbose
    lbl_verbose = Label(frame_group_header, text=translate[language_code]['verbose'])
    # maybe enable in future.
    #lbl_verbose.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_verbose
    chk_state_verbose = BooleanVar()
    chk_state_verbose.set(config_dict['advanced']["verbose"])

    global chk_verbose
    chk_verbose = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_verbose)
    # maybe enable in future.
    #chk_verbose.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_ocr_captcha
    lbl_ocr_captcha = Label(frame_group_header, text=translate[language_code]["ocr_captcha"])
    lbl_ocr_captcha.grid(column=0, row=group_row_count, sticky = E)

    frame_group_ddddocr_enable = Frame(frame_group_header)

    global chk_state_ocr_captcha
    chk_state_ocr_captcha = BooleanVar()
    chk_state_ocr_captcha.set(config_dict["ocr_captcha"]["enable"])

    global chk_ocr_captcha
    chk_ocr_captcha = Checkbutton(frame_group_ddddocr_enable, text=translate[language_code]['enable'], variable=chk_state_ocr_captcha, command=showHideOcrCaptchaWithSubmit)
    chk_ocr_captcha.grid(column=0, row=0, sticky = W)

    global lbl_ocr_captcha_not_support_arm
    lbl_ocr_captcha_not_support_arm = Label(frame_group_ddddocr_enable, fg="red", text=translate[language_code]['ocr_captcha_not_support_arm'])
    if util.is_arm():
        lbl_ocr_captcha_not_support_arm.grid(column=1, row=0, sticky = E)

    frame_group_ddddocr_enable.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_ocr_captcha_ddddocr_beta
    lbl_ocr_captcha_ddddocr_beta = Label(frame_group_header, text=translate[language_code]['ocr_captcha_ddddocr_beta'])
    lbl_ocr_captcha_ddddocr_beta.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_ocr_captcha_ddddocr_beta
    chk_state_ocr_captcha_ddddocr_beta = BooleanVar()
    chk_state_ocr_captcha_ddddocr_beta.set(config_dict["ocr_captcha"]["beta"])

    global chk_ocr_captcha_ddddocr_beta
    chk_ocr_captcha_ddddocr_beta = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_ocr_captcha_ddddocr_beta)
    chk_ocr_captcha_ddddocr_beta.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global ocr_captcha_force_submit_index
    ocr_captcha_force_submit_index = group_row_count

    global lbl_ocr_captcha_force_submit
    lbl_ocr_captcha_force_submit = Label(frame_group_header, text=translate[language_code]['ocr_captcha_force_submit'])
    lbl_ocr_captcha_force_submit.grid(column=0, row=ocr_captcha_force_submit_index, sticky = E)

    global chk_state_ocr_captcha_force_submit
    chk_state_ocr_captcha_force_submit = BooleanVar()
    chk_state_ocr_captcha_force_submit.set(config_dict["ocr_captcha"]["force_submit"])

    global chk_ocr_captcha_force_submit
    chk_ocr_captcha_force_submit = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_ocr_captcha_force_submit)
    chk_ocr_captcha_force_submit.grid(column=1, row=group_row_count, sticky = W)

    frame_group_header.grid(column=0, row=row_count, padx=UI_PADDING_X)

    showHideOcrCaptchaWithSubmit()

def VerificationTab(root, config_dict, language_code, UI_PADDING_X):
    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    global lbl_user_guess_string_description
    lbl_user_guess_string_description = Label(frame_group_header, text=translate[language_code]['user_guess_string'])
    lbl_user_guess_string_description.grid(column=1, row=group_row_count, sticky =  W)

    group_row_count+=1

    global lbl_user_guess_string
    lbl_user_guess_string = Label(frame_group_header, text=translate[language_code]['local_dictionary'])
    lbl_user_guess_string.grid(column=0, row=group_row_count, sticky =  E+N)

    global txt_user_guess_string
    txt_user_guess_string = Text(frame_group_header, width=30, height=4)
    txt_user_guess_string.grid(column=1, row=group_row_count, sticky = W)
    txt_user_guess_string.insert("1.0", config_dict["advanced"]["user_guess_string"].strip())

    group_row_count+=1

    global lbl_remote_url
    lbl_remote_url = Label(frame_group_header, text=translate[language_code]['remote_url'])
    lbl_remote_url.grid(column=0, row=group_row_count, sticky = E+N)

    global txt_remote_url
    txt_remote_url = Text(frame_group_header, width=30, height=4)
    txt_remote_url.grid(column=1, row=group_row_count, sticky = W)
    txt_remote_url.insert("1.0", config_dict['advanced']["remote_url"].strip())

    icon_preview_text_filename = "icon_chrome_4.gif"
    icon_preview_text_img = PhotoImage(file=icon_preview_text_filename)

    lbl_icon_preview_text = Label(frame_group_header, image=icon_preview_text_img, cursor="hand2")
    lbl_icon_preview_text.image = icon_preview_text_img
    lbl_icon_preview_text.grid(column=2, row=group_row_count, sticky = W+N)
    lbl_icon_preview_text.bind("<Button-1>", lambda e: btn_open_text_server_clicked())

    group_row_count+=1

    global lbl_online_dictionary_preview
    lbl_online_dictionary_preview = Label(frame_group_header, text=translate[language_code]['preview'])
    lbl_online_dictionary_preview.grid(column=0, row=group_row_count, sticky = E)

    global lbl_online_dictionary_preview_data
    lbl_online_dictionary_preview_data = Label(frame_group_header, text="")
    lbl_online_dictionary_preview_data.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_auto_guess_options
    lbl_auto_guess_options = Label(frame_group_header, text=translate[language_code]['auto_guess_options'])
    lbl_auto_guess_options.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_auto_guess_options
    chk_state_auto_guess_options = BooleanVar()
    chk_state_auto_guess_options.set(config_dict["advanced"]["auto_guess_options"])

    global chk_auto_guess_options
    chk_auto_guess_options = Checkbutton(frame_group_header, text=translate[language_code]['enable'], variable=chk_state_auto_guess_options)
    chk_auto_guess_options.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    frame_group_header.grid(column=0, row=row_count, padx=UI_PADDING_X)

def ServerTab(root, config_dict, language_code, UI_PADDING_X):
    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    global lbl_server_url
    lbl_server_url = Label(frame_group_header, text=translate[language_code]['server_url'])
    lbl_server_url.grid(column=0, row=group_row_count, sticky = E)

    local_ip = util.get_ip_address()
    ip_address = "http://%s:%d/" % (local_ip, CONST_SERVER_PORT)
    global lbl_ip_address
    lbl_ip_address = Label(frame_group_header, text=ip_address)
    lbl_ip_address.grid(column=1, row=group_row_count, sticky = W)

    icon_copy_filename = "icon_copy_2.gif"
    icon_copy_img = PhotoImage(file=icon_copy_filename)

    lbl_icon_copy_ip = Label(frame_group_header, image=icon_copy_img, cursor="hand2")
    lbl_icon_copy_ip.image = icon_copy_img
    lbl_icon_copy_ip.grid(column=2, row=group_row_count, sticky = W+N)
    lbl_icon_copy_ip.bind("<Button-1>", lambda e: btn_copy_ip_clicked())

    group_row_count += 1

    global lbl_question
    lbl_question = Label(frame_group_header, text=translate[language_code]['question'])
    lbl_question.grid(column=0, row=group_row_count, sticky = E+N)

    global txt_question
    txt_question = Text(frame_group_header, width=50, height=22)
    txt_question.grid(column=1, row=group_row_count, sticky = W)
    txt_question.insert("1.0", "")

    lbl_icon_copy_question = Label(frame_group_header, image=icon_copy_img, cursor="hand2")
    lbl_icon_copy_question.image = icon_copy_img
    #lbl_icon_copy_question.grid(column=2, row=group_row_count, sticky = W+N)
    lbl_icon_copy_question.bind("<Button-1>", lambda e: btn_copy_question_clicked())

    icon_query_filename = "icon_query_5.gif"
    icon_query_img = PhotoImage(file=icon_query_filename)

    lbl_icon_query_question = Label(frame_group_header, image=icon_query_img, cursor="hand2")
    lbl_icon_query_question.image = icon_query_img
    lbl_icon_query_question.grid(column=2, row=group_row_count, sticky = W+N)
    lbl_icon_query_question.bind("<Button-1>", lambda e: btn_query_question_clicked())

    group_row_count += 1

    global lbl_answer
    lbl_answer = Label(frame_group_header, text=translate[language_code]['answer'])
    lbl_answer.grid(column=0, row=group_row_count, sticky = E)

    global txt_answer
    global txt_answer_value
    txt_answer_value = StringVar(frame_group_header, value="")
    txt_answer = Entry(frame_group_header, width=30, textvariable = txt_answer_value)
    txt_answer.grid(column=1, row=group_row_count, sticky = W)
    txt_answer.bind('<Control-v>', lambda e: btn_paste_answer_by_user())

    frame_group_header.grid(column=0, row=row_count, padx=UI_PADDING_X, pady=15)


def AutofillTab(root, config_dict, language_code, UI_PADDING_X):
    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    global lbl_tixcraft_sid
    lbl_tixcraft_sid = Label(frame_group_header, text=translate[language_code]['tixcraft_sid'])
    lbl_tixcraft_sid.grid(column=0, row=group_row_count, sticky = E)

    global txt_tixcraft_sid
    txt_tixcraft_sid_value = StringVar(frame_group_header, value=config_dict["advanced"]["tixcraft_sid"].strip())
    txt_tixcraft_sid = Entry(frame_group_header, width=30, textvariable = txt_tixcraft_sid_value, show="*")
    txt_tixcraft_sid.grid(column=1, row=group_row_count, columnspan=2, sticky = W)

    group_row_count +=1

    global lbl_ibon_ibonqware
    lbl_ibon_ibonqware = Label(frame_group_header, text=translate[language_code]['ibon_ibonqware'])
    lbl_ibon_ibonqware.grid(column=0, row=group_row_count, sticky = E)

    global txt_ibon_ibonqware
    txt_ibon_ibonqware_value = StringVar(frame_group_header, value=config_dict["advanced"]["ibonqware"].strip())
    txt_ibon_ibonqware = Entry(frame_group_header, width=30, textvariable = txt_ibon_ibonqware_value, show="*")
    txt_ibon_ibonqware.grid(column=1, row=group_row_count, columnspan=2, sticky = W)

    group_row_count +=1

    global lbl_password
    lbl_password = Label(frame_group_header, text=translate[language_code]['password'])
    lbl_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_facebook_account
    lbl_facebook_account = Label(frame_group_header, text=translate[language_code]['facebook_account'])
    lbl_facebook_account.grid(column=0, row=group_row_count, sticky = E)

    global txt_facebook_account
    txt_facebook_account_value = StringVar(frame_group_header, value=config_dict["advanced"]["facebook_account"].strip())
    txt_facebook_account = Entry(frame_group_header, width=15, textvariable = txt_facebook_account_value)
    txt_facebook_account.grid(column=1, row=group_row_count, sticky = W)

    global txt_facebook_password
    txt_facebook_password_value = StringVar(frame_group_header, value=util.decryptMe(config_dict["advanced"]["facebook_password"].strip()))
    txt_facebook_password = Entry(frame_group_header, width=15, textvariable = txt_facebook_password_value, show="*")
    txt_facebook_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_kktix_account
    lbl_kktix_account = Label(frame_group_header, text=translate[language_code]['kktix_account'])
    lbl_kktix_account.grid(column=0, row=group_row_count, sticky = E)

    global txt_kktix_account
    txt_kktix_account_value = StringVar(frame_group_header, value=config_dict["advanced"]["kktix_account"].strip())
    txt_kktix_account = Entry(frame_group_header, width=15, textvariable = txt_kktix_account_value)
    txt_kktix_account.grid(column=1, row=group_row_count, sticky = W)

    global txt_kktix_password
    txt_kktix_password_value = StringVar(frame_group_header, value=util.decryptMe(config_dict["advanced"]["kktix_password"].strip()))
    txt_kktix_password = Entry(frame_group_header, width=15, textvariable = txt_kktix_password_value, show="*")
    txt_kktix_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_fami_account
    lbl_fami_account = Label(frame_group_header, text=translate[language_code]['fami_account'])
    lbl_fami_account.grid(column=0, row=group_row_count, sticky = E)

    global txt_fami_account
    txt_fami_account_value = StringVar(frame_group_header, value=config_dict["advanced"]["fami_account"].strip())
    txt_fami_account = Entry(frame_group_header, width=15, textvariable = txt_fami_account_value)
    txt_fami_account.grid(column=1, row=group_row_count, sticky = W)

    global txt_fami_password
    txt_fami_password_value = StringVar(frame_group_header, value=util.decryptMe(config_dict["advanced"]["fami_password"].strip()))
    txt_fami_password = Entry(frame_group_header, width=15, textvariable = txt_fami_password_value, show="*")
    txt_fami_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_cityline_account
    lbl_cityline_account = Label(frame_group_header, text=translate[language_code]['cityline_account'])
    lbl_cityline_account.grid(column=0, row=group_row_count, sticky = E)

    global txt_cityline_account
    txt_cityline_account_value = StringVar(frame_group_header, value=config_dict["advanced"]["cityline_account"].strip())
    txt_cityline_account = Entry(frame_group_header, width=30, textvariable = txt_cityline_account_value)
    txt_cityline_account.grid(column=1, row=group_row_count, sticky = W, columnspan=2)

    global txt_cityline_password
    txt_cityline_password_value = StringVar(frame_group_header, value=util.decryptMe(config_dict["advanced"]["cityline_password"].strip()))
    txt_cityline_password = Entry(frame_group_header, width=15, textvariable = txt_cityline_password_value, show="*")
    #txt_cityline_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_urbtix_account
    lbl_urbtix_account = Label(frame_group_header, text=translate[language_code]['urbtix_account'])
    lbl_urbtix_account.grid(column=0, row=group_row_count, sticky = E)

    global txt_urbtix_account
    txt_urbtix_account_value = StringVar(frame_group_header, value=config_dict["advanced"]["urbtix_account"].strip())
    txt_urbtix_account = Entry(frame_group_header, width=15, textvariable = txt_urbtix_account_value)
    txt_urbtix_account.grid(column=1, row=group_row_count, sticky = W)

    global txt_urbtix_password
    txt_urbtix_password_value = StringVar(frame_group_header, value=util.decryptMe(config_dict["advanced"]["urbtix_password"].strip()))
    txt_urbtix_password = Entry(frame_group_header, width=15, textvariable = txt_urbtix_password_value, show="*")
    txt_urbtix_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_hkticketing_account
    lbl_hkticketing_account = Label(frame_group_header, text=translate[language_code]['hkticketing_account'])
    lbl_hkticketing_account.grid(column=0, row=group_row_count, sticky = E)

    global txt_hkticketing_account
    txt_hkticketing_account_value = StringVar(frame_group_header, value=config_dict["advanced"]["hkticketing_account"].strip())
    txt_hkticketing_account = Entry(frame_group_header, width=15, textvariable = txt_hkticketing_account_value)
    txt_hkticketing_account.grid(column=1, row=group_row_count, sticky = W)

    global txt_hkticketing_password
    txt_hkticketing_password_value = StringVar(frame_group_header, value=util.decryptMe(config_dict["advanced"]["hkticketing_password"].strip()))
    txt_hkticketing_password = Entry(frame_group_header, width=15, textvariable = txt_hkticketing_password_value, show="*")
    txt_hkticketing_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_kham_account
    lbl_kham_account = Label(frame_group_header, text=translate[language_code]['kham_account'])
    lbl_kham_account.grid(column=0, row=group_row_count, sticky = E)

    global txt_kham_account
    txt_kham_account_value = StringVar(frame_group_header, value=config_dict["advanced"]["kham_account"].strip())
    txt_kham_account = Entry(frame_group_header, width=15, textvariable = txt_kham_account_value)
    txt_kham_account.grid(column=1, row=group_row_count, sticky = W)

    global txt_kham_password
    txt_kham_password_value = StringVar(frame_group_header, value=util.decryptMe(config_dict["advanced"]["kham_password"].strip()))
    txt_kham_password = Entry(frame_group_header, width=15, textvariable = txt_kham_password_value, show="*")
    txt_kham_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_ticket_account
    lbl_ticket_account = Label(frame_group_header, text=translate[language_code]['ticket_account'])
    lbl_ticket_account.grid(column=0, row=group_row_count, sticky = E)

    global txt_ticket_account
    txt_ticket_account_value = StringVar(frame_group_header, value=config_dict["advanced"]["ticket_account"].strip())
    txt_ticket_account = Entry(frame_group_header, width=15, textvariable = txt_ticket_account_value)
    txt_ticket_account.grid(column=1, row=group_row_count, sticky = W)

    global txt_ticket_password
    txt_ticket_password_value = StringVar(frame_group_header, value=util.decryptMe(config_dict["advanced"]["ticket_password"].strip()))
    txt_ticket_password = Entry(frame_group_header, width=15, textvariable = txt_ticket_password_value, show="*")
    txt_ticket_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_udn_account
    lbl_udn_account = Label(frame_group_header, text=translate[language_code]['udn_account'])
    lbl_udn_account.grid(column=0, row=group_row_count, sticky = E)

    global txt_udn_account
    txt_udn_account_value = StringVar(frame_group_header, value=config_dict["advanced"]["udn_account"].strip())
    txt_udn_account = Entry(frame_group_header, width=15, textvariable = txt_udn_account_value)
    txt_udn_account.grid(column=1, row=group_row_count, sticky = W)

    global txt_udn_password
    txt_udn_password_value = StringVar(frame_group_header, value=util.decryptMe(config_dict["advanced"]["udn_password"].strip()))
    txt_udn_password = Entry(frame_group_header, width=15, textvariable = txt_udn_password_value, show="*")
    txt_udn_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_ticketplus_account
    lbl_ticketplus_account = Label(frame_group_header, text=translate[language_code]['ticketplus_account'])
    lbl_ticketplus_account.grid(column=0, row=group_row_count, sticky = E)

    global txt_ticketplus_account
    txt_ticketplus_account_value = StringVar(frame_group_header, value=config_dict["advanced"]["ticketplus_account"].strip())
    txt_ticketplus_account = Entry(frame_group_header, width=15, textvariable = txt_ticketplus_account_value)
    txt_ticketplus_account.grid(column=1, row=group_row_count, sticky = W)

    global txt_ticketplus_password
    txt_ticketplus_password_value = StringVar(frame_group_header, value=util.decryptMe(config_dict["advanced"]["ticketplus_password"].strip()))
    txt_ticketplus_password = Entry(frame_group_header, width=15, textvariable = txt_ticketplus_password_value, show="*")
    txt_ticketplus_password.grid(column=2, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_save_password_alert
    lbl_save_password_alert = Label(frame_group_header, fg="red", text=translate[language_code]['save_password_alert'])
    lbl_save_password_alert.grid(column=0, row=group_row_count, columnspan=2, sticky = E)

    frame_group_header.grid(column=0, row=row_count, padx=UI_PADDING_X)


def change_maxbot_status_by_keyword():
    config_filepath, config_dict = load_json()

    system_clock_data = datetime.now()
    current_time = system_clock_data.strftime('%H:%M:%S')
    #print('Current Time is:', current_time)
    if len(config_dict["advanced"]["idle_keyword"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["idle_keyword"], current_time)
        if is_matched:
            #print("match to idle:", current_time)
            do_maxbot_idle()
    if len(config_dict["advanced"]["resume_keyword"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["resume_keyword"], current_time)
        if is_matched:
            #print("match to resume:", current_time)
            do_maxbot_resume()
    
    current_time = system_clock_data.strftime('%S')
    if len(config_dict["advanced"]["idle_keyword_second"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["idle_keyword_second"], current_time)
        if is_matched:
            #print("match to idle:", current_time)
            do_maxbot_idle()
    if len(config_dict["advanced"]["resume_keyword_second"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["resume_keyword_second"], current_time)
        if is_matched:
            #print("match to resume:", current_time)
            do_maxbot_resume()

    check_maxbot_config_unsaved(config_dict)

def check_maxbot_config_unsaved(config_dict):
    # alert not saved config.
    global combo_homepage
    global combo_ticket_number

    global txt_date_keyword
    global txt_area_keyword
    global txt_keyword_exclude

    global txt_idle_keyword
    global txt_resume_keyword
    global txt_idle_keyword_second
    global txt_resume_keyword_second

    try:
        date_keyword = ""
        if 'txt_date_keyword' in globals():
            date_keyword = txt_date_keyword.get("1.0",END).strip()
            date_keyword = util.format_config_keyword_for_json(date_keyword)

        area_keyword = ""
        if 'txt_area_keyword' in globals():
            area_keyword = txt_area_keyword.get("1.0",END).strip()
            area_keyword = util.format_config_keyword_for_json(area_keyword)

        keyword_exclude = ""
        if 'txt_keyword_exclude' in globals():
            keyword_exclude = txt_keyword_exclude.get("1.0",END).strip()
            keyword_exclude = util.format_config_keyword_for_json(keyword_exclude)

        idle_keyword = ""
        if 'txt_idle_keyword' in globals():
            idle_keyword = txt_idle_keyword.get("1.0",END).strip()
            idle_keyword = util.format_config_keyword_for_json(idle_keyword)

        resume_keyword = ""
        if 'txt_resume_keyword' in globals():
            resume_keyword = txt_resume_keyword.get("1.0",END).strip()
            resume_keyword = util.format_config_keyword_for_json(resume_keyword)

        idle_keyword_second = ""
        if 'txt_idle_keyword_second' in globals():
            idle_keyword_second = txt_idle_keyword_second.get("1.0",END).strip()
            idle_keyword_second = util.format_config_keyword_for_json(idle_keyword_second)

        resume_keyword_second = ""
        if 'txt_resume_keyword_second' in globals():
            resume_keyword_second = txt_resume_keyword_second.get("1.0",END).strip()
            resume_keyword_second = util.format_config_keyword_for_json(resume_keyword_second)

        highlightthickness = 0
        if 'combo_homepage' in globals():
            if len(combo_homepage.get().strip())>0:
                if config_dict["homepage"] != combo_homepage.get().strip():
                    highlightthickness = 2
        
        if highlightthickness > 0:
            showHideBlocks()

        highlightthickness = 0
        if 'combo_ticket_number' in globals():
            if len(combo_ticket_number.get().strip())>0:
                if config_dict["ticket_number"] != int(combo_ticket_number.get().strip()):
                    highlightthickness = 2
        # fail, tkinter combobox border style is not working anymore
        #combo_ticket_number.config(highlightthickness=highlightthickness, highlightbackground="red")

        highlightthickness = 0
        if config_dict["date_auto_select"]["date_keyword"] != date_keyword:
            highlightthickness = 2
        txt_date_keyword.config(highlightthickness=highlightthickness, highlightbackground="red")

        highlightthickness = 0
        if config_dict["area_auto_select"]["area_keyword"] != area_keyword:
            highlightthickness = 2
        txt_area_keyword.config(highlightthickness=highlightthickness, highlightbackground="red")

        highlightthickness = 0
        if config_dict["keyword_exclude"] != keyword_exclude:
            highlightthickness = 2
        txt_keyword_exclude.config(highlightthickness=highlightthickness, highlightbackground="red")

        highlightthickness = 0
        if config_dict["advanced"]["idle_keyword"] != idle_keyword:
            highlightthickness = 2
        txt_idle_keyword.config(highlightthickness=highlightthickness, highlightbackground="red")

        highlightthickness = 0
        if config_dict["advanced"]["resume_keyword"] != resume_keyword:
            highlightthickness = 2
        txt_resume_keyword.config(highlightthickness=highlightthickness, highlightbackground="red")

        highlightthickness = 0
        if config_dict["advanced"]["idle_keyword_second"] != idle_keyword_second:
            highlightthickness = 2
        txt_idle_keyword_second.config(highlightthickness=highlightthickness, highlightbackground="red")

        highlightthickness = 0
        if config_dict["advanced"]["resume_keyword_second"] != resume_keyword_second:
            highlightthickness = 2
        txt_resume_keyword_second.config(highlightthickness=highlightthickness, highlightbackground="red")
    except Exception as exc:
        #print(exc)
        pass

def settgins_gui_timer():
    while True:
        btn_preview_text_clicked()
        preview_question_text_file()
        update_maxbot_runtime_status()
        change_maxbot_status_by_keyword()
        time.sleep(0.3)
        if GLOBAL_SERVER_SHUTDOWN:
            break

def clean_extension_status():
    Root_Dir = util.get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    target_path = os.path.join(webdriver_path, CONST_MAXBOT_EXTENSION_NAME)
    target_path = os.path.join(target_path, "data")
    target_path = os.path.join(target_path, CONST_MAXBOT_EXTENSION_STATUS_JSON)
    if os.path.exists(target_path):
        try:
            os.unlink(target_path)
        except Exception as exc:
            print(exc)
            pass

def sync_status_to_extension(status):
    Root_Dir = util.get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    target_path = os.path.join(webdriver_path, CONST_MAXBOT_EXTENSION_NAME)
    target_path = os.path.join(target_path, "data")
    if os.path.exists(target_path):
        target_path = os.path.join(target_path, CONST_MAXBOT_EXTENSION_STATUS_JSON)
        #print("save as to:", target_path)
        status_json={}
        status_json["status"]=status
        #print("dump json to path:", target_path)
        with open(target_path, 'w') as outfile:
            json.dump(status_json, outfile)

def update_maxbot_runtime_status():
    is_paused = False
    if os.path.exists(CONST_MAXBOT_INT28_FILE):
        is_paused = True

    sync_status_to_extension(not is_paused)

    global combo_language
    global lbl_maxbot_status_data
    try:
        language_code = ""
        if 'combo_language' in globals():
            new_language = combo_language.get().strip()
            language_code=get_language_code_by_name(new_language)

        if len(language_code) > 0:
            maxbot_status = translate[language_code]['status_enabled']
            if is_paused:
                maxbot_status = translate[language_code]['status_paused']

            if 'lbl_maxbot_status_data' in globals():
                lbl_maxbot_status_data.config(text=maxbot_status)

        global btn_idle
        global btn_resume

        if not is_paused:
            btn_idle.grid(column=1, row=0)
            btn_resume.grid_forget()
        else:
            btn_resume.grid(column=2, row=0)
            btn_idle.grid_forget()

        global lbl_maxbot_last_url_data
        last_url = read_last_url_from_file()
        if len(last_url) > 60:
            last_url=last_url[:60]+"..."
        if 'lbl_maxbot_last_url_data' in globals():
            lbl_maxbot_last_url_data.config(text=last_url)

        system_clock_data = datetime.now()
        current_time = system_clock_data.strftime('%H:%M:%S')
        #print('Current Time is:', current_time)
        
        global lbl_system_clock_data
        if 'lbl_system_clock_data' in globals():
            lbl_system_clock_data.config(text=current_time)

    except Exception as exc:
        #print(exc)
        pass


def RuntimeTab(root, config_dict, language_code, UI_PADDING_X):
    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    maxbot_status = ""
    global lbl_maxbot_status
    lbl_maxbot_status = Label(frame_group_header, text=translate[language_code]['running_status'])
    lbl_maxbot_status.grid(column=0, row=group_row_count, sticky = E)

    frame_maxbot_interrupt = Frame(frame_group_header)

    global lbl_maxbot_status_data
    lbl_maxbot_status_data = Label(frame_maxbot_interrupt, text=maxbot_status)
    lbl_maxbot_status_data.grid(column=0, row=group_row_count, sticky = W)

    global btn_idle
    global btn_resume

    btn_idle = ttk.Button(frame_maxbot_interrupt, text=translate[language_code]['idle'], command= lambda: btn_idle_clicked(language_code) )
    btn_idle.grid(column=1, row=0)

    btn_resume = ttk.Button(frame_maxbot_interrupt, text=translate[language_code]['resume'], command= lambda: btn_resume_clicked(language_code))
    btn_resume.grid(column=2, row=0)

    frame_maxbot_interrupt.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_maxbot_last_url
    lbl_maxbot_last_url = Label(frame_group_header, text=translate[language_code]['running_url'])
    lbl_maxbot_last_url.grid(column=0, row=group_row_count, sticky = E)

    last_url = ""
    global lbl_maxbot_last_url_data
    lbl_maxbot_last_url_data = Label(frame_group_header, text=last_url)
    lbl_maxbot_last_url_data.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_system_clock
    lbl_system_clock = Label(frame_group_header, text=translate[language_code]['system_clock'])
    lbl_system_clock.grid(column=0, row=group_row_count, sticky = E)

    system_clock = ""
    global lbl_system_clock_data
    lbl_system_clock_data = Label(frame_group_header, text=system_clock)
    lbl_system_clock_data.grid(column=1, row=group_row_count, sticky = W)

    group_row_count +=1

    global lbl_idle_keyword
    lbl_idle_keyword = Label(frame_group_header, text=translate[language_code]['idle_keyword'])
    lbl_idle_keyword.grid(column=0, row=group_row_count, sticky = E+N)

    global txt_idle_keyword
    txt_idle_keyword = Text(frame_group_header, width=30, height=4)
    txt_idle_keyword.grid(column=1, row=group_row_count, sticky = W)
    txt_idle_keyword.insert("1.0", config_dict["advanced"]["idle_keyword"].strip())

    group_row_count +=1

    global lbl_resume_keyword
    lbl_resume_keyword = Label(frame_group_header, text=translate[language_code]['resume_keyword'])
    lbl_resume_keyword.grid(column=0, row=group_row_count, sticky = E+N)

    global txt_resume_keyword
    txt_resume_keyword = Text(frame_group_header, width=30, height=4)
    txt_resume_keyword.grid(column=1, row=group_row_count, sticky = W)
    txt_resume_keyword.insert("1.0", config_dict["advanced"]["resume_keyword"].strip())

    group_row_count +=1

    global lbl_idle_keyword_second
    lbl_idle_keyword_second = Label(frame_group_header, text=translate[language_code]['idle_keyword_second'])
    lbl_idle_keyword_second.grid(column=0, row=group_row_count, sticky = E+N)

    global txt_idle_keyword_second
    txt_idle_keyword_second = Text(frame_group_header, width=30, height=4)
    txt_idle_keyword_second.grid(column=1, row=group_row_count, sticky = W)
    txt_idle_keyword_second.insert("1.0", config_dict["advanced"]["idle_keyword_second"].strip())

    group_row_count +=1

    global lbl_resume_keyword_second
    lbl_resume_keyword_second = Label(frame_group_header, text=translate[language_code]['resume_keyword_second'])
    lbl_resume_keyword_second.grid(column=0, row=group_row_count, sticky = E+N)

    global txt_resume_keyword_second
    txt_resume_keyword_second = Text(frame_group_header, width=30, height=4)
    txt_resume_keyword_second.grid(column=1, row=group_row_count, sticky = W)
    txt_resume_keyword_second.insert("1.0", config_dict["advanced"]["resume_keyword_second"].strip())

    frame_group_header.grid(column=0, row=row_count, padx=UI_PADDING_X)
    update_maxbot_runtime_status()


def AboutTab(root, language_code):
    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    logo_filename = "maxbot_logo2_single.ppm"
    logo_img = PhotoImage(file=logo_filename)

    lbl_logo = Label(frame_group_header, image=logo_img)
    lbl_logo.image = logo_img
    lbl_logo.grid(column=0, row=group_row_count, columnspan=2)

    group_row_count +=1

    global lbl_slogan
    global lbl_help
    global lbl_donate
    global lbl_release

    lbl_slogan = Label(frame_group_header, text=translate[language_code]['maxbot_slogan'], wraplength=400, justify="center")
    lbl_slogan.grid(column=0, row=group_row_count, columnspan=2)

    group_row_count +=1

    lbl_help = Label(frame_group_header, text=translate[language_code]['help'])
    lbl_help.grid(column=0, row=group_row_count, sticky = E)

    lbl_help_url = Label(frame_group_header, text=URL_HELP, fg="blue", bg="gray", cursor="hand2")
    lbl_help_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_help_url.bind("<Button-1>", lambda e: open_url(URL_HELP))

    group_row_count +=1

    lbl_donate = Label(frame_group_header, text=translate[language_code]['donate'])
    lbl_donate.grid(column=0, row=group_row_count, sticky = E)

    lbl_donate_url = Label(frame_group_header, text=URL_DONATE, fg="blue", bg="gray", cursor="hand2")
    lbl_donate_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_donate_url.bind("<Button-1>", lambda e: open_url(URL_DONATE))

    group_row_count +=1

    lbl_release = Label(frame_group_header, text=translate[language_code]['release'])
    lbl_release.grid(column=0, row=group_row_count, sticky = E)

    lbl_release_url = Label(frame_group_header, text=URL_RELEASE, fg="blue", bg="gray", cursor="hand2")
    lbl_release_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_release_url.bind("<Button-1>", lambda e: open_url(URL_RELEASE))

    group_row_count +=1

    lbl_fb_fans = Label(frame_group_header, text=u'Facebook')
    lbl_fb_fans.grid(column=0, row=group_row_count, sticky = E)

    lbl_fb_fans_url = Label(frame_group_header, text=URL_FB, fg="blue", bg="gray", cursor="hand2")
    lbl_fb_fans_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_fb_fans_url.bind("<Button-1>", lambda e: open_url(URL_FB))


    group_row_count +=1

    lbl_chrome_driver = Label(frame_group_header, text=u'Chrome Driver')
    lbl_chrome_driver.grid(column=0, row=group_row_count, sticky = E)

    lbl_chrome_driver_url = Label(frame_group_header, text=URL_CHROME_DRIVER, fg="blue", bg="gray", cursor="hand2")
    lbl_chrome_driver_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_chrome_driver_url.bind("<Button-1>", lambda e: open_url(URL_CHROME_DRIVER))

    group_row_count +=1

    lbl_firefox_driver = Label(frame_group_header, text=u'Firefox Driver')
    lbl_firefox_driver.grid(column=0, row=group_row_count, sticky = E)

    lbl_firefox_driver_url = Label(frame_group_header, text=URL_FIREFOX_DRIVER, fg="blue", bg="gray", cursor="hand2")
    lbl_firefox_driver_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_firefox_driver_url.bind("<Button-1>", lambda e: open_url(URL_FIREFOX_DRIVER))

    group_row_count +=1

    lbl_edge_driver = Label(frame_group_header, text=u'Edge Driver')
    lbl_edge_driver.grid(column=0, row=group_row_count, sticky = E)

    lbl_edge_driver_url = Label(frame_group_header, text=URL_EDGE_DRIVER, fg="blue", bg="gray", cursor="hand2")
    lbl_edge_driver_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_edge_driver_url.bind("<Button-1>", lambda e: open_url(URL_EDGE_DRIVER))

    frame_group_header.grid(column=0, row=row_count)

def get_action_bar(root, language_code):
    frame_action = Frame(root)

    global btn_run
    global btn_save
    global btn_exit
    global btn_restore_defaults
    global btn_launcher

    btn_run = ttk.Button(frame_action, text=translate[language_code]['run'], command= lambda: btn_run_clicked(language_code))
    btn_run.grid(column=0, row=0)

    btn_save = ttk.Button(frame_action, text=translate[language_code]['save'], command= lambda: btn_save_clicked() )
    btn_save.grid(column=1, row=0)

    btn_exit = ttk.Button(frame_action, text=translate[language_code]['exit'], command=btn_exit_clicked)
    #btn_exit.grid(column=2, row=0)

    btn_launcher = ttk.Button(frame_action, text=translate[language_code]['config_launcher'], command= lambda: btn_launcher_clicked(language_code))
    btn_launcher.grid(column=2, row=0)

    btn_restore_defaults = ttk.Button(frame_action, text=translate[language_code]['restore_defaults'], command= lambda: btn_restore_defaults_clicked(language_code))
    btn_restore_defaults.grid(column=3, row=0)

    return frame_action

def clearFrame(frame):
    # destroy all widgets from frame
    for widget in frame.winfo_children():
       widget.destroy()

def load_GUI(root, config_dict):
    clearFrame(root)

    language_code="en_us"
    if not config_dict is None:
        if u'language' in config_dict:
            language_code = get_language_code_by_name(config_dict["language"])

    row_count = 0

    global tabControl
    tabControl = ttk.Notebook(root)
    tab1 = Frame(tabControl)
    tabControl.add(tab1, text=translate[language_code]['preference'])

    tab2 = Frame(tabControl)
    tabControl.add(tab2, text=translate[language_code]['advanced'])

    tab3 = Frame(tabControl)
    tabControl.add(tab3, text=translate[language_code]['verification_word'])

    global tab4
    tab4 = Frame(tabControl)
    tabControl.add(tab4, text=translate[language_code]['maxbot_server'])

    tab5 = Frame(tabControl)
    tabControl.add(tab5, text=translate[language_code]['autofill'])

    tab6 = Frame(tabControl)
    tabControl.add(tab6, text=translate[language_code]['runtime'])

    tab7 = Frame(tabControl)
    tabControl.add(tab7, text=translate[language_code]['about'])

    tabControl.grid(column=0, row=row_count)
    tabControl.select(tab1)

    row_count+=1

    frame_action = get_action_bar(root, language_code)
    frame_action.grid(column=0, row=row_count)

    global UI_PADDING_X
    PreferenctTab(tab1, config_dict, language_code, UI_PADDING_X)
    AdvancedTab(tab2, config_dict, language_code, UI_PADDING_X)
    VerificationTab(tab3, config_dict, language_code, UI_PADDING_X)
    ServerTab(tab4, config_dict, language_code, UI_PADDING_X)
    AutofillTab(tab5, config_dict, language_code, UI_PADDING_X)
    RuntimeTab(tab6, config_dict, language_code, UI_PADDING_X)
    AboutTab(tab7, language_code)

def main_gui():
    global translate
    translate = load_translate()

    global config_filepath
    global config_dict
    config_filepath, config_dict = load_json()

    global root
    root = Tk()
    #root = customtkinter.CTk()
    root.title(CONST_APP_VERSION)

    global UI_PADDING_X
    UI_PADDING_X = 15

    load_GUI(root, config_dict)

    GUI_SIZE_WIDTH = 590
    GUI_SIZE_HEIGHT = 645

    GUI_SIZE_MACOS = str(GUI_SIZE_WIDTH) + 'x' + str(GUI_SIZE_HEIGHT)
    GUI_SIZE_WINDOWS=str(GUI_SIZE_WIDTH-70) + 'x' + str(GUI_SIZE_HEIGHT-80)
    GUI_SIZE_LINUX=str(GUI_SIZE_WIDTH-50) + 'x' + str(GUI_SIZE_HEIGHT-140)

    GUI_SIZE =GUI_SIZE_MACOS
    if platform.system() == 'Windows':
        GUI_SIZE = GUI_SIZE_WINDOWS
    if platform.system() == 'Linux':
        GUI_SIZE = GUI_SIZE_LINUX

    root.geometry(GUI_SIZE)

    # icon format.
    iconImg = 'AAABAAEAAAAAAAEAIAD4MgAAFgAAAIlQTkcNChoKAAAADUlIRFIAAAEAAAABAAgGAAAAXHKoZgAAAAFzUkdCAK7OHOkAAABQZVhJZk1NACoAAAAIAAIBEgADAAAAAQABAACHaQAEAAAAAQAAACYAAAAAAAOgAQADAAAAAQABAACgAgAEAAAAAQAAAQCgAwAEAAAAAQAAAQAAAAAAdTc0VwAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KTMInWQAAMPFJREFUeAHtndmTJNd13rP36e7pWXt6OFiHGAxACssApChTskRZom1J3ETS9ov/AIclO/Tm8JMj/OxQBMNhO0IRdvjNtB0SSYirTFEiJZoSTBAidoAAZjCYAYazb73M9O7vdzKzOqu6qmvLyr5VeW5MT3VXVea997s3v3vOueecO/SlmYnNyIsj4AiUEoHhUvbaO+0IOAKGgBOATwRHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECIzuWt83N3et6oGpeGioflf6FFtmhPWoUb/q9zafd4VZpf587ljIXSpt7hCz4glADR0ZH49GJiai4dHRaGh4JErbbvOW/2wweAVD+68QMPupks2NzWhlfj7a3FivavbQ8HA0PjMjXPtRuBuK1u7eidbu3KnqUxF/jAmzkbFxVdVv820o2lhbjVYWFuy5aRer4glALYQAJg/PRlNzc9H00Q/o9aj9znt7Dh6MJvbtj8amp6ORPXs0KGPR0MiIloYhWx02Y5aAI+IO2y/tdru/v8/DffPM6eh7f/D70Z1r1wRNLAlsbmxEhz704eiTX/pP0fi+fR1NiN1EhnF+/X99OfrJl/6wMAJjPk3NHok++R//c3TgoRMi1I3dhKDtusHswt/+KPrBv/030cbqStvXF08AAnzl9u1oWT9MYiYvnRgeHYtG90zYgz8+s09EcCianD0cTR2Zi6ZEEtMpSRw5Ek3qs4n9B6KxvXuj0clJkyTa7nmfXzD/3nvRqlg/ffjpDpN37tRT0T2//CuFPUB5w3jw5MlC2765vh7d92ufiD7425+yhSnv/hRxv6uvvhJtSgropBRPALQyWc3TBjMI6/xI/Lt784Zmsj4RUcSrPd/XP6kKqAwj4yKJqSkTcycOHIgmDx2OJkUK00clRSREwd+8z+eQydjUpF1nkkRaaZ+/XnnpBROVs33i96NPfaTQByhvGMen91r7i1qJmUuPfPGf9u3DD/4LF96PNvT8dKL27Q4BNJo1Rgw87fEXkpfK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'
    if platform.system() == 'Linux':
        iconImg = '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'

    icon_filepath = 'tmp.ico'
    tmpIcon = open(icon_filepath, 'wb+')
    tmpIcon.write(base64.b64decode(iconImg))
    tmpIcon.close()
    if platform.system() == 'Windows':
        root.iconbitmap(icon_filepath)
    if platform.system() == 'Darwin':
        #from PIL import Image, ImageTk
        #logo = ImageTk.PhotoImage(Image.open(icon_filepath).convert('RGB'))
        #root.call('wm', 'iconphoto', root._w, logo)
        pass
    if platform.system() == 'Linux':
        logo = PhotoImage(file=icon_filepath)
        root.call('wm', 'iconphoto', root._w, logo)
    os.remove(icon_filepath)

    root.mainloop()
    GLOBAL_SERVER_SHUTDOWN=True
    clean_extension_status()

def clean_tmp_file():
    remove_file_list = [CONST_MAXBOT_LAST_URL_FILE
        ,CONST_MAXBOT_INT28_FILE
        ,CONST_MAXBOT_ANSWER_ONLINE_FILE
        ,CONST_MAXBOT_QUESTION_FILE
    ]
    for filepath in remove_file_list:
         util.force_remove_file(filepath)

def btn_copy_ip_clicked():
    local_ip = util.get_ip_address()
    ip_address = "http://%s:%d/" % (local_ip,CONST_SERVER_PORT)
    pyperclip.copy(ip_address)

def btn_copy_question_clicked():
    global txt_question
    question_text = txt_question.get("1.0",END).strip()
    if len(question_text) > 0:
        pyperclip.copy(question_text)

def btn_query_question_clicked():
    global txt_question
    question_text = txt_question.get("1.0",END).strip()
    if len(question_text) > 0:
        webbrowser.open("https://www.google.com/search?q="+question_text)

class MainHandler(tornado.web.RequestHandler):
    def format_config_keyword_for_json(self, user_input):
        if len(user_input) > 0:
            if not ('\"' in user_input):
                user_input = '"' + user_input + '"'
        return user_input

    def compose_as_json(self, user_input):
        user_input = self.format_config_keyword_for_json(user_input)
        return "{\"data\":[%s]}" % user_input

    def get(self):
        global txt_answer_value
        answer_text = ""
        try:
            answer_text = txt_answer_value.get().strip()
        except Exception as exc:
            pass
        answer_text_output = self.compose_as_json(answer_text)
        #print("answer_text_output:", answer_text_output)
        self.write(answer_text_output)

class QuestionHandler(tornado.web.RequestHandler):
    def get(self):
        global txt_question
        txt_question.insert("1.0", "")

class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"version":self.application.version})

class OcrHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"answer": "1234"})

    def post(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

        _body = None
        is_pass_check = True
        errorMessage = ""
        errorCode = 0

        if is_pass_check:
            is_pass_check = False
            try :
                _body = json.loads(self.request.body)
                is_pass_check = True
            except Exception:
                errorMessage = "wrong json format"
                errorCode = 1001
                pass

        img_base64 = None
        image_data = ""
        if is_pass_check:
            if 'image_data' in _body:
                image_data = _body['image_data']
                if len(image_data) > 0:
                    img_base64 = base64.b64decode(image_data)
            else:
                errorMessage = "image_data not exist"
                errorCode = 1002

        #print("is_pass_check:", is_pass_check)
        #print("errorMessage:", errorMessage)
        #print("errorCode:", errorCode)
        ocr_answer = ""
        if not img_base64 is None:
            try:
                ocr_answer = self.application.ocr.classification(img_base64)
                print("ocr_answer:", ocr_answer)
            except Exception as exc:
                pass

        self.write({"answer": ocr_answer})

async def main_server():
    ocr = None
    try:
        ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
    except Exception as exc:
        print(exc)
        pass

    app = Application([
        ("/", MainHandler),
        ("/version", VersionHandler),
        ("/ocr", OcrHandler),
        ("/query", MainHandler),
        ("/question", QuestionHandler),
    ])
    app.ocr = ocr;
    app.version = CONST_APP_VERSION;

    app.listen(CONST_SERVER_PORT)
    print("server running on port:", CONST_SERVER_PORT)
    await asyncio.Event().wait()


def web_server():
    is_port_binded = util.is_connectable(CONST_SERVER_PORT)
    #print("is_port_binded:", is_port_binded)
    if not is_port_binded:
        asyncio.run(main_server())
    else:
        print("port:", CONST_SERVER_PORT, " is in used.")

def preview_question_text_file():
    if os.path.exists(CONST_MAXBOT_QUESTION_FILE):
        infile = None
        if platform.system() == 'Windows':
            infile = open(CONST_MAXBOT_QUESTION_FILE, 'r', encoding='UTF-8')
        else:
            infile = open(CONST_MAXBOT_QUESTION_FILE, 'r')

        if not infile is None:
            question_text = infile.readline()

            global txt_question
            if 'txt_question' in globals():
                try:
                    displayed_question_text = txt_question.get("1.0",END).strip()
                    if displayed_question_text != question_text:
                        # start to refresh
                        txt_question.delete("1.0","end")
                        if len(question_text) > 0:
                            txt_question.insert("1.0", question_text)
                except Exception as exc:
                    pass

if __name__ == "__main__":
    threading.Thread(target=settgins_gui_timer, daemon=True).start()
    threading.Thread(target=web_server, daemon=True).start()
    clean_tmp_file()
    main_gui()
