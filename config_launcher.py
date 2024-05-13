#!/usr/bin/env python
#encoding=utf-8

try:
    # for Python2
    import tkMessageBox as messagebox
    import ttk
    from Tkinter import *
except ImportError:
    # for Python3
    try:
        from tkinter import *
        from tkinter import filedialog, messagebox, ttk
    except Exception as e:
        pass

import base64
import json
import os
import platform
import sys
import threading
import webbrowser

import util

CONST_APP_VERSION = "MaxBot (2024.04.18)"

CONST_MAXBOT_LAUNCHER_FILE = "config_launcher.json"
CONST_MAXBOT_CONFIG_FILE = "settings.json"

translate={}

URL_DONATE = 'https://max-everyday.com/about/#donate'
URL_HELP = 'https://max-everyday.com/2018/08/max-auto-reg-bot/'
URL_RELEASE = 'https://github.com/max32002/joint_bot/releases'
URL_FB = 'https://www.facebook.com/maxbot.ticket'
URL_CHROME_DRIVER = 'https://chromedriver.chromium.org/'
URL_FIREFOX_DRIVER = 'https://github.com/mozilla/geckodriver/releases'
URL_EDGE_DRIVER = 'https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/'

def load_translate():
    translate = {
        'en_us': {
            "language": 'Language',
            "enable": 'Enable',
            "config_list": 'Config List',
            "advanced": 'Advanced',
            "about": 'About',
            "run": 'Run',
            "browse": 'Browse...',
            "save": 'Save',
            "exit": 'Close',
            "copy": 'Copy',
            "restore_defaults": 'Restore Defaults',
            "done": 'Done',
            "maxbot_slogan": 'MaxRegBot is a FREE and open source bot program. Wish you good luck.',
            "donate": 'Donate',
            "help": 'Help',
            "release": 'Release'
        },
        'zh_tw': {
            "language": '語言',
            "enable": '啟用',
            "config_list": '設定檔管理',
            "advanced": '進階設定',
            "autofill": '自動填表單',
            "about": '關於',
            "run": '搶票',
            "browse": '開啟...',
            "save": '存檔',
            "exit": '關閉',
            "copy": '複製',
            "restore_defaults": '恢復預設值',
            "done": '完成',
            "maxbot_slogan": 'MaxRegBot是一個免費、開放原始碼的搶票機器人。\n祝您掛號成功。',
            "donate": '打賞',
            "release": '所有可用版本',
            "help": '使用教學'
        },
        'zh_cn': {
            "language": '语言',
            "enable": '启用',
            "config_list": '设定档管理',
            "advanced": '進階設定',
            "autofill": '自动填表单',
            "about": '关于',
            "run": '抢票',
            "browse": '开启...',
            "save": '存档',
            "exit": '关闭',
            "copy": '复制',
            "restore_defaults": '恢复默认值',
            "done": '完成',
            "maxbot_slogan": 'MaxRegBot 是一个免费的开源机器人程序。\n祝您挂号成功。',
            "donate": '打赏',
            "help": '使用教学',
            "release": '所有可用版本'
        },
        'ja_jp': {
            "language": '言語',
            "enable": '有効',
            "config_list": 'Config List',
            "advanced": '高度な設定',
            "autofill": 'オートフィル',
            "about": '情報',
            "run": 'チケットを取る',
            "browse": '開ける...',
            "save": '保存',
            "exit": '閉じる',
            "copy": 'コピー',
            "restore_defaults": 'デフォルトに戻す',
            "done": '終わり',
            "maxbot_slogan": 'MaxRegBot は無料のオープン ソース ボット プログラムです。チケットの成功をお祈りします。',
            "donate": '寄付',
            "help": '利用方法',
            "release": 'リリース'
        }
    }
    return translate

def get_default_config():
    config_dict={}

    config_dict["list"] = [CONST_MAXBOT_CONFIG_FILE]

    config_dict["advanced"] = {}
    config_dict["advanced"]["language"] = "English"

    return config_dict

