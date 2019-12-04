#!/usr/bin/env python
#encoding=utf-8

try:
    # for Python2
    from Tkinter import *
    import ttk
    import tkMessageBox as messagebox
except ImportError:
    # for Python3
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox

import os
import sys
import json

CONST_APP_VERSION = u"MaxBot (2019.12.04)"

CONST_FROM_TOP_TO_BOTTOM = u"from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = u"from bottom to top"
CONST_RANDOM = u"random"
CONST_SELECT_ORDER_DEFAULT = CONST_FROM_TOP_TO_BOTTOM
CONST_SELECT_OPTIONS_DEFAULT = (CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_RANDOM)
CONST_SELECT_OPTIONS_ARRAY = [CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_RANDOM]

config_filepath = None
config_dict = None

window = None

btn_save = None
btn_exit = None

def load_json():
    # 讀取檔案裡的參數值
    basis = ""
    if hasattr(sys, 'frozen'):
        basis = sys.executable
    else:
        basis = sys.argv[0]
    app_root = os.path.dirname(basis)

    global config_filepath
    config_filepath = os.path.join(app_root, 'settings.json')

    global config_dict
    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)

def btn_save_clicked():
    btn_save_act()

def btn_save_act(slience_mode=False):

    is_all_data_correct = True

    global config_filepath

    global config_dict
    if not config_dict is None:
        # read user input

        global combo_homepage
        global combo_browser
        global txt_ticket_number
        #global txt_facebook_account
    
        global chk_state_auto_press_next_step_button
        global chk_state_auto_fill_ticket_number
        global txt_kktix_area_keyword
        global txt_kktix_answer_dictionary

        global chk_state_date_auto_select
        global txt_date_keyword
        global chk_state_area_auto_select
        global txt_area_keyword_1
        global txt_area_keyword_2

        global combo_date_auto_select_mode
        global combo_area_auto_select_mode

        if is_all_data_correct:
            if combo_homepage.get().strip()=="":
                is_all_data_correct = False
                messagebox.showerror("Error", "Please enter homepage")
            else:
                config_dict["homepage"] = combo_homepage.get().strip()

        if is_all_data_correct:
            if combo_browser.get().strip()=="":
                is_all_data_correct = False
                messagebox.showerror("Error", "Please enter browser: chrome or firefox")
            else:
                config_dict["browser"] = combo_browser.get().strip()

        if is_all_data_correct:
            if txt_ticket_number.get().strip()=="":
                is_all_data_correct = False
                messagebox.showerror("Error", "Please enter text")
            else:
                config_dict["ticket_number"] = int(txt_ticket_number.get().strip())

        if is_all_data_correct:
            #config_dict["facebook_account"] = txt_facebook_account.get().strip()
            pass

        if is_all_data_correct:
            config_dict["kktix"]["auto_press_next_step_button"] = bool(chk_state_auto_press_next_step_button.get())
            config_dict["kktix"]["auto_fill_ticket_number"] = bool(chk_state_auto_fill_ticket_number.get())
            config_dict["kktix"]["area_mode"] = combo_kktix_area_mode.get().strip()
            config_dict["kktix"]["area_keyword"] = txt_kktix_area_keyword.get().strip()
            config_dict["kktix"]["answer_dictionary"] = txt_kktix_answer_dictionary.get().strip()

            config_dict["tixcraft"]["date_auto_select"]["enable"] = bool(chk_state_date_auto_select.get())
            config_dict["tixcraft"]["date_auto_select"]["date_keyword"] = txt_date_keyword.get().strip()

            config_dict["tixcraft"]["area_auto_select"]["enable"] = bool(chk_state_area_auto_select.get())
            config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"] = txt_area_keyword_1.get().strip()
            config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"] = txt_area_keyword_2.get().strip()

            config_dict["tixcraft"]["date_auto_select"]["mode"] = combo_date_auto_select_mode.get().strip()
            config_dict["tixcraft"]["area_auto_select"]["mode"] = combo_area_auto_select_mode.get().strip()

        # save config.
        if is_all_data_correct:
            import json
            with open(config_filepath, 'w') as outfile:
                json.dump(config_dict, outfile)

            if slience_mode==False:
                messagebox.showinfo("File Save", "Done ^_^")

    return is_all_data_correct

