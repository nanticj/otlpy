import datetime
from typing import Any, Optional

import numpy as np
from loguru import logger
from tompy.stdlib import Datetime

from otlpy.base.market import ORDER_SIDE, ORDER_TYPE, BaseOrder


class Order(BaseOrder):
    def __init__(
        self,
        oside: ORDER_SIDE,
        otype: ORDER_TYPE,
        ticker: str,
        qty: float,
        price: float,
    ) -> None:
        super().__init__(oside, otype, ticker, qty, price)
        self.__rdata: dict[str, Any] = {}
        self.__uid = ""
        self.__filled: float = 0
        self.__filled_price: float = 0
        self.__opened: float = 0

    @property
    def rdata(self) -> dict[str, Any]:
        return self.__rdata

    def _set_rdata(self, rdata: dict[str, Any]) -> None:
        self.__rdata = rdata

    @property
    def uid(self) -> str:
        return self.__uid

    def _set_uid(self, uid: str) -> None:
        self.__uid = uid

    @property
    def filled(self) -> float:
        return self.__filled

    def _set_filled(self, filled: float) -> None:
        self.__filled = filled

    @property
    def filled_price(self) -> float:
        return self.__filled_price

    def _set_filled_price(self, filled_price: float) -> None:
        self.__filled_price = filled_price

    @property
    def opened(self) -> float:
        return self.__opened

    def _set_opened(self, opened: float) -> None:
        self.__opened = opened

    def acknowledgment(
        self,
        rdata: dict[str, Any],
        uid: str,
        opened: float,
    ) -> None:
        self._set_rdata(rdata)
        self._set_uid(uid)
        self._set_opened(opened)

    def filled_event(
        self,
        filled: float,
        filled_price: float,
        opened: Optional[float],
    ) -> None:
        if opened is None:
            opened = filled
        assert filled <= self.opened and opened <= self.opened
        if filled > 0:
            total_filled = self.filled + filled
            self._set_filled_price(
                (self.filled * self.filled_price + filled * filled_price)
                / total_filled
            )
            self._set_filled(total_filled)
        if opened > 0:
            self._set_opened(self.opened - opened)

    def filled_total(
        self,
        total_filled: float,
        total_filled_price: float,
        total_opened: float,
    ) -> tuple[float, float, float]:
        assert total_filled >= self.filled and self.opened >= total_opened
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
        otype: ORDER_TYPE,
        ticker: str,
        qty: float,
        price: float,
    ) -> None:
        super().__init__(
            ORDER_SIDE.BUY,
            otype,
            ticker,
            qty,
            price,
        )


class Sell(Order):
    def __init__(
        self,
        otype: ORDER_TYPE,
        ticker: str,
        qty: float,
        price: float,
    ) -> None:
        super().__init__(
            ORDER_SIDE.SELL,
            otype,
            ticker,
            qty,
            price,
        )


class Cancel(Order):
    def __init__(
        self,
        origin: Order,
        otype: ORDER_TYPE,
    ) -> None:
        super().__init__(
            origin.oside,
            otype,
            origin.ticker,
            origin.qty,
            0,
        )
        self.__origin = origin

    @property
    def origin(self) -> Order:
        return self.__origin


class Replace(Order):
    def __init__(
        self,
        origin: Order,
        otype: ORDER_TYPE,
        price: float,
    ) -> None:
        super().__init__(
            origin.oside,
            otype,
            origin.ticker,
            origin.qty,
            price,
        )
        self.__origin = origin

    @property
    def origin(self) -> Order:
        return self.__origin


