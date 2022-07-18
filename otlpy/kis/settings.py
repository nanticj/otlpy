from typing import Optional

from tompy.settings import BaseSettings


class Settings(BaseSettings):
    kis_app_key: str
    kis_app_secret: str
    kis_account_htsid: str
    kis_account_custtype: str
    kis_account_cano_domestic_stock: Optional[str]
    kis_account_prdt_domestic_stock: Optional[str]
    kis_account_cano_domestic_futureoption: Optional[str]
    kis_account_prdt_domestic_futureoption: Optional[str]
    kis_account_cano_overseas_stock: Optional[str]
    kis_account_prdt_overseas_stock: Optional[str]