def load_json():
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_LAUNCHER_FILE)

    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
    else:
        config_dict = get_default_config()
    return config_filepath, config_dict

def btn_restore_defaults_clicked(language_code):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_LAUNCHER_FILE)
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

def btn_save_clicked():
    btn_save_act()

def btn_save_act(slience_mode=True):
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_LAUNCHER_FILE)

    config_dict = get_default_config()
    language_code = get_language_code_by_name(config_dict["advanced"]["language"])

    config_dict["advanced"]["language"] = combo_language.get().strip()
    language_code = get_language_code_by_name(config_dict["advanced"]["language"])

    filelist = [txt_file_name[i].get().strip() for i in range(15)]
    config_dict["list"] = filelist

    util.save_json(config_dict, config_filepath)
    
    if not slience_mode:
        messagebox.showinfo(translate[language_code]["save"], translate[language_code]["done"])

    return True

def open_url(url):
    webbrowser.open_new(url)

def btn_exit_clicked():
    root.destroy()

def btn_donate_clicked():
    open_url.open(URL_DONATE)

def btn_help_clicked():
    open_url.open(URL_HELP)

def callbackLanguageOnChange(event):
    applyNewLanguage()

def get_language_code_by_name(new_language):
    language_code = "en_us"
    if '繁體中文' in new_language:
        language_code = 'zh_tw'
    if '簡体中文' in new_language:
        language_code = 'zh_cn'
    if '日本語' in new_language:
        language_code = 'ja_jp'
    return language_code

def applyNewLanguage():
    global combo_language
    new_language = combo_language.get().strip()
    #print("new language value:", new_language)

    language_code=get_language_code_by_name(new_language)

    global lbl_language

    lbl_language.config(text=translate[language_code]["language"])

    global tabControl

    tabControl.tab(0, text=translate[language_code]["config_list"])
    tabControl.tab(1, text=translate[language_code]["advanced"])
    tabControl.tab(2, text=translate[language_code]["about"])

    global lbl_slogan
    global lbl_help
    global lbl_donate
    global lbl_release

    lbl_slogan.config(text=translate[language_code]["maxbot_slogan"])
    lbl_help.config(text=translate[language_code]["help"])
    lbl_donate.config(text=translate[language_code]["donate"])
    lbl_release.config(text=translate[language_code]["release"])

    global btn_browse
    for i in range(15):
        btn_browse[i].config(text=translate[language_code]['browse'] + " " + str(i+1))

    global btn_run
    for i in range(15):
        btn_run[i].config(text=translate[language_code]['run'] + " " + str(i+1))

    global btn_save
    global btn_restore_defaults

    btn_save.config(text=translate[language_code]["save"])
    btn_restore_defaults.config(text=translate[language_code]["restore_defaults"])

def btn_items_browse_event(event):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    btn_index = int(str(event.widget['text']).split(" ")[1])

    global widgets
    if "widgets" in globals():
        file_path = filedialog.askopenfilename(initialdir=working_dir, defaultextension=".json",filetypes=[("json Documents","*.json"),("All Files","*.*")])
        if not file_path is None:
            display_path = file_path
            if len(file_path) > len(working_dir):
                if file_path[:len(working_dir)]==working_dir:
                    display_path = file_path[len(working_dir)+1:]
            #print("json file path:", file_path)
            widgets['txt_file_name_value'][btn_index-1].set(display_path)
            #print("new json file path:", txt_file_name[btn_index-1].get().strip())

def btn_items_run_event(event):
    btn_index = int(str(event.widget['text']).split(" ")[1])

    global widgets
    if "widgets" in globals():
        filename=widgets['txt_file_name_value'][btn_index-1].get().strip()
        script_name = "chrome_tixcraft"
        threading.Thread(target=util.launch_maxbot, args=(script_name,filename,)).start()

