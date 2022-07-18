from otlpy.kis.common import Common
from otlpy.kis.domestic_stock import DomesticStock
from otlpy.kis.settings import Settings


class KIS:
    def __init__(self, settings: Settings) -> None:
        self.common = Common(settings)
        self.domestic_stock = DomesticStock(self.common)
