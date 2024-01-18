import base64
import json
from io import BytesIO

import requests
from PIL import Image


class NonBrowser():
    def __init__(self, domain_name = "tixcraft.com") -> None:
        self.Session = requests.session()
        self.Set_Domain(domain_name)

    def Set_cookies(self, cookies:dict):
        ret = False
        if not cookies is None:
            for cookie in cookies:
                self.Session.cookies.set(cookie["name"],cookie["value"])
                ret = True
        return ret

    def Get_cookies(self):
        return self.Session.cookies.get_dict()

    def set_headers(self, header:str):
        self.Session.headers = header

    def Set_Domain(self, domain_name, captcha_url="ticket/captcha", refresh_url="ticket/captcha?refresh=1"):
        self.url = "https://%s/%s" % (domain_name, captcha_url)
        self.refresh_url = "https://%s/%s" % (domain_name, refresh_url)

    def Request_Captcha(self):
        img = Image.open(BytesIO(self.Session.get(self.url, stream = True).content))
        output_buffer = BytesIO()
        img.save(output_buffer, format='JPEG')
        binary_data = output_buffer.getvalue()
        base64_data = base64.b64encode(binary_data)
        return base64_data

    def Request_Refresh_Captcha(self) -> str:
        try:
            result = self.Session.get(self.refresh_url, stream = True)
            if result.status_code == 200:
                json_data = json.loads(result.text)
                return json_data.get("url","")
            else:
                return ""
        except Exception as e:
            return ""