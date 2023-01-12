import requests
import json
import base64
from PIL import Image
from io import BytesIO

class NonBrowser():
    def __init__(self) -> None:
        self.Session = requests.session()
        self.url = "https://tixcraft.com/ticket/captcha"
        self.refresh_url = "https://tixcraft.com/ticket/captcha?refresh=1"

    def Set_cookies(self,cookies:dict):
        for cookie in cookies:
            self.Session.cookies.set(cookie["name"],cookie["value"])
        return True

    def set_headers(self,header:str):
        self.Session.headers = header

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