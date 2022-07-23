from otlpy.base.net import AsyncHttpClient, AsyncWebSocketClient
from otlpy.kis.common import Common
from otlpy.kis.domestic_stock import DomesticStock, DomesticStockWS
from otlpy.kis.settings import Settings


class API:
    def __init__(self, settings: Settings) -> None:
        self.__common = Common(settings)

    @property
    def _common(self) -> Common:
        return self.__common

    def CreateAsyncWebSocketClient(
        self, delay_send: float, delay_recv: float, debug: bool
    ) -> AsyncWebSocketClient:
        return AsyncWebSocketClient(
            self._common.url_ws,
            delay_send=delay_send,
            delay_recv=delay_recv,
            debug=debug,
        )

    def CreateAsyncHttpClient(
        self, delay: float, debug: bool
    ) -> AsyncHttpClient:
        return AsyncHttpClient(self._common.url_base, delay=delay, debug=debug)

    def CreateDomesticStockWS(
        self, ws: AsyncWebSocketClient
    ) -> DomesticStockWS:
        return DomesticStockWS(self._common, ws)

    def CreateDomesticStock(self, client: AsyncHttpClient) -> DomesticStock:
        return DomesticStock(self._common, client)
