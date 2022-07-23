from typing import Any, Union

from loguru import logger

from otlpy.base.account import Buy, Cancel, Order, Sell
from otlpy.base.market import ORDER_TYPE
from otlpy.base.net import AsyncHttpClient
from otlpy.binance.common import Common


class Spot:
    def __init__(self, common: Common, client: AsyncHttpClient) -> None:
        self.__common = common
        self.__client = client

    @property
    def _common(self) -> Common:
        return self.__common

    @property
    def _client(self) -> AsyncHttpClient:
        return self.__client

    async def new_order(self, order: Union[Buy, Sell]) -> Order:
        url_path = "/api/v3/order"
        data = self._common.signature(
            {
                "symbol": order.ticker,
                "side": order.oside.name,
                "type": order.otype.name,
                "timeInForce": "GTC",
                "quantity": self._common.qty2str(order.ticker, order.qty),
                "price": self._common.price2str(order.ticker, order.price),
            }
        )
        headers = self._common.headers2()
        rheaders, rdata = await self._client.post_params(
            url_path, headers, data
        )
        if not rdata:
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return order
        order.acknowledgment(rdata, str(rdata["orderId"]), order.qty)
        return order

    async def cancel_order(self, order: Cancel) -> Order:
        url_path = "/api/v3/order"
        data = self._common.signature(
            {
                "symbol": order.ticker,
                "orderId": order.origin.rdata["orderId"],
            }
        )
        headers = self._common.headers2()
        rheaders, rdata = await self._client.delete(url_path, headers, data)
        if not rdata:
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return order
        order.acknowledgment(rdata, "C_" + str(rdata["orderId"]), 0)
        return order

    async def buy(
        self, order_type: ORDER_TYPE, ticker: str, qty: float, price: float
    ) -> Order:
        return await self.new_order(Buy(order_type, ticker, qty, price))

    async def buy_market(self, ticker: str, qty: float) -> Order:
        return await self.buy(ORDER_TYPE.MARKET, ticker, qty, 0)

    async def buy_limit(self, ticker: str, qty: float, price: float) -> Order:
        return await self.buy(ORDER_TYPE.LIMIT, ticker, qty, price)

    async def sell(
        self, order_type: ORDER_TYPE, ticker: str, qty: float, price: float
    ) -> Order:
        return await self.new_order(Sell(order_type, ticker, qty, price))

    async def sell_market(self, ticker: str, qty: float) -> Order:
        return await self.sell(ORDER_TYPE.MARKET, ticker, qty, 0)

    async def sell_limit(self, ticker: str, qty: float, price: float) -> Order:
        return await self.sell(ORDER_TYPE.LIMIT, ticker, qty, price)

    async def cancel(self, origin: Order) -> Order:
        return await self.cancel_order(Cancel(origin, ORDER_TYPE.LIMIT))

    async def all_orders(self, ticker: str) -> list[dict[str, Any]]:
        url_path = "/api/v3/allOrders"
        data = self._common.signature(
            {
                "symbol": ticker,
                "startTime": self._common.starttime,
            }
        )
        headers = self._common.headers2()
        rheaders, rdata = await self._client.get(url_path, headers, data)
        if not rdata:
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return []
        return list(rdata)

    async def limitorderbook(self, ticker: str) -> dict[str, Any]:
        url_path = "/api/v3/depth"
        data = {
            "symbol": ticker,
        }
        headers = self._common.headers1()
        rheaders, rdata = await self._client.get(url_path, headers, data)
        if not rdata:
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return {}
        return dict(rdata)