def ConfigListTab(root, config_dict, language_code, UI_PADDING_X):
    frame_group_header = Frame(root)
    widgets = {
        'lbl_file_name': {},
        'txt_file_name': {},
        'txt_file_name_value': {},
        'btn_browse': {},
        'btn_run': {},
    }

    for i, filename in enumerate(config_dict["list"][:15]):
        widgets['lbl_file_name'][i] = Label(frame_group_header, text=str(i+1))
        widgets['lbl_file_name'][i].grid(column=0, row=i, sticky=E)

        widgets['txt_file_name_value'][i] = StringVar(frame_group_header, value=filename)
        widgets['txt_file_name'][i] = Entry(frame_group_header, width=20, textvariable=widgets['txt_file_name_value'][i])
        widgets['txt_file_name'][i].grid(column=1, row=i, sticky=W)

        widgets['btn_browse'][i] = ttk.Button(frame_group_header, text=translate[language_code]['browse'] + " " + str(i+1))
        widgets['btn_browse'][i].grid(column=2, row=i, sticky=W)
        widgets['btn_browse'][i].bind('<Button-1>', btn_items_browse_event)

        widgets['btn_run'][i] = ttk.Button(frame_group_header, text=translate[language_code]['run'] + " " + str(i+1))
        widgets['btn_run'][i].grid(column=3, row=i, sticky=W)
        widgets['btn_run'][i].bind('<Button-1>', btn_items_run_event)

    frame_group_header.grid(column=0, row=0, sticky=W, padx=UI_PADDING_X)
    return widgets


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

    lbl_help_url = Label(frame_group_header, text=URL_HELP, fg="blue", cursor="hand2")
    lbl_help_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_help_url.bind("<Button-1>", lambda e: open_url(URL_HELP))

    group_row_count +=1

    lbl_donate = Label(frame_group_header, text=translate[language_code]['donate'])
    lbl_donate.grid(column=0, row=group_row_count, sticky = E)

    lbl_donate_url = Label(frame_group_header, text=URL_DONATE, fg="blue", cursor="hand2")
    lbl_donate_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_donate_url.bind("<Button-1>", lambda e: open_url(URL_DONATE))

    group_row_count +=1

    lbl_release = Label(frame_group_header, text=translate[language_code]['release'])
    lbl_release.grid(column=0, row=group_row_count, sticky = E)

    lbl_release_url = Label(frame_group_header, text=URL_RELEASE, fg="blue", cursor="hand2")
    lbl_release_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_release_url.bind("<Button-1>", lambda e: open_url(URL_RELEASE))

    group_row_count +=1

    lbl_fb_fans = Label(frame_group_header, text=u'Facebook')
    lbl_fb_fans.grid(column=0, row=group_row_count, sticky = E)

    lbl_fb_fans_url = Label(frame_group_header, text=URL_FB, fg="blue", cursor="hand2")
    lbl_fb_fans_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_fb_fans_url.bind("<Button-1>", lambda e: open_url(URL_FB))


    group_row_count +=1

    lbl_chrome_driver = Label(frame_group_header, text=u'Chrome Driver')
    lbl_chrome_driver.grid(column=0, row=group_row_count, sticky = E)

    lbl_chrome_driver_url = Label(frame_group_header, text=URL_CHROME_DRIVER, fg="blue", cursor="hand2")
    lbl_chrome_driver_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_chrome_driver_url.bind("<Button-1>", lambda e: open_url(URL_CHROME_DRIVER))

    group_row_count +=1

    lbl_firefox_driver = Label(frame_group_header, text=u'Firefox Driver')
    lbl_firefox_driver.grid(column=0, row=group_row_count, sticky = E)

    lbl_firefox_driver_url = Label(frame_group_header, text=URL_FIREFOX_DRIVER, fg="blue", cursor="hand2")
    lbl_firefox_driver_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_firefox_driver_url.bind("<Button-1>", lambda e: open_url(URL_FIREFOX_DRIVER))

    group_row_count +=1

    lbl_edge_driver = Label(frame_group_header, text=u'Edge Driver')
    lbl_edge_driver.grid(column=0, row=group_row_count, sticky = E)

    lbl_edge_driver_url = Label(frame_group_header, text=URL_EDGE_DRIVER, fg="blue", cursor="hand2")
    lbl_edge_driver_url.grid(column=1, row=group_row_count, sticky = W)
    lbl_edge_driver_url.bind("<Button-1>", lambda e: open_url(URL_EDGE_DRIVER))

    frame_group_header.grid(column=0, row=row_count)

