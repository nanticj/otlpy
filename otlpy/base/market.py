import datetime
from enum import Enum, auto
from typing import Optional

from tompy.stdlib import Datetime


class MARKET_TYPE(Enum):
    LIT_POOL = auto()
    DARK_POOL = auto()


class MARKET_EXECUTION(Enum):
    PRICE_TIME_PRIORITY = auto()
    PRO_RATA = auto()


class ORDER_SIDE(Enum):
    BUY = auto()
    SELL = auto()


class ORDER_TYPE(Enum):
    LIMIT = auto()
    MARKET = auto()


class BaseOrder:
    def __init__(
        self,
        oside: ORDER_SIDE,
        otype: ORDER_TYPE,
        ticker: str,
        qty: float,
        price: float,
    ) -> None:
        self.__oside = oside
        self.__otype = otype
        self.__ticker = ticker
        self.__qty = qty
        self.__price = price
        self.__updated_at = Datetime.now()

    @property
    def oside(self) -> ORDER_SIDE:
        return self.__oside

    @property
    def otype(self) -> ORDER_TYPE:
        return self.__otype

    @property
    def ticker(self) -> str:
        return self.__ticker

    @property
    def qty(self) -> float:
        return self.__qty

    @property
    def price(self) -> float:
        return self.__price

    @property
    def updated_at(self) -> datetime.datetime:
        return self.__updated_at


class PQN:
    def __init__(
        self,
        price: float,
        qty: float,
        num: Optional[int] = None,
    ) -> None:
        self.__price = price
        self.__qty = qty
        self.__num = num

    @property
    def price(self) -> float:
        return self.__price

    @property
    def qty(self) -> float:
        return self.__qty

    @property
    def num(self) -> Optional[int]:
        return self.__num


class LimitOrderBook:
    def __init__(
        self,
        stime: str,
        ticker: str,
        bid: list[PQN],
        ask: list[PQN],
    ) -> None:
        self.__stime = stime
        self.__ticker = ticker
        self.__bid = bid
        self.__ask = ask
        self.__updated_at = Datetime.now()

    @property
    def stime(self) -> str:
        return self.__stime

    @property
    def ticker(self) -> str:
        return self.__ticker

    @property
    def bid(self) -> list[PQN]:
        return self.__bid

    @property
    def ask(self) -> list[PQN]:
        return self.__ask

    @property
    def updated_at(self) -> datetime.datetime:
        return self.__updated_at


class Price:
    def __init__(
        self,
        stime: str,
        ticker: str,
        trade: PQN,
        bid: Optional[PQN],
        ask: Optional[PQN],
    ) -> None:
        self.__stime = stime
        self.__ticker = ticker
        self.__trade = trade
        self.__bid = bid
        self.__ask = ask
        self.__updated_at = Datetime.now()

    @property
    def stime(self) -> str:
        return self.__stime

    @property
    def ticker(self) -> str:
        return self.__ticker

    @property
    def trade(self) -> PQN:
        return self.__trade

    @property
    def bid(self) -> Optional[PQN]:
        return self.__bid

    @property
    def ask(self) -> Optional[PQN]:
        return self.__ask

    @property
    def updated_at(self) -> datetime.datetime:
        return self.__updated_at
