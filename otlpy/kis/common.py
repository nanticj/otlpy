from typing import Any

from httpx import AsyncClient

from otlpy.base.net import post
from otlpy.kis.settings import Settings


class Common:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.url_base = "https://openapi.koreainvestment.com:9443"
        self.url_ws = "ws://ops.koreainvestment.com:21000"
        self.authorization = ""
        self.content_type = "application/json; charset=UTF-8"

    def headers1(self) -> dict[str, str]:
        return {
            "content-type": self.content_type,
        }

    def headers3(self) -> dict[str, str]:
        return {
            "content-type": self.content_type,
            "appkey": self.settings.kis_app_key,
            "appsecret": self.settings.kis_app_secret,
        }

    def headers4(self) -> dict[str, str]:
        return {
            "content-type": self.content_type,
            "appkey": self.settings.kis_app_key,
            "appsecret": self.settings.kis_app_secret,
            "authorization": self.authorization,
        }

    async def hash(
        self,
        client: AsyncClient,
        data: Any,
        sleep: float,
        debug: bool,
    ) -> str:
        url_path = "/uapi/hashkey"
        headers = self.headers3()
        _, rdata = await post(client, url_path, headers, data, sleep, debug)
        return str(rdata["HASH"])

    async def token(
        self,
        client: AsyncClient,
        sleep: float,
        debug: bool,
    ) -> None:
        url_path = "/oauth2/tokenP"
        headers = self.headers1()
        data = {
            "grant_type": "client_credentials",
            "appkey": self.settings.kis_app_key,
            "appsecret": self.settings.kis_app_secret,
        }
        _, rdata = await post(client, url_path, headers, data, sleep, debug)
        self.authorization = "%s %s" % (
            rdata["token_type"],
            rdata["access_token"],
        )
