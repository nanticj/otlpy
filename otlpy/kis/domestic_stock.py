from typing import Any, Union

from loguru import logger

from otlpy.base.account import Buy, Cancel, Order, Replace, Sell
from otlpy.base.market import ORDER_SIDE, ORDER_TYPE
from otlpy.base.net import AsyncHttpClient, AsyncWebSocketClient
from otlpy.kis.common import Common


def str_order_type(order_type: ORDER_TYPE) -> str:
    if order_type == ORDER_TYPE.LIMIT:
        s = "00"
    elif order_type == ORDER_TYPE.MARKET:
        s = "01"
    else:
        assert False
    return s


class DomesticStock:
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
        if order.oside == ORDER_SIDE.BUY:
            tr_id = "TTTC0802U"
        elif order.oside == ORDER_SIDE.SELL:
            tr_id = "TTTC0801U"
        else:
            assert False
        url_path = "/uapi/domestic-stock/v1/trading/order-cash"
        data = {
            "CANO": self._common.account_cano_domestic_stock,
            "ACNT_PRDT_CD": self._common.account_prdt_domestic_stock,
            "PDNO": order.ticker,
            "ORD_DVSN": str_order_type(order.otype),
            "ORD_QTY": str(int(order.qty)),
            "ORD_UNPR": str(int(order.price)),
        }
        headers = {
            **self._common.headers4(),
            "tr_id": tr_id,
            "hashkey": await self._common.hash(self._client, data),
        }
        rheaders, rdata = await self._client.post(url_path, headers, data)
        if not rdata or rdata["rt_cd"] != "0":
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return order
        rdata_output = rdata["output"]
        order.acknowledgment(rdata_output, rdata_output["ODNO"], order.qty)
        return order

    async def cancel_or_replace_order(
        self, order: Union[Cancel, Replace]
    ) -> Order:
        if isinstance(order, Cancel):
            omsg = "02"
        elif isinstance(order, Replace):
            omsg = "01"
        else:
            assert False
        tr_id = "TTTC0803U"
        url_path = "/uapi/domestic-stock/v1/trading/order-rvsecncl"
        data = {
            "CANO": self._common.account_cano_domestic_stock,
            "ACNT_PRDT_CD": self._common.account_prdt_domestic_stock,
            "KRX_FWDG_ORD_ORGNO": order.origin.rdata["KRX_FWDG_ORD_ORGNO"],
            "ORGN_ODNO": order.origin.rdata["ODNO"],
            "ORD_DVSN": str_order_type(order.otype),
            "RVSE_CNCL_DVSN_CD": omsg,
            "ORD_QTY": str(int(order.qty)),
            "ORD_UNPR": str(int(order.price)),
            "QTY_ALL_ORD_YN": "Y",
        }
        headers = {
            **self._common.headers4(),
            "tr_id": tr_id,
            "hashkey": await self._common.hash(self._client, data),
        }
        rheaders, rdata = await self._client.post(url_path, headers, data)
        if not rdata or rdata["rt_cd"] != "0":
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return order
        rdata_output = rdata["output"]
        if isinstance(order, Cancel):
            order.acknowledgment(rdata_output, rdata_output["ODNO"], 0)
        elif isinstance(order, Replace):
            order.acknowledgment(rdata_output, rdata_output["ODNO"], order.qty)
        else:
            assert False
        return order

    async def buy(
        self, order_type: ORDER_TYPE, ticker: str, qty: int, price: int
    ) -> Order:
        return await self.new_order(Buy(order_type, ticker, qty, price))

    async def buy_market(self, ticker: str, qty: int) -> Order:
        return await self.buy(ORDER_TYPE.MARKET, ticker, qty, 0)

    async def buy_limit(self, ticker: str, qty: int, price: int) -> Order:
        return await self.buy(ORDER_TYPE.LIMIT, ticker, qty, price)

    async def sell(
        self, order_type: ORDER_TYPE, ticker: str, qty: int, price: int
    ) -> Order:
        return await self.new_order(Sell(order_type, ticker, qty, price))

    async def sell_market(self, ticker: str, qty: int) -> Order:
        return await self.sell(ORDER_TYPE.MARKET, ticker, qty, 0)

    async def sell_limit(self, ticker: str, qty: int, price: int) -> Order:
        return await self.sell(ORDER_TYPE.LIMIT, ticker, qty, price)

    async def cancel(self, origin: Order) -> Order:
        return await self.cancel_or_replace_order(
            Cancel(origin, ORDER_TYPE.LIMIT)
        )

    async def replace(
        self, origin: Order, order_type: ORDER_TYPE, price: int
    ) -> Order:
        return await self.cancel_or_replace_order(
            Replace(origin, order_type, price)
        )

    async def replace_market(self, origin: Order) -> Order:
        return await self.replace(origin, ORDER_TYPE.MARKET, 0)

    async def replace_limit(self, origin: Order, price: int) -> Order:
        return await self.replace(origin, ORDER_TYPE.LIMIT, price)

    async def all_orders(
        self,
        yyyymmdd: str,
        tr_cont: str,
        ctx_area_fk100: str,
        ctx_area_nk100: str,
    ) -> tuple[list[Any], str, str, str]:
        tr_id = "TTTC8001R"
        url_path = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
        data = {
            "CANO": self._common.account_cano_domestic_stock,
            "ACNT_PRDT_CD": self._common.account_prdt_domestic_stock,
            "INQR_STRT_DT": yyyymmdd,
            "INQR_END_DT": yyyymmdd,
            "SLL_BUY_DVSN_CD": "00",
            "INQR_DVSN": "00",
            "PDNO": "",
            "CCLD_DVSN": "00",
            "ORD_GNO_BRNO": "",
            "ODNO": "",
            "INQR_DVSN_3": "",
            "INQR_DVSN_1": "",
            "CTX_AREA_FK100": ctx_area_fk100,
            "CTX_AREA_NK100": ctx_area_nk100,
        }
        headers = {
            **self._common.headers4(),
            "tr_id": tr_id,
            "tr_cont": tr_cont,
        }
        rheaders, rdata = await self._client.get(url_path, headers, data)
        if not rdata or rdata["rt_cd"] != "0":
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return [], "", "", ""
        if rheaders["tr_cont"] == "D" or rheaders["tr_cont"] == "E":
            return rdata["output1"], "", "", ""
        if rheaders["tr_cont"] == "F" or rheaders["tr_cont"] == "M":
            return (
                rdata["output1"],
                "N",
                rdata["ctx_area_fk100"],
                rdata["ctx_area_nk100"],
            )
        assert False

    async def limitorderbook(self, ticker: str) -> dict[str, Any]:
        tr_id = "FHKST01010200"
        url_path = (
            "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"
        )
        data = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": ticker,
        }
        headers = {
            **self._common.headers4(),
            "tr_id": tr_id,
        }
        rheaders, rdata = await self._client.get(url_path, headers, data)
        if not rdata or rdata["rt_cd"] != "0":
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return {}
        return dict(rdata["output1"])


class DomesticStockWS:
    def __init__(self, common: Common, ws: AsyncWebSocketClient) -> None:
        self.__common = common
        self.__ws = ws

    @property
    def _common(self) -> Common:
        return self.__common

    @property
    def _ws(self) -> AsyncWebSocketClient:
        return self.__ws

    def senddata_trade(self, ticker: str, subscribe: bool = True) -> str:
        return self._common.ws_senddata(subscribe, "H0STCNT0", ticker)

    def senddata_orderbook(self, ticker: str, subscribe: bool = True) -> str:
        return self._common.ws_senddata(subscribe, "H0STASP0", ticker)

    def senddata_execution(self, subscribe: bool = True) -> str:
        return self._common.ws_senddata(
            subscribe, "H0STCNI0", self._common.account_htsid
        )
