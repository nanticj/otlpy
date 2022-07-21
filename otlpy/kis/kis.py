from otlpy.kis.common import Common
from otlpy.kis.domestic_stock import DomesticStock
from otlpy.kis.settings import Settings


class KIS:
    def __init__(self, settings: Settings) -> None:
        self.__common = Common(settings)
        self.__domestic_stock = DomesticStock(self.common)

    @property
    def common(self) -> Common:
        return self.__common

    @property
    def domestic_stock(self) -> DomesticStock:
        return self.__domestic_stock
