from typing import Any, Optional

import numpy as np
from loguru import logger
from tompy.stdlib import Datetime

from otlpy.base import market


class Order(market.BaseOrder):
    def __init__(
        self,
        oside: market.ORDER_SIDE,
        otype: market.ORDER_TYPE,
        ticker: str,
        qty: float,
        price: float,
    ) -> None:
        super().__init__(ticker, oside, otype, qty, price)
        self.rdata: dict[str, Any] = {}
        self.uid = ""
        self.filled: float = 0
        self.filled_price: float = 0
        self.opened: float = 0

    def filled_event(
        self,
        filled: float,
        filled_price: float,
        opened: Optional[float],
    ) -> None:
        assert 0 <= filled <= self.opened, f"{filled} {self.opened}"
        if opened is None:
            opened = filled
        assert 0 <= opened <= self.opened, f"{opened} {self.opened}"
        if filled > 0:
            total_filled = self.filled + filled
            self.filled_price = (
                self.filled * self.filled_price + filled * filled_price
            ) / total_filled
            self.filled = total_filled
        if opened > 0:
            self.opened -= opened

    def filled_total(
        self,
        total_filled: float,
        total_filled_price: float,
        total_opened: float,
    ) -> tuple[float, float, float]:
        assert total_filled >= self.filled, f"{total_filled} {self.filled}"
        assert self.opened >= total_opened, f"{self.opened} {total_opened}"
        filled = total_filled - self.filled
        if filled > 0:
            filled_price = (
                total_filled * total_filled_price
                - self.filled * self.filled_price
            ) / filled
        else:
            filled_price = 0
        opened = self.opened - total_opened
        self.filled_event(filled, filled_price, opened)
        return filled, filled_price, opened


class Buy(Order):
    def __init__(
        self,
        otype: market.ORDER_TYPE,
        ticker: str,
        qty: float,
        price: float,
    ) -> None:
        super().__init__(
            market.ORDER_SIDE.BUY,
            otype,
            ticker,
            qty,
            price,
        )


class Sell(Order):
    def __init__(
        self,
        otype: market.ORDER_TYPE,
        ticker: str,
        qty: float,
        price: float,
    ) -> None:
        super().__init__(
            market.ORDER_SIDE.SELL,
            otype,
            ticker,
            qty,
            price,
        )


class Cancel(Order):
    def __init__(
        self,
        origin: Order,
        otype: market.ORDER_TYPE,
    ) -> None:
        super().__init__(
            origin.oside,
            otype,
            origin.ticker,
            origin.qty,
            origin.price,
        )
        self.origin = origin


class Replace(Order):
    def __init__(
        self,
        origin: Order,
        otype: market.ORDER_TYPE,
        price: float,
    ) -> None:
        super().__init__(
            origin.oside,
            otype,
            origin.ticker,
            origin.qty,
            price,
        )
        self.origin = origin


class Inventory:
    def __init__(
        self,
        ticker: str,
        ticksize: float,
        unit: float,
        fee: float,
        fee_rate: float,
    ) -> None:
        assert ticksize > 0 and unit > 0 and fee >= 0 and fee_rate >= 0
        self.ticker = ticker
        self.ticksize = ticksize
        self.unit = unit
        self.fee = fee
        self.fee_rate = fee_rate
        self.orders: dict[str, Order] = {}
        self.realized_pnl: float = 0
        self.realized_fee: float = 0
        self.pos: float = 0
        self.price: float = 0
        self.opened_buy: float = 0
        self.opened_sell: float = 0
        self.timestamp = Datetime.now()

    def bid_adjust(self, price: float) -> float:
        return float(np.floor(price / self.ticksize) * self.ticksize)

    def ask_adjust(self, price: float) -> float:
        return float(np.ceil(price / self.ticksize) * self.ticksize)

    def bid_min(self, bid: float, price: float) -> float:
        return min(bid, self.bid_adjust(price))

    def ask_max(self, ask: float, price: float) -> float:
        return max(ask, self.ask_adjust(price))

    def unrealized_pnl(self, price: float) -> float:
        return (price - self.price) * self.pos * self.unit

    def total_pnl(self, price: float) -> float:
        return (
            self.realized_pnl - self.realized_fee + self.unrealized_pnl(price)
        )

    def add_order(self, order: Order) -> None:
        assert self.ticker == order.ticker, f"{self.ticker} {order.ticker}"
        self.orders[order.uid] = order
        if order.oside == market.ORDER_SIDE.BUY:
            self.opened_buy += order.opened
        elif order.oside == market.ORDER_SIDE.SELL:
            self.opened_sell += order.opened
        else:
            assert False

    def filled_position(
        self,
        pos: float,
        price: float,
    ) -> None:
        if self.pos * pos > 0:
            pp = self.price * self.pos + price * pos
            self.pos += pos
            self.price = pp / self.pos
        elif np.abs(pos) <= np.abs(self.pos):
            self.realized_pnl += (self.price - price) * pos * self.unit
            self.pos += pos
        else:
            self.realized_pnl += (price - self.price) * self.pos * self.unit
            self.price = price
            self.pos += pos
        self.realized_fee += (
            self.fee + price * self.unit * self.fee_rate
        ) * np.abs(pos)
        self.timestamp = Datetime.now()
        ur_pnl = self.unrealized_pnl(price)
        pnl = self.total_pnl(price)
        logger.info(
            f"FIL {pos} {price} "
            f"POS {self.pos} {self.price} "
            f"PNL {pnl} = {self.realized_pnl} - {self.realized_fee} + {ur_pnl}"
        )

    def filled_total(
        self,
        order: Order,
        total_filled: float,
        total_filled_price: float,
        total_opened: float,
    ) -> None:
        filled, filled_price, opened = order.filled_total(
            total_filled,
            total_filled_price,
            total_opened,
        )
        if order.oside == market.ORDER_SIDE.BUY:
            self.opened_buy -= opened
            pos = filled
        elif order.oside == market.ORDER_SIDE.SELL:
            self.opened_sell -= opened
            pos = -filled
        else:
            assert False
        if pos != 0:
            self.filled_position(pos, filled_price)

    def check_validity(self) -> None:
        filled_buy: float = 0
        filled_sell: float = 0
        opened_buy: float = 0
        opened_sell: float = 0
        for order in self.orders.values():
            if order.oside == market.ORDER_SIDE.BUY:
                filled_buy += order.filled
                opened_buy += order.opened
            elif order.oside == market.ORDER_SIDE.SELL:
                filled_sell += order.filled
                opened_sell += order.opened
            else:
                assert False
        assert (
            self.pos == filled_buy - filled_sell
        ), f"{self.pos} {filled_buy} {filled_sell}"
        assert self.opened_buy == opened_buy, f"{self.opened_buy} {opened_buy}"
        assert (
            self.opened_sell == opened_sell
        ), f"{self.opened_sell} {opened_sell}"


class Book:
    def __init__(self) -> None:
        self.ois: dict[str, tuple[Order, Inventory]] = {}

    def add(self, order: Order, inventory: Inventory) -> None:
        if order.uid:
            self.ois[order.uid] = (order, inventory)
            inventory.add_order(order)

    def get(self, uid: str) -> tuple[Optional[Order], Optional[Inventory]]:
        if uid:
            oi = self.ois.get(uid)
            if oi is None:
                return None, None
            return oi
        return None, None
