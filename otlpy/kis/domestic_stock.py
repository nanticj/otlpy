from typing import Any, Union

from httpx import AsyncClient
from loguru import logger

from otlpy.base.account import Buy, Cancel, Order, Replace, Sell
from otlpy.base.market import ORDER_SIDE, ORDER_TYPE
from otlpy.base.net import get, post
from otlpy.kis.common import Common


class DomesticStock:
    def __init__(self, common: Common) -> None:
        self.common = common
        self.settings = common.settings

    def order_type(self, order_type: ORDER_TYPE) -> str:
        if order_type == ORDER_TYPE.LIMIT:
            s = "00"
        elif order_type == ORDER_TYPE.MARKET:
            s = "01"
        else:
            assert False
        return s

    async def new_order(
        self,
        client: AsyncClient,
        order: Union[Buy, Sell],
        sleep: float,
        debug: bool,
    ) -> Order:
        order.qty = int(order.qty)
        if order.otype == ORDER_TYPE.MARKET:
            order.price = int(0)
        else:
            order.price = int(order.price)
        if order.oside == ORDER_SIDE.BUY:
            tr_id = "TTTC0802U"
        elif order.oside == ORDER_SIDE.SELL:
            tr_id = "TTTC0801U"
        else:
            assert False
        url_path = "/uapi/domestic-stock/v1/trading/order-cash"
        data = {
            "CANO": self.settings.kis_account_cano_domestic_stock,
            "ACNT_PRDT_CD": self.settings.kis_account_prdt_domestic_stock,
            "PDNO": order.ticker,
            "ORD_DVSN": self.order_type(order.otype),
            "ORD_QTY": str(int(order.qty)),
            "ORD_UNPR": str(int(order.price)),
        }
        headers = {
            **self.common.headers4(),
            "tr_id": tr_id,
            "hashkey": await self.common.hash(client, data, 0, False),
        }
        rheaders, rdata = await post(
            client, url_path, headers, data, sleep, debug
        )
        if not rdata or rdata["rt_cd"] != "0":
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return order
        order.rdata = rdata["output"]
        order.uid = order.rdata["ODNO"]
        order.opened = order.qty
        return order

    async def cancel_or_replace_order(
        self,
        client: AsyncClient,
        order: Union[Cancel, Replace],
        sleep: float,
        debug: bool,
    ) -> Order:
        if isinstance(order, Cancel):
            omsg = "02"
            order.price = int(0)
        elif isinstance(order, Replace):
            omsg = "01"
            order.price = int(order.price)
        else:
            assert False
        tr_id = "TTTC0803U"
        url_path = "/uapi/domestic-stock/v1/trading/order-rvsecncl"
        data = {
            "CANO": self.settings.kis_account_cano_domestic_stock,
            "ACNT_PRDT_CD": self.settings.kis_account_prdt_domestic_stock,
            "KRX_FWDG_ORD_ORGNO": order.origin.rdata["KRX_FWDG_ORD_ORGNO"],
            "ORGN_ODNO": order.origin.rdata["ODNO"],
            "ORD_DVSN": self.order_type(order.otype),
            "RVSE_CNCL_DVSN_CD": omsg,
            "ORD_QTY": str(int(order.qty)),
            "ORD_UNPR": str(int(order.price)),
            "QTY_ALL_ORD_YN": "Y",
        }
        headers = {
            **self.common.headers4(),
            "tr_id": tr_id,
            "hashkey": await self.common.hash(client, data, 0, False),
        }
        rheaders, rdata = await post(
            client, url_path, headers, data, sleep, debug
        )
        if not rdata or rdata["rt_cd"] != "0":
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return order
        order.rdata = rdata["output"]
        order.uid = order.rdata["ODNO"]
        order.opened = order.qty
        return order

    async def buy(
        self,
        client: AsyncClient,
        order_type: ORDER_TYPE,
        ticker: str,
        qty: int,
        price: int,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.new_order(
            client, Buy(order_type, ticker, qty, price), sleep, debug
        )

    async def buy_market(
        self,
        client: AsyncClient,
        ticker: str,
        qty: int,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.buy(
            client, ORDER_TYPE.MARKET, ticker, qty, 0, sleep, debug
        )

    async def buy_limit(
        self,
        client: AsyncClient,
        ticker: str,
        qty: int,
        price: int,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.buy(
            client, ORDER_TYPE.LIMIT, ticker, qty, price, sleep, debug
        )

    async def sell(
        self,
        client: AsyncClient,
        order_type: ORDER_TYPE,
        ticker: str,
        qty: int,
        price: int,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.new_order(
            client, Sell(order_type, ticker, qty, price), sleep, debug
        )

    async def sell_market(
        self,
        client: AsyncClient,
        ticker: str,
        qty: int,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.sell(
            client, ORDER_TYPE.MARKET, ticker, qty, 0, sleep, debug
        )

    async def sell_limit(
        self,
        client: AsyncClient,
        ticker: str,
        qty: int,
        price: int,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.sell(
            client, ORDER_TYPE.LIMIT, ticker, qty, price, sleep, debug
        )

    async def cancel(
        self,
        client: AsyncClient,
        origin: Order,
        order_type: ORDER_TYPE,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.cancel_or_replace_order(
            client, Cancel(origin, order_type), sleep, debug
        )

    async def cancel_market(
        self,
        client: AsyncClient,
        origin: Order,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.cancel(
            client, origin, ORDER_TYPE.MARKET, sleep, debug
        )

    async def cancel_limit(
        self,
        client: AsyncClient,
        origin: Order,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.cancel(
            client, origin, ORDER_TYPE.LIMIT, sleep, debug
        )

    async def replace(
        self,
        client: AsyncClient,
        origin: Order,
        order_type: ORDER_TYPE,
        price: int,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.cancel_or_replace_order(
            client, Replace(origin, order_type, price), sleep, debug
        )

    async def replace_market(
        self,
        client: AsyncClient,
        origin: Order,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.replace(
            client, origin, ORDER_TYPE.MARKET, 0, sleep, debug
        )

    async def replace_limit(
        self,
        client: AsyncClient,
        origin: Order,
        price: int,
        sleep: float,
        debug: bool,
    ) -> Order:
        return await self.replace(
            client, origin, ORDER_TYPE.LIMIT, price, sleep, debug
        )

    async def all_orders(
        self,
        client: AsyncClient,
        yyyymmdd: str,
        tr_cont: str,
        ctx_area_fk100: str,
        ctx_area_nk100: str,
        sleep: float,
        debug: bool,
    ) -> tuple[list[Any], str, str, str]:
        tr_id = "TTTC8001R"
        url_path = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
        data = {
            "CANO": self.settings.kis_account_cano_domestic_stock,
            "ACNT_PRDT_CD": self.settings.kis_account_prdt_domestic_stock,
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
            **self.common.headers4(),
            "tr_id": tr_id,
            "tr_cont": tr_cont,
        }
        rheaders, rdata = await get(
            client, url_path, headers, data, sleep, debug
        )
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

    async def loop_all_orders(
        self,
        client: AsyncClient,
        yyyymmdd: str,
        sleep: float,
        debug: bool,
    ) -> list[Any]:
        tr_cont = ""
        ctx_area_fk100 = ""
        ctx_area_nk100 = ""
        outlist: list[Any] = []
        while True:
            (
                out0,
                tr_cont,
                ctx_area_fk100,
                ctx_area_nk100,
            ) = await self.all_orders(
                client,
                yyyymmdd,
                tr_cont,
                ctx_area_fk100,
                ctx_area_nk100,
                sleep,
                debug,
            )
            outlist = outlist + out0
            if not tr_cont:
                return outlist

    async def limitorderbook(
        self,
        client: AsyncClient,
        ticker: str,
        sleep: float,
        debug: bool,
    ) -> dict[str, Any]:
        tr_id = "FHKST01010200"
        url_path = (
            "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"
        )
        data = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": ticker,
        }
        headers = {
            **self.common.headers4(),
            "tr_id": tr_id,
        }
        rheaders, rdata = await get(
            client, url_path, headers, data, sleep, debug
        )
        if not rdata or rdata["rt_cd"] != "0":
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, rheaders, rdata)
            )
            return {}
        return dict(rdata["output1"])

    def ws_senddata(self, subscribe: bool, tr_id: str, tr_key: str) -> str:
        if subscribe:
            tr_type = "1"
        else:
            tr_type = "2"
        return (
            '{"header":{"appkey":"'
            + self.settings.kis_app_key
            + '","appsecret":"'
            + self.settings.kis_app_secret
            + '","custtype":"'
            + self.settings.kis_account_custtype
            + '","tr_type":"'
            + tr_type
            + '","content-type":"utf-8"},"body":{"input":{"tr_id":"'
            + tr_id
            + '","tr_key":"'
            + tr_key
            + '"}}}'
        )

    def ws_senddata_trade(self, ticker: str, subscribe: bool = True) -> str:
        return self.ws_senddata(subscribe, "H0STCNT0", ticker)

    def ws_senddata_orderbook(
        self, ticker: str, subscribe: bool = True
    ) -> str:
        return self.ws_senddata(subscribe, "H0STASP0", ticker)

    def ws_senddata_execution(self, subscribe: bool = True) -> str:
        return self.ws_senddata(
            subscribe, "H0STCNI0", self.settings.kis_account_htsid
        )
