from datetime import timedelta

from proalgotrader_core.enums.candle_type import CandleType
from proalgotrader_core.protocols.broker_symbol import BrokerSymbolProtocol
from proalgotrader_core.protocols.signal_manager import SignalManagerProtocol
from proalgotrader_core.algorithm import Algorithm
from proalgotrader_core.indicators import SMA


class SignalManager(SignalManagerProtocol):
    def __init__(
        self, *, algorithm: "Algorithm", broker_symbol: "BrokerSymbolProtocol"
    ) -> None:
        self.algorithm = algorithm
        self.broker_symbol = broker_symbol

    async def initialize(self) -> None:
        # Use daily candles for proper moving average calculation
        self.chart = await self.algorithm.add_chart(
            broker_symbol=self.broker_symbol,
            timeframe=timedelta(days=1),
            candle_type=CandleType.REGULAR,
        )

        # Add 50-day and 200-day SMA indicators for golden crossover
        self.sma_50 = await self.chart.add_indicator(
            key="sma_50", indicator=SMA(period=50)
        )
        self.sma_200 = await self.chart.add_indicator(
            key="sma_200", indicator=SMA(period=200)
        )

    async def next(self) -> None:
        # Get current and previous SMA values
        current_sma_50 = await self.sma_50.get_data(0, "sma_50_close")
        current_sma_200 = await self.sma_200.get_data(0, "sma_200_close")

        # Get previous SMA values for crossover detection
        prev_sma_50 = await self.sma_50.get_data(-1, "sma_50_close")
        prev_sma_200 = await self.sma_200.get_data(-1, "sma_200_close")

        # Check for golden crossover: 50-day SMA crosses above 200-day SMA
        golden_crossover = (
            current_sma_50 > current_sma_200 and prev_sma_50 <= prev_sma_200
        )

        if golden_crossover:
            print(f"🟢 GOLDEN CROSSOVER DETECTED for {self.broker_symbol.symbol_name}")
            print(f"Current SMA 50: {current_sma_50}")
            print(f"Current SMA 200: {current_sma_200}")
            print(f"Previous SMA 50: {prev_sma_50}")
            print(f"Previous SMA 200: {prev_sma_200}")
            print("=" * 50)
