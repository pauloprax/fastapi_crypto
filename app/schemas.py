from pydantic import BaseModel


class CoinPairModel(BaseModel):
    symbol: str
    min_price: float | None = None
    max_price: float | None = None