class Inventory:
    def __init__(
        self,
        name: str,
        ticker: str,
        ticksize: float,
        unit: float,
        fee: float,
        fee_rate: float,
    ) -> None:
        assert (
            ticker and ticksize > 0 and unit > 0 and fee >= 0 and fee_rate >= 0
        )
        self.__name = name
        self.__ticker = ticker
        self.__ticksize = ticksize
        self.__unit = unit
        self.__fee = fee
        self.__fee_rate = fee_rate
        self.__orders: dict[str, Order] = {}
        self.__realized_pnl: float = 0
        self.__realized_fee: float = 0
        self.__pos: float = 0
        self.__price: float = 0
        self.__opened_buy: float = 0
        self.__opened_sell: float = 0
        self.__updated_at = Datetime.now()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def ticker(self) -> str:
        return self.__ticker

    @property
    def ticksize(self) -> float:
        return self.__ticksize

    @property
    def unit(self) -> float:
        return self.__unit

    @property
    def fee(self) -> float:
        return self.__fee

    @property
    def fee_rate(self) -> float:
        return self.__fee_rate

    @property
    def realized_pnl(self) -> float:
        return self.__realized_pnl

    def _add_realized_pnl(self, realized_pnl: float) -> None:
        self.__realized_pnl += realized_pnl

    @property
    def realized_fee(self) -> float:
        return self.__realized_fee

    def _add_realized_fee(self, realized_fee: float) -> None:
        self.__realized_fee += realized_fee

    @property
    def pos(self) -> float:
        return self.__pos

    def _add_pos(self, pos: float) -> None:
        self.__pos += pos

    @property
    def price(self) -> float:
        return self.__price

    def _set_price(self, price: float) -> None:
        self.__price = price

    @property
    def opened_buy(self) -> float:
        return self.__opened_buy

    def _add_opened_buy(self, opened_buy: float) -> None:
        self.__opened_buy += opened_buy

    @property
    def opened_sell(self) -> float:
        return self.__opened_sell

    def _add_opened_sell(self, opened_sell: float) -> None:
        self.__opened_sell += opened_sell

    @property
    def updated_at(self) -> datetime.datetime:
        return self.__updated_at

    def _set_updated_at(self) -> None:
        self.__updated_at = Datetime.now()

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
        assert self.ticker == order.ticker
        assert self.__orders.get(order.uid) is None
        self.__orders[order.uid] = order
        if order.oside == ORDER_SIDE.BUY:
            self._add_opened_buy(order.opened)
        elif order.oside == ORDER_SIDE.SELL:
            self._add_opened_sell(order.opened)
        else:
            assert False

    def filled_position(
        self,
        pos: float,
        price: float,
    ) -> None:
        if self.pos * pos > 0:
            pp = self.price * self.pos + price * pos
            self._add_pos(pos)
            self._set_price(pp / self.pos)
        elif np.abs(pos) <= np.abs(self.pos):
            self._add_realized_pnl((self.price - price) * pos * self.unit)
            self._add_pos(pos)
        else:
            self._add_realized_pnl((price - self.price) * self.pos * self.unit)
            self._set_price(price)
            self._add_pos(pos)
        self._add_realized_fee(
            (self.fee + price * self.unit * self.fee_rate) * np.abs(pos)
        )
        self._set_updated_at()
        ur_pnl = self.unrealized_pnl(price)
        pnl = self.total_pnl(price)
        logger.info(
            f"INV {self.name} "
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
        if order.oside == ORDER_SIDE.BUY:
            self._add_opened_buy(-opened)
            pos = filled
        elif order.oside == ORDER_SIDE.SELL:
            self._add_opened_sell(-opened)
            pos = -filled
        else:
            assert False
        if pos != 0:
            self.filled_position(pos, filled_price)

    def check_validity(self) -> None:
        pos: float = 0
        opened_buy: float = 0
        opened_sell: float = 0
        for order in self.__orders.values():
            if order.oside == ORDER_SIDE.BUY:
                pos += order.filled
                opened_buy += order.opened
            elif order.oside == ORDER_SIDE.SELL:
                pos -= order.filled
                opened_sell += order.opened
            else:
                assert False
        assert self.pos == pos
        assert self.opened_buy == opened_buy
        assert self.opened_sell == opened_sell


class Book:
    def __init__(self) -> None:
        self.__ois: dict[str, tuple[Order, Inventory]] = {}

    def add(self, order: Order, inventory: Inventory) -> None:
        if order.uid:
            assert order.ticker == inventory.ticker
            self.__ois[order.uid] = (order, inventory)
            inventory.add_order(order)

    def get(self, uid: str) -> tuple[Optional[Order], Optional[Inventory]]:
        if uid:
            oi = self.__ois.get(uid)
            if oi is None:
                return None, None
            order, inventory = oi
            assert order.ticker == inventory.ticker
            return order, inventory
        return None, None
