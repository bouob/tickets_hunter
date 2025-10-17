import base64
import requests
from io import BytesIO
from PIL import Image
from typing import Optional
from requests.exceptions import RequestException

class NonBrowser:
    def __init__(self, domain_name: str = "tixcraft.com") -> None:
        self.session = requests.Session()
        self.set_domain(domain_name)

    def set_cookies(self, cookies: Optional[dict]) -> bool:
        if cookies is not None:
            [self.session.cookies.set(cookie["name"], cookie["value"]) for cookie in cookies]
            return True
        return False

    def get_cookies(self) -> dict:
        return self.session.cookies.get_dict()

    def set_headers(self, header: str) -> None:
        self.session.headers = header

    def set_domain(self, domain_name: str, captcha_url: str = "ticket/captcha", refresh_url: str = "ticket/captcha?refresh=1") -> None:
        self.url = f"https://{domain_name}/{captcha_url}"
        self.refresh_url = f"https://{domain_name}/{refresh_url}"

    def request_captcha(self) -> bytes:
        response = self.session.get(self.url, stream=True)
        img = Image.open(BytesIO(response.content))
        output_buffer = BytesIO()
        img.save(output_buffer, format='JPEG')
        binary_data = output_buffer.getvalue()
        return base64.b64encode(binary_data)

    def request_refresh_captcha(self) -> str:
        try:
            response = self.session.get(self.refresh_url, stream=True)
            if response.status_code == 200:
                return response.json().get("url", "")
        except RequestException:
            pass
        return ""