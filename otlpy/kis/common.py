from typing import Any, Optional

from otlpy.base.net import AsyncHttpClient
from otlpy.kis.settings import Settings


class Common:
    def __init__(self, settings: Settings) -> None:
        self.__settings = settings
        self.__url_base = "https://openapi.koreainvestment.com:9443"
        self.__url_ws = "ws://ops.koreainvestment.com:21000"
        self.__authorization = ""
        self.__content_type = "application/json; charset=UTF-8"

    @property
    def _settings(self) -> Settings:
        return self.__settings

    @property
    def url_base(self) -> str:
        return self.__url_base

    @property
    def url_ws(self) -> str:
        return self.__url_ws

    @property
    def _authorization(self) -> str:
        return self.__authorization

    def _set_authorization(self, authorization: str) -> None:
        self.__authorization = authorization

    @property
    def _content_type(self) -> str:
        return self.__content_type

    @property
    def _app_key(self) -> str:
        return self._settings.kis_app_key

    @property
    def _app_secret(self) -> str:
        return self._settings.kis_app_secret

    @property
    def account_htsid(self) -> str:
        return self._settings.kis_account_htsid

    @property
    def _account_custtype(self) -> str:
        return self._settings.kis_account_custtype

    @property
    def account_cano_domestic_stock(self) -> Optional[str]:
        return self._settings.kis_account_cano_domestic_stock

    @property
    def account_prdt_domestic_stock(self) -> Optional[str]:
        return self._settings.kis_account_prdt_domestic_stock

    @property
    def account_cano_domestic_futureoption(self) -> Optional[str]:
        return self._settings.kis_account_cano_domestic_futureoption

    @property
    def account_prdt_domestic_futureoption(self) -> Optional[str]:
        return self._settings.kis_account_prdt_domestic_futureoption

    @property
    def account_cano_overseas_stock(self) -> Optional[str]:
        return self._settings.kis_account_cano_overseas_stock

    @property
    def account_prdt_overseas_stock(self) -> Optional[str]:
        return self._settings.kis_account_prdt_overseas_stock

    def headers1(self) -> dict[str, str]:
        return {
            "content-type": self._content_type,
        }

    def headers3(self) -> dict[str, str]:
        return {
            "content-type": self._content_type,
            "appkey": self._app_key,
            "appsecret": self._app_secret,
        }

    def headers4(self) -> dict[str, str]:
        return {
            "content-type": self._content_type,
            "appkey": self._app_key,
            "appsecret": self._app_secret,
            "authorization": self._authorization,
        }

    async def hash(self, client: AsyncHttpClient, data: Any) -> str:
        url_path = "/uapi/hashkey"
        headers = self.headers3()
        _, rdata = await client.post(url_path, headers, data)
        return str(rdata["HASH"])

    async def token(self, client: AsyncHttpClient) -> None:
        url_path = "/oauth2/tokenP"
        headers = self.headers1()
        data = {
            "grant_type": "client_credentials",
            "appkey": self._app_key,
            "appsecret": self._app_secret,
        }
        _, rdata = await client.post(url_path, headers, data)
        self._set_authorization(
            "%s %s" % (rdata["token_type"], rdata["access_token"])
        )

    def ws_senddata(self, subscribe: bool, tr_id: str, tr_key: str) -> str:
        if subscribe:
            tr_type = "1"
        else:
            tr_type = "2"
        return (
            '{"header":{"appkey":"'
            + self._app_key
            + '","appsecret":"'
            + self._app_secret
            + '","custtype":"'
            + self._account_custtype
            + '","tr_type":"'
            + tr_type
            + '","content-type":"utf-8"},"body":{"input":{"tr_id":"'
            + tr_id
            + '","tr_key":"'
            + tr_key
            + '"}}}'
        )
