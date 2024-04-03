#!/usr/bin/env python
#encoding=utf-8
import argparse
import asyncio
import base64
import json
import os
import sys
import time

import nodriver as uc
import requests

import util

CONST_APP_VERSION = "MaxBot (2024.03.21)"

CONST_MAXBOT_CONFIG_FILE = "settings.json"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
PROFILE_URL = "https://kktix.com/users/edit"
SIGNIN_URL = "https://kktix.com/users/sign_in"

def load_json():
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
    else:
        config_dict = get_default_config()
    return config_filepath, config_dict

def kktix_signin_requests(kktix_account, kktix_password):
    import urllib.parse
    headers = {
        "accept-language": "zh-TW;q=0.7", 
        "cache-control": "max-age=0", 
        "origin": "https://kktix.com", 
        'User-Agent': USER_AGENT
        }

    authenticity_token = ""
    utf8 = "✓"
    try:
        response = requests.get(profile_url , headers=headers, timeout=0.7, allow_redirects=True)
        status_code = response.status_code
        #print("status_code:",status_code)
        #if status_code == 200:
        #print(response.content)

        response = requests.get(signin_url , headers=headers, timeout=0.7, allow_redirects=False)
        s = requests.session()
        #print(response.cookies)
        for key, value in response.cookies.items():
            print(key + '=' + value)
            if key=="XSRF-TOKEN":
                #authenticity_token = urllib.parse.unquote(value)
                authenticity_token = value

        login_data={
            "utf8": utf8, 
            "authenticity_token": authenticity_token,
            "user[login]": kktix_account,
            "user[password]": kktix_password,
            "user[remember_me]": 0
            }
        #print("login_data", login_data)
        
        login_data_string = 'utf8=%E2%9C%93&authenticity_token='+ authenticity_token +'&user%5Blogin%5D='+ kktix_account +'&user%5Bpassword%5D='+ kktix_password +'&user%5Bremember_me%5D=0'
        #print("login_data_string", login_data_string)
        
        response=s.post(signin_url, data=login_data)
        #response=s.post(signin_url, data=login_data_string) 
        status_code = response.status_code
        #print("status_code:",status_code)
        #if status_code == 200:
        #print (response.status_code) 
        #print (response.content)

        response = s.get(profile_url , headers=headers, timeout=0.7, allow_redirects=False)
        status_code = response.status_code
        #print("status_code:",status_code)
        #if status_code == 200:
        #print(response.content)

    except Exception as exc:
        print(exc)

async def kktix_signin_nodriver(tab, kktix_account, kktix_password):
    while True:
        try:
    
            #html = await tab.get_content()
            #await tab.sleep(0.1)
            #print(html)

            x_window = await tab.js_dumps('window')
            #print(x_window["location"]["href"])
            if x_window["location"]["href"]==SIGNIN_URL:
                account = await tab.select("#user_login")
                await account.send_keys(kktix_account)
                #await tab.sleep(0.1)

                password = await tab.select("#user_password")
                await password.send_keys(kktix_password)
                #await tab.sleep(0.1)

                submit = await tab.select("div.form-actions a.btn-primary")
                await submit.click()
                
                await tab.sleep(0.5)
                #tab = await tab.get(SIGNOUT_URL)

            signout = await tab.select("a[href='/users/sign_out']")
            await signout.click()
            await tab.sleep(0.5)

            tab = await tab.get(SIGNIN_URL)
        except Exception as e:
            print(e)
            
            if str(e)=="coroutine raised StopIteration":
                break
            pass


#def kktix_signout_main(config_dict):
async def kktix_signout_main(config_dict):
    conf = util.get_extension_config()
    driver = await uc.start(conf)
    tab = await driver.get(SIGNIN_URL)

    #if not config_dict["advanced"]["headless"]:
    if len(config_dict["advanced"]["window_size"]) > 0:
        if "," in config_dict["advanced"]["window_size"]:
            target_array = config_dict["advanced"]["window_size"].split(",")
            await tab.set_window_size(left=20, top=20, width=int(target_array[0]), height=int(target_array[1]))

    kktix_account = config_dict["advanced"]["kktix_account"]
    kktix_password = config_dict["advanced"]["kktix_password_plaintext"].strip()
    if kktix_password == "":
        kktix_password = util.decryptMe(config_dict["advanced"]["kktix_password"])

    print("kktix_account:", kktix_account)
    #print("kktix_password:", kktix_password)

    #kktix_signin_requests(kktix_account, kktix_password)
    await kktix_signin_nodriver(tab, kktix_account, kktix_password)


#def main(args):
async def main(args):
    config_filepath, config_dict = load_json()

    if not args.kktix_account is None:
        if len(args.kktix_account) > 0:
            config_dict["advanced"]["kktix_account"] = args.kktix_account
    if not args.kktix_password is None:
        if len(args.kktix_password) > 0:
            config_dict["advanced"]["kktix_password_plaintext"] = args.kktix_password

    if len(config_dict["advanced"]["kktix_account"]) > 0:
        #kktix_account_loop(config_dict)
        await kktix_signout_main(config_dict)
    else:
        print("請輸入 kktix_account")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="MaxBot Aggument Parser")

    parser.add_argument("--kktix_account",
        help="overwrite kktix_account field",
        type=str)

    parser.add_argument("--kktix_password",
        help="overwrite kktix_password field",
        type=str)

    args = parser.parse_args()
    #main(args)
    uc.loop().run_until_complete(main(args))
