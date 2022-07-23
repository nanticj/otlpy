import time
from typing import Any
from urllib.parse import urlencode

from otlpy.base.crypto import hmac_sha256
from otlpy.binance.settings import Settings


def drop_none(data: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k, v in data.items():
        if v is not None:
            out[k] = v
    return out


def timestamp() -> int:
    return int(time.time() * 1000)


class Common:
    def __init__(self, settings: Settings) -> None:
        self.__settings = settings
        self.__url_base = "https://api.binance.com"
        self.__content_type = "application/json; charset=UTF-8"
        self.__starttime = timestamp()

    @property
    def _settings(self) -> Settings:
        return self.__settings

    @property
    def url_base(self) -> str:
        return self.__url_base

    @property
    def _content_type(self) -> str:
        return self.__content_type

    @property
    def starttime(self) -> int:
        return self.__starttime

    def set_starttime(self) -> None:
        self.__starttime = timestamp()

    @property
    def _app_key(self) -> str:
        return self._settings.binance_app_key

    @property
    def _app_secret(self) -> str:
        return self._settings.binance_app_secret

    def headers1(self) -> dict[str, str]:
        return {
            "content-type": self._content_type,
        }

    def headers2(self) -> dict[str, str]:
        return {
            "content-type": self._content_type,
            "X-MBX-APIKEY": self._app_key,
        }

    def signature(self, data: dict[str, Any]) -> dict[str, Any]:
        out = drop_none(data)
        out["timestamp"] = timestamp()
        out["signature"] = hmac_sha256(self._app_secret, urlencode(out, True))
        return out

    def qty2str(self, ticker: str, qty: float) -> str:
        # TODO
        return str(qty)

    def price2str(self, ticker: str, price: float) -> str:
        # TODO
        return str(price)

    def str2qty(self, ticker: str, qty: str) -> float:
        # TODO
        return float(qty)

    def str2price(self, ticker: str, price: str) -> float:
        # TODO
        return float(price)