def btn_run_clicked():
    if btn_save_act(slience_mode=True):
        import subprocess
        if hasattr(sys, 'frozen'):
            import platform

            # check platform here.
            # for windows.
            if platform.system() == 'Darwin':
                 subprocess.Popen("./chrome_tixcraft", shell=True)
            if platform.system() == 'Windows':
                subprocess.Popen("chrome_tixcraft.exe", shell=True)
        else:
            subprocess.Popen("python chrome_tixcraft.py", shell=True)


def btn_exit_clicked():
    root.destroy()

def callbackHomepageOnChange(event):
    showHideBlocks()

def callbackDateAutoOnChange():
    showHideTixcraftBlocks()

def showHideBlocks(all_layout_visible=False):
    global UI_PADDING_X

    global frame_group_kktix
    global frame_group_kktix_index
    global frame_group_tixcraft
    global frame_group_tixcraft_index

    # for kktix only.
    global lbl_kktix_area_mode
    global lbl_kktix_answer_dictionary

    global txt_kktix_answer_dictionary
    global txt_kktix_answer_dictionary_index

    global combo_kktix_area_mode
    global combo_kktix_area_mode_index

    new_homepage = combo_homepage.get().strip()
    #print("new homepage value:", new_homepage)

    show_block_index = 0
    if u'tixcraft' in new_homepage:
        show_block_index = 1
    if u'famiticket' in new_homepage:
        show_block_index = 1

    # all_layout_visible==true, means enter function when onload().
    #print("all_layout_visible:", all_layout_visible)
    if all_layout_visible:
        if show_block_index==0:
            frame_group_tixcraft.grid_forget()

            if u'kktix' in new_homepage:
                #combo_kktix_area_mode.grid(column=1, row=combo_kktix_area_mode_index, sticky = W)
                #txt_kktix_answer_dictionary.grid(column=1, row=txt_kktix_answer_dictionary_index, sticky = W)
                pass
            else:
                combo_kktix_area_mode.grid_forget()
                txt_kktix_answer_dictionary.grid_forget()

        else:
            frame_group_kktix.grid_forget()
    else:
        if show_block_index == 0:
            frame_group_kktix.grid(column=0, row=frame_group_kktix_index, padx=UI_PADDING_X)
            frame_group_tixcraft.grid_forget()

            if u'kktix' in new_homepage:
                combo_kktix_area_mode.grid(column=1, row=combo_kktix_area_mode_index, sticky = W)
                txt_kktix_answer_dictionary.grid(column=1, row=txt_kktix_answer_dictionary_index, sticky = W)
            else:
                combo_kktix_area_mode.grid_forget()
                txt_kktix_answer_dictionary.grid_forget()

        else:
            frame_group_tixcraft.grid(column=0, row=frame_group_tixcraft_index, padx=UI_PADDING_X)
            frame_group_kktix.grid_forget()

    lbl_kktix_area_mode_default = 'Area select order'
    lbl_kktix_answer_default = 'Answer Dictionary'
    if u'kktix' in new_homepage:
        lbl_kktix_area_mode['text'] = lbl_kktix_area_mode_default
        lbl_kktix_answer_dictionary['text'] = lbl_kktix_answer_default
    else:
        lbl_kktix_area_mode['text'] = ''
        lbl_kktix_answer_dictionary['text'] = ''

    showHideTixcraftBlocks()