def AdvancedTab(root, config_dict, language_code, UI_PADDING_X):
    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    # for kktix
    print("==[advanced]==")
    print(config_dict["advanced"])

    global lbl_language
    lbl_language = Label(frame_group_header, text=translate[language_code]['language'])
    lbl_language.grid(column=0, row=group_row_count, sticky = E)

    global combo_language
    combo_language = ttk.Combobox(frame_group_header, state="readonly")
    combo_language['values']= ("English","繁體中文","簡体中文","日本語")
    combo_language.set(config_dict["advanced"]['language'])
    combo_language.bind("<<ComboboxSelected>>", callbackLanguageOnChange)
    combo_language.grid(column=1, row=group_row_count, sticky = W)

    frame_group_header.grid(column=0, row=row_count, padx=UI_PADDING_X)


def get_action_bar(root, language_code):
    frame_action = Frame(root)

    global btn_save
    global btn_restore_defaults

    btn_save = ttk.Button(frame_action, text=translate[language_code]['save'], command= lambda: btn_save_clicked() )
    btn_save.grid(column=1, row=0)

    btn_restore_defaults = ttk.Button(frame_action, text=translate[language_code]['restore_defaults'], command= lambda: btn_restore_defaults_clicked(language_code))
    btn_restore_defaults.grid(column=2, row=0)

    return frame_action

def clearFrame(frame):
    # destroy all widgets from frame
    for widget in frame.winfo_children():
       widget.destroy()

def load_GUI(root, config_dict):
    clearFrame(root)

    #language_code="en_us"
    language_code = get_language_code_by_name(config_dict["advanced"]["language"])

    row_count = 0

    global tabControl
    tabControl = ttk.Notebook(root)
    tab1 = Frame(tabControl)
    tabControl.add(tab1, text=translate[language_code]['config_list'])

    tab2 = Frame(tabControl)
    tabControl.add(tab2, text=translate[language_code]['advanced'])

    tab3 = Frame(tabControl)
    tabControl.add(tab3, text=translate[language_code]['about'])
    tabControl.grid(column=0, row=row_count)
    tabControl.select(tab1)

    row_count+=1

    frame_action = get_action_bar(root, language_code)
    frame_action.grid(column=0, row=row_count)

    global UI_PADDING_X
    widgets = ConfigListTab(tab1, config_dict, language_code, UI_PADDING_X)
    AdvancedTab(tab2, config_dict, language_code, UI_PADDING_X)
    AboutTab(tab3, language_code)
    return widgets

