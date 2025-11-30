from typing import TypedDict, NotRequired

class StockAnalysisState(TypedDict):
    ticker: str
    stock_info: NotRequired[str]
    news_summary: NotRequired[str]
    analysis: NotRequired[str]
    recommendation: NotRequired[str]