def showHideTixcraftBlocks():
    # for tixcraft show/hide enable.
    # field 1
    global chk_state_date_auto_select

    global date_auto_select_mode_index
    global lbl_date_auto_select_mode
    global combo_date_auto_select_mode

    global date_keyword_index
    global lbl_date_keyword
    global txt_date_keyword

    # field 2
    global chk_area_auto_select

    global area_auto_select_index
    global lbl_area_auto_select_mode
    global combo_area_auto_select_mode

    global area_keyword_1_index
    global area_keyword_2_index
    global lbl_area_keyword_1
    global lbl_area_keyword_2
    global txt_area_keyword_1
    global txt_area_keyword_2

    is_date_set_to_enable = bool(chk_state_date_auto_select.get())
    is_area_set_to_enable = bool(chk_state_area_auto_select.get())
    #print("now is_date_set_to_enable value:", is_date_set_to_enable)
    #print("now is_area_set_to_enable value:", is_area_set_to_enable)

    if is_date_set_to_enable:
        # show
        lbl_date_auto_select_mode.grid(column=0, row=date_auto_select_mode_index, sticky = E)
        combo_date_auto_select_mode.grid(column=1, row=date_auto_select_mode_index, sticky = W)

        lbl_date_keyword.grid(column=0, row=date_keyword_index, sticky = E)
        txt_date_keyword.grid(column=1, row=date_keyword_index, sticky = W)
    else:
        # hide
        lbl_date_auto_select_mode.grid_forget()
        combo_date_auto_select_mode.grid_forget()

        lbl_date_keyword.grid_forget()
        txt_date_keyword.grid_forget()

    if is_area_set_to_enable:
        # show
        lbl_area_auto_select_mode.grid(column=0, row=area_auto_select_index, sticky = E)
        combo_area_auto_select_mode.grid(column=1, row=area_auto_select_index, sticky = W)

        lbl_area_keyword_1.grid(column=0, row=area_keyword_1_index, sticky = E)
        txt_area_keyword_1.grid(column=1, row=area_keyword_1_index, sticky = W)

        lbl_area_keyword_2.grid(column=0, row=area_keyword_2_index, sticky = E)
        txt_area_keyword_2.grid(column=1, row=area_keyword_2_index, sticky = W)
    else:
        # hide
        lbl_area_auto_select_mode.grid_forget()
        combo_area_auto_select_mode.grid_forget()

        lbl_area_keyword_1.grid_forget()
        txt_area_keyword_1.grid_forget()

        lbl_area_keyword_2.grid_forget()
        txt_area_keyword_2.grid_forget()