def main_gui():
    global translate
    # only need to load translate once.
    translate = load_translate()

    global config_filepath
    global config_dict
    # only need to load json file once.
    config_filepath, config_dict = load_json()

    global root
    root = Tk()
    root.title(CONST_APP_VERSION)

    global UI_PADDING_X
    UI_PADDING_X = 15

    global widgets
    widgets = load_GUI(root, config_dict)

    GUI_SIZE_WIDTH = 580
    GUI_SIZE_HEIGHT = 580

    GUI_SIZE_MACOS = str(GUI_SIZE_WIDTH) + 'x' + str(GUI_SIZE_HEIGHT)
    GUI_SIZE_WINDOWS=str(GUI_SIZE_WIDTH-60) + 'x' + str(GUI_SIZE_HEIGHT-55)

    GUI_SIZE =GUI_SIZE_MACOS

    if platform.system() == 'Windows':
        GUI_SIZE = GUI_SIZE_WINDOWS

    root.geometry(GUI_SIZE)

    # for icon.
    icon_filepath = 'tmp.ico'

    # icon format.
    iconImg = 'AAABAAEAAAAAAAEAIAD4MgAAFgAAAIlQTkcNChoKAAAADUlIRFIAAAEAAAABAAgGAAAAXHKoZgAAAAFzUkdCAK7OHOkAAABQZVhJZk1NACoAAAAIAAIBEgADAAAAAQABAACHaQAEAAAAAQAAACYAAAAAAAOgAQADAAAAAQABAACgAgAEAAAAAQAAAQCgAwAEAAAAAQAAAQAAAAAAdTc0VwAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KTMInWQAAMPFJREFUeAHtndmTJNd13rP36e7pWXt6OFiHGAxACssApChTskRZom1J3ETS9ov/AIclO/Tm8JMj/OxQBMNhO0IRdvjNtB0SSYirTFEiJZoSTBAidoAAZjCYAYazb73M9O7vdzKzOqu6qmvLyr5VeW5MT3VXVea997s3v3vOueecO/SlmYnNyIsj4AiUEoHhUvbaO+0IOAKGgBOATwRHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECDgBlHjwveuOgBOAzwFHoMQIOAGUePC9646AE4DPAUegxAg4AZR48L3rjoATgM8BR6DECIzuWt83N3et6oGpeGioflf6FFtmhPWoUb/q9zafd4VZpf587ljIXSpt7hCz4glADR0ZH49GJiai4dHRaGh4JErbbvOW/2wweAVD+68QMPupks2NzWhlfj7a3FivavbQ8HA0PjMjXPtRuBuK1u7eidbu3KnqUxF/jAmzkbFxVdVv820o2lhbjVYWFuy5aRer4glALYQAJg/PRlNzc9H00Q/o9aj9znt7Dh6MJvbtj8amp6ORPXs0KGPR0MiIloYhWx02Y5aAI+IO2y/tdru/v8/DffPM6eh7f/D70Z1r1wRNLAlsbmxEhz704eiTX/pP0fi+fR1NiN1EhnF+/X99OfrJl/6wMAJjPk3NHok++R//c3TgoRMi1I3dhKDtusHswt/+KPrBv/030cbqStvXF08AAnzl9u1oWT9MYiYvnRgeHYtG90zYgz8+s09EcCianD0cTR2Zi6ZEEtMpSRw5Ek3qs4n9B6KxvXuj0clJkyTa7nmfXzD/3nvRqlg/ffjpDpN37tRT0T2//CuFPUB5w3jw5MlC2765vh7d92ufiD7425+yhSnv/hRxv6uvvhJtSgropBRPALQyWc3TBjMI6/xI/Lt784Zmsj4RUcSrPd/XP6kKqAwj4yKJqSkTcycOHIgmDx2OJkUK00clRSREwd+8z+eQydjUpF1nkkRaaZ+/XnnpBROVs33i96NPfaTQByhvGMen91r7i1qJmUuPfPGf9u3DD/4LF96PNvT8dKL27Q4BNJo1Rgw87fEXkpfK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'
    if platform.system() == 'Linux':
        # PNG format.
        iconImg = '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'

    tmpIcon = open(icon_filepath, 'wb+')
    tmpIcon.write(base64.b64decode(iconImg))
    tmpIcon.close()
    if platform.system() == 'Windows':
        root.iconbitmap(icon_filepath)
    if platform.system() == 'Linux':
        logo = PhotoImage(file=icon_filepath)
        root.call('wm', 'iconphoto', root._w, logo)
    os.remove(icon_filepath)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
