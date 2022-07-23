from otlpy.base.net import AsyncHttpClient
from otlpy.binance.common import Common
from otlpy.binance.settings import Settings
from otlpy.binance.spot import Spot


class API:
    def __init__(self, settings: Settings) -> None:
        self.__common = Common(settings)

    @property
    def _common(self) -> Common:
        return self.__common

    def CreateAsyncHttpClient(
        self, delay: float, debug: bool
    ) -> AsyncHttpClient:
        return AsyncHttpClient(self._common.url_base, delay=delay, debug=debug)

    def CreateSpot(self, client: AsyncHttpClient) -> Spot:
        return Spot(self._common, client)
