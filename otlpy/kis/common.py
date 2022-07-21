from typing import Any, Optional

from httpx import AsyncClient

from otlpy.base.net import post
from otlpy.kis.settings import Settings


class Common:
    def __init__(self, settings: Settings) -> None:
        self.__settings = settings
        self.__url_base = "https://openapi.koreainvestment.com:9443"
        self.__url_ws = "ws://ops.koreainvestment.com:21000"
        self.__authorization = ""
        self.__content_type = "application/json; charset=UTF-8"

    @property
    def kis_app_key(self) -> str:
        return self.__settings.kis_app_key

    @property
    def kis_app_secret(self) -> str:
        return self.__settings.kis_app_secret

    @property
    def kis_account_htsid(self) -> str:
        return self.__settings.kis_account_htsid

    @property
    def kis_account_custtype(self) -> str:
        return self.__settings.kis_account_custtype

    @property
    def kis_account_cano_domestic_stock(self) -> Optional[str]:
        return self.__settings.kis_account_cano_domestic_stock

    @property
    def kis_account_prdt_domestic_stock(self) -> Optional[str]:
        return self.__settings.kis_account_prdt_domestic_stock

    @property
    def kis_account_cano_domestic_futureoption(self) -> Optional[str]:
        return self.__settings.kis_account_cano_domestic_futureoption

    @property
    def kis_account_prdt_domestic_futureoption(self) -> Optional[str]:
        return self.__settings.kis_account_prdt_domestic_futureoption

    @property
    def kis_account_cano_overseas_stock(self) -> Optional[str]:
        return self.__settings.kis_account_cano_overseas_stock

    @property
    def kis_account_prdt_overseas_stock(self) -> Optional[str]:
        return self.__settings.kis_account_prdt_overseas_stock

    @property
    def url_base(self) -> str:
        return self.__url_base

    @property
    def url_ws(self) -> str:
        return self.__url_ws

    @property
    def authorization(self) -> str:
        return self.__authorization

    @property
    def content_type(self) -> str:
        return self.__content_type

    def headers1(self) -> dict[str, str]:
        return {
            "content-type": self.content_type,
        }

    def headers3(self) -> dict[str, str]:
        return {
            "content-type": self.content_type,
            "appkey": self.kis_app_key,
            "appsecret": self.kis_app_secret,
        }

    def headers4(self) -> dict[str, str]:
        return {
            "content-type": self.content_type,
            "appkey": self.kis_app_key,
            "appsecret": self.kis_app_secret,
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
            "appkey": self.kis_app_key,
            "appsecret": self.kis_app_secret,
        }
        _, rdata = await post(client, url_path, headers, data, sleep, debug)
        self.__authorization = "%s %s" % (
            rdata["token_type"],
            rdata["access_token"],
        )
