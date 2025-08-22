from datetime import timedelta

from proalgotrader_core.algorithm import Algorithm
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.indicators import Indicators
from proalgotrader_core.protocols.enums.account_type import AccountType
from proalgotrader_core.protocols.enums.symbol_type import SymbolType
from proalgotrader_core.protocols.strategy import StrategyProtocol

from project.position_manager import PositionManager


class Strategy(StrategyProtocol):
    def __init__(self, algorithm: Algorithm) -> None:
        self.algorithm = algorithm

        self.algorithm.set_account_type(account_type=AccountType.DERIVATIVE_INTRADAY)

        self.algorithm.set_interval(interval=timedelta(seconds=1))

        self.algorithm.set_position_manager(position_manager=PositionManager)

    async def initialize(self) -> None:
        self.nifty_equity = await self.algorithm.add_equity(
            symbol_type=SymbolType.Index.NIFTY
        )

        self.nifty_equity_chart = await self.algorithm.add_chart(
            broker_symbol=self.nifty_equity, timeframe=timedelta(minutes=5)
        )

    async def get_sma_20(self):
        return await self.nifty_equity_chart.add_indicator(
            "get_sma_20",
            Indicators.Overlap.SMA(period=20),
        )

    async def get_sma_50(self):
        return await self.nifty_equity_chart.add_indicator(
            "get_sma_50",
            Indicators.Overlap.SMA(period=50),
        )

    async def ce_symbol(self) -> BrokerSymbol:
        return await self.algorithm.add_option(
            symbol_type=SymbolType.Index.NIFTY,
            expiry_input=("Weekly", 0),
            strike_price_input=+2,
            option_type="CE",
        )

    async def pe_symbol(self) -> BrokerSymbol:
        return await self.algorithm.add_option(
            symbol_type=SymbolType.Index.NIFTY,
            expiry_input=("Weekly", 0),
            strike_price_input=+2,
            option_type="PE",
        )

    async def next(self) -> None:
        # Do not enter new trades if already in a position
        if self.algorithm.open_positions:
            return

        sma_20 = await self.get_sma_20()
        sma_50 = await self.get_sma_50()

        # 0 = current candle, -1 = previous candle
        sma20_curr = await sma_20.get_data(0, "sma_20_close")
        sma50_curr = await sma_50.get_data(0, "sma_50_close")
        sma20_prev = await sma_20.get_data(-1, "sma_20_close")
        sma50_prev = await sma_50.get_data(-1, "sma_50_close")

        # Crossovers: only act when the relationship changes this bar
        golden_cross = sma20_prev <= sma50_prev and sma20_curr > sma50_curr
        death_cross = sma20_prev >= sma50_prev and sma20_curr < sma50_curr

        if golden_cross:
            ce = await self.ce_symbol()
            await self.algorithm.buy(broker_symbol=ce, quantities=50)

        if death_cross:
            pe = await self.pe_symbol()
            await self.algorithm.buy(broker_symbol=pe, quantities=50)