def MainMenu(root):
    global UI_PADDING_X
    UI_PADDING_X = 15
    global UI_PADDING_Y
    UI_PADDING_Y = 10

    lbl_homepage = None
    lbl_browser = None
    lbl_ticket_number = None
    lbl_kktix = None
    lbl_tixcraft = None

    homepage = None
    browser = None
    ticket_number = 1

    auto_press_next_step_button = None
    auto_fill_ticket_number = None

    kktix_area_mode = ""
    kktix_area_keyword = ""
    kktix_answer_dictionary = ""

    date_auto_select_enable = None
    date_auto_select_mode = ""
    date_keyword = ""

    area_auto_select_enable = None
    area_auto_select_mode = ""
    area_keyword_1 = ""
    area_keyword_2 = ""

    global config_dict
    if not config_dict is None:
        # read config.
        if u'homepage' in config_dict:
            homepage = config_dict["homepage"]

        if u'browser' in config_dict:
            browser = config_dict["browser"]

        # default ticket number
        # 說明：自動選擇的票數
        ticket_number = "2"
        if u'ticket_number' in config_dict:
            ticket_number = str(config_dict["ticket_number"])

        facebook_account = ""
        if 'facebook_account' in config_dict:
            facebook_account = str(config_dict["facebook_account"])

        # for ["kktix"]
        if 'kktix' in config_dict:
            auto_press_next_step_button = config_dict["kktix"]["auto_press_next_step_button"]
            auto_fill_ticket_number = config_dict["kktix"]["auto_fill_ticket_number"]

            if 'area_mode' in config_dict["kktix"]:
                kktix_area_mode = config_dict["kktix"]["area_mode"]
                kktix_area_mode = kktix_area_mode.strip()
            if not kktix_area_mode in CONST_SELECT_OPTIONS_ARRAY:
                kktix_area_mode = CONST_SELECT_ORDER_DEFAULT

            if 'area_keyword' in config_dict["kktix"]:
                kktix_area_keyword = config_dict["kktix"]["area_keyword"]
                if kktix_area_keyword is None:
                    kktix_area_keyword = ""
                kktix_area_keyword = kktix_area_keyword.strip()

            if 'answer_dictionary' in config_dict["kktix"]:
                kktix_answer_dictionary = config_dict["kktix"]["answer_dictionary"]
                if kktix_answer_dictionary is None:
                    kktix_answer_dictionary = ""
                kktix_answer_dictionary = kktix_answer_dictionary.strip()

        # for ["tixcraft"]
        if 'tixcraft' in config_dict:
            date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
            date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]

            if not date_auto_select_mode in CONST_SELECT_OPTIONS_ARRAY:
                date_auto_select_mode = CONST_SELECT_ORDER_DEFAULT

            if 'date_keyword' in config_dict["tixcraft"]["date_auto_select"]:
                date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"]
                date_keyword = date_keyword.strip()

            area_auto_select_enable = config_dict["tixcraft"]["area_auto_select"]["enable"]
            area_auto_select_mode = config_dict["tixcraft"]["area_auto_select"]["mode"]

            if not area_auto_select_mode in CONST_SELECT_OPTIONS_ARRAY:
                area_auto_select_mode = CONST_SELECT_ORDER_DEFAULT

            if 'area_keyword_1' in config_dict["tixcraft"]["area_auto_select"]:
                area_keyword_1 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_1"]
                area_keyword_1 = area_keyword_1.strip()

            if 'area_keyword_2' in config_dict["tixcraft"]["area_auto_select"]:
                area_keyword_2 = config_dict["tixcraft"]["area_auto_select"]["area_keyword_2"]
                area_keyword_2 = area_keyword_2.strip()

        # output config:
        print("homepage", homepage)
        print("browser", browser)
        print("ticket_number", ticket_number)
        print("facebook_account", facebook_account)

        # for kktix
        print("==[kktix]==")
        print("auto_press_next_step_button", auto_press_next_step_button)
        print("auto_fill_ticket_number", auto_fill_ticket_number)
        print("kktix_area_mode", kktix_area_mode)
        print("kktix_area_keyword", kktix_area_keyword)
        print("kktix_answer_dictionary", kktix_answer_dictionary)

        # for tixcraft
        print("==[tixcraft]==")
        print("date_auto_select_enable", date_auto_select_enable)
        print("date_auto_select_mode", date_auto_select_mode)
        print("date_keyword", date_keyword)
        
        print("area_auto_select_enable", area_auto_select_enable)
        print("area_auto_select_mode", area_auto_select_mode)
        print("area_keyword_1", area_keyword_1)
        print("area_keyword_2", area_keyword_2)
    else:
        print('config is none')

    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    # first row need padding Y
    lbl_homepage = Label(frame_group_header, text="Homepage", pady = UI_PADDING_Y)
    lbl_homepage.grid(column=0, row=group_row_count, sticky = E)

    #global txt_homepage
    #txt_homepage = Entry(root, width=20, textvariable = StringVar(root, value=homepage))
    #txt_homepage.grid(column=1, row=row_count)

    global combo_homepage
    combo_homepage = ttk.Combobox(frame_group_header, state="readonly")
    combo_homepage['values']= ("https://kktix.com","https://tixcraft.com","https://www.famiticket.com.tw","http://www.urbtix.hk/","https://www.cityline.com/")
    combo_homepage.set(homepage)
    combo_homepage.bind("<<ComboboxSelected>>", callbackHomepageOnChange)
    combo_homepage.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    lbl_browser = Label(frame_group_header, text="Browser")
    lbl_browser.grid(column=0, row=group_row_count, sticky = E)

    #global txt_browser
    #txt_browser = Entry(root, width=20, textvariable = StringVar(root, value=browser))
    #txt_browser.grid(column=1, row=group_row_count)

    global combo_browser
    combo_browser = ttk.Combobox(frame_group_header, state="readonly")
    combo_browser['values']= ("chrome","firefox")
    #combo_browser.current(0)
    combo_browser.set(browser)
    combo_browser.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    lbl_ticket_number = Label(frame_group_header, text="Ticket Number")
    lbl_ticket_number.grid(column=0, row=group_row_count, sticky = E)

    global txt_ticket_number
    global txt_ticket_number_value
    txt_ticket_number_value = StringVar(frame_group_header, value=ticket_number)
    txt_ticket_number = Entry(frame_group_header, width=20, textvariable = txt_ticket_number_value)
    txt_ticket_number.grid(column=1, row=group_row_count, sticky = W)

    frame_group_header.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)

    '''
    row_count+=1

    lbl_facebook_account = Label(root, text="Facebook Account")
    lbl_facebook_account.grid(column=0, row=row_count, sticky = E)

    global txt_facebook_account
    global txt_facebook_account_value
    txt_facebook_account_value = StringVar(root, value=facebook_account)
    txt_facebook_account = Entry(root, width=20, textvariable = txt_facebook_account_value)
    txt_facebook_account.grid(column=1, row=row_count, sticky = W)
    '''

    row_count+=1

    global frame_group_kktix
    frame_group_kktix = Frame(root)
    group_row_count = 0

    #lbl_kktix = Label(frame_group_kktix, text="[ KKTIX / URBTIX / Cityline]")
    lbl_kktix = Label(frame_group_kktix, text="")
    lbl_kktix.grid(column=0, row=group_row_count)

    group_row_count+=1

    lbl_auto_press_next_step_button = Label(frame_group_kktix, text="Auto Press Next Step Button")
    lbl_auto_press_next_step_button.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_auto_press_next_step_button
    chk_state_auto_press_next_step_button = BooleanVar()
    chk_state_auto_press_next_step_button.set(auto_press_next_step_button)

    chk_auto_press_next_step_button = Checkbutton(frame_group_kktix, text='Enable', variable=chk_state_auto_press_next_step_button)
    chk_auto_press_next_step_button.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    lbl_auto_fill_ticket_number = Label(frame_group_kktix, text="Auto Fill Ticket Number")
    lbl_auto_fill_ticket_number.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_auto_fill_ticket_number
    chk_state_auto_fill_ticket_number = BooleanVar()
    chk_state_auto_fill_ticket_number.set(auto_fill_ticket_number)

    chk_auto_auto_fill_ticket_number = Checkbutton(frame_group_kktix, text='Enable', variable=chk_state_auto_fill_ticket_number)
    chk_auto_auto_fill_ticket_number.grid(column=1, row=group_row_count, sticky = W)


    group_row_count+=1

    global lbl_kktix_area_mode
    lbl_kktix_area_mode = Label(frame_group_kktix, text="Area select order")
    lbl_kktix_area_mode.grid(column=0, row=group_row_count, sticky = E)

    global combo_kktix_area_mode
    global combo_kktix_area_mode_index
    combo_kktix_area_mode_index = group_row_count
    combo_kktix_area_mode = ttk.Combobox(frame_group_kktix, state="readonly")
    combo_kktix_area_mode['values']= CONST_SELECT_OPTIONS_DEFAULT
    combo_kktix_area_mode.set(kktix_area_mode)
    combo_kktix_area_mode.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    lbl_kktix_area_keyword = Label(frame_group_kktix, text="Area Keyword")
    lbl_kktix_area_keyword.grid(column=0, row=group_row_count, sticky = E)

    global txt_kktix_area_keyword
    global txt_kktix_area_keyword_value
    txt_kktix_area_keyword_value = StringVar(frame_group_kktix, value=kktix_area_keyword)
    txt_kktix_area_keyword = Entry(frame_group_kktix, width=20, textvariable = txt_kktix_area_keyword_value)
    txt_kktix_area_keyword.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global lbl_kktix_answer_dictionary
    lbl_kktix_answer_dictionary = Label(frame_group_kktix, text="Answer Dictionary")
    lbl_kktix_answer_dictionary.grid(column=0, row=group_row_count, sticky = E)

    global txt_kktix_answer_dictionary
    global txt_kktix_answer_dictionary_index
    txt_kktix_answer_dictionary_index = group_row_count
    global txt_kktix_answer_dictionary_value
    txt_kktix_answer_dictionary_value = StringVar(frame_group_kktix, value=kktix_answer_dictionary)
    txt_kktix_answer_dictionary = Entry(frame_group_kktix, width=20, textvariable = txt_kktix_answer_dictionary_value)
    txt_kktix_answer_dictionary.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    lbl_hr = Label(frame_group_kktix, text="")
    lbl_hr.grid(column=0, row=group_row_count)

    global frame_group_kktix_index
    frame_group_kktix_index = row_count
    frame_group_kktix.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)

    row_count+=1

    global frame_group_tixcraft
    frame_group_tixcraft = Frame(root)
    group_row_count = 0

    #lbl_tixcraft = Label(frame_group_tixcraft, text="[ tixCraft / FamiTicket]")
    lbl_tixcraft = Label(frame_group_tixcraft, text="")
    lbl_tixcraft.grid(column=0, row=group_row_count)

    group_row_count+=1

    lbl_date_auto_select = Label(frame_group_tixcraft, text="Date Auto Select")
    lbl_date_auto_select.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_date_auto_select
    chk_state_date_auto_select = BooleanVar()
    chk_state_date_auto_select.set(date_auto_select_enable)

    chk_date_auto_select = Checkbutton(frame_group_tixcraft, text='Enable', variable=chk_state_date_auto_select, command=callbackDateAutoOnChange)
    chk_date_auto_select.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global date_auto_select_mode_index
    date_auto_select_mode_index = group_row_count

    global lbl_date_auto_select_mode
    lbl_date_auto_select_mode = Label(frame_group_tixcraft, text="Date select order")
    lbl_date_auto_select_mode.grid(column=0, row=date_auto_select_mode_index, sticky = E)

    global combo_date_auto_select_mode
    combo_date_auto_select_mode = ttk.Combobox(frame_group_tixcraft, state="readonly")
    combo_date_auto_select_mode['values']= (CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP)
    combo_date_auto_select_mode.set(date_auto_select_mode)
    combo_date_auto_select_mode.grid(column=1, row=date_auto_select_mode_index, sticky = W)

    group_row_count+=1

    global date_keyword_index
    date_keyword_index = group_row_count

    global lbl_date_keyword
    lbl_date_keyword = Label(frame_group_tixcraft, text="Date Keyword")
    lbl_date_keyword.grid(column=0, row=date_keyword_index, sticky = E)

    global txt_date_keyword
    global txt_date_keyword_value
    txt_date_keyword_value = StringVar(frame_group_tixcraft, value=date_keyword)
    txt_date_keyword = Entry(frame_group_tixcraft, width=20, textvariable = txt_date_keyword_value)
    txt_date_keyword.grid(column=1, row=date_keyword_index, sticky = W)

    group_row_count+=1

    lbl_area_auto_select = Label(frame_group_tixcraft, text="Area Auto Select")
    lbl_area_auto_select.grid(column=0, row=group_row_count, sticky = E)

    global chk_state_area_auto_select
    chk_state_area_auto_select = BooleanVar()
    chk_state_area_auto_select.set(area_auto_select_enable)

    global chk_area_auto_select
    chk_area_auto_select = Checkbutton(frame_group_tixcraft, text='Enable', variable=chk_state_area_auto_select, command=callbackDateAutoOnChange)
    chk_area_auto_select.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    global area_auto_select_index
    area_auto_select_index = group_row_count

    global lbl_area_auto_select_mode
    lbl_area_auto_select_mode = Label(frame_group_tixcraft, text="Area select order")
    lbl_area_auto_select_mode.grid(column=0, row=area_auto_select_index, sticky = E)

    global combo_area_auto_select_mode
    combo_area_auto_select_mode = ttk.Combobox(frame_group_tixcraft, state="readonly")
    combo_area_auto_select_mode['values']= CONST_SELECT_OPTIONS_DEFAULT
    combo_area_auto_select_mode.set(area_auto_select_mode)
    combo_area_auto_select_mode.grid(column=1, row=area_auto_select_index, sticky = W)

    group_row_count+=1

    global area_keyword_1_index
    area_keyword_1_index = group_row_count

    global lbl_area_keyword_1
    lbl_area_keyword_1 = Label(frame_group_tixcraft, text="Area Keyword #1")
    lbl_area_keyword_1.grid(column=0, row=area_keyword_1_index, sticky = E)

    global txt_area_keyword_1
    global txt_area_keyword_1_value
    txt_area_keyword_1_value = StringVar(frame_group_tixcraft, value=area_keyword_1)
    txt_area_keyword_1 = Entry(frame_group_tixcraft, width=20, textvariable = txt_area_keyword_1_value)
    txt_area_keyword_1.grid(column=1, row=area_keyword_1_index, sticky = W)

    group_row_count+=1

    global area_keyword_2_index
    area_keyword_2_index = group_row_count

    global lbl_area_keyword_2
    lbl_area_keyword_2 = Label(frame_group_tixcraft, text="Area Keyword #2")
    lbl_area_keyword_2.grid(column=0, row=area_keyword_2_index, sticky = E)

    global txt_area_keyword_2
    global txt_area_keyword_2_value
    txt_area_keyword_2_value = StringVar(frame_group_tixcraft, value=area_keyword_2)
    txt_area_keyword_2 = Entry(frame_group_tixcraft, width=20, textvariable = txt_area_keyword_2_value)
    txt_area_keyword_2.grid(column=1, row=area_keyword_2_index, sticky = W)

    global frame_group_tixcraft_index
    frame_group_tixcraft_index = row_count
    frame_group_tixcraft.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)

    row_count+=1

    lbl_hr = Label(root, text="")
    lbl_hr.grid(column=0, row=row_count)

    row_count+=1

    frame_action = Frame(root)

    btn_run = ttk.Button(frame_action, text="Run", command=btn_run_clicked)
    btn_run.grid(column=0, row=0)

    btn_save = ttk.Button(frame_action, text="Save", command=btn_save_clicked)
    btn_save.grid(column=1, row=0)

    btn_exit = ttk.Button(frame_action, text="Exit", command=btn_exit_clicked)
    btn_exit.grid(column=2, row=0)

    frame_action.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)

    showHideBlocks(all_layout_visible=True)


def main():
    load_json()

    global root
    root = Tk()
    root.title(CONST_APP_VERSION)

    #style = ttk.Style(root)
    #style.theme_use('aqua')

    #root.configure(background='lightgray')
    # style configuration
    #style = Style(root)
    #style.configure('TLabel', background='lightgray', foreground='black')
    #style.configure('TFrame', background='lightgray')

    GUI = MainMenu(root)

    GUI_SIZE_WIDTH = 420
    GUI_SIZE_HEIGHT = 370
    GUI_SIZE_MACOS = str(GUI_SIZE_WIDTH) + 'x' + str(GUI_SIZE_HEIGHT)
    GUI_SIZE_WINDOWS=str(GUI_SIZE_WIDTH-60) + 'x' + str(GUI_SIZE_HEIGHT-20)

    GUI_SIZE =GUI_SIZE_MACOS
    import platform
    if platform.system() == 'Windows':
        GUI_SIZE =GUI_SIZE_WINDOWS
    root.geometry(GUI_SIZE)
    root.mainloop()

if __name__ == "__main__":
    main()