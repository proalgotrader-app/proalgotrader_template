"""
SMA Crossover Strategy - Simple SMA 20 vs SMA 50 crossover for Nifty options
"""

from datetime import timedelta
from typing import Optional

from proalgotrader_core.algorithm import Algorithm
from proalgotrader_core.order_item import OrderItem
from proalgotrader_core.enums.market_type import MarketType
from proalgotrader_core.enums.account_type import AccountType
from proalgotrader_core.enums.order_type import OrderType
from proalgotrader_core.enums.position_type import PositionType
from proalgotrader_core.enums.product_type import ProductType
from proalgotrader_core.enums.symbol_type import SymbolType
from proalgotrader_core.enums.candle_type import CandleType
from proalgotrader_core.indicators.overlap.sma import SMA
from .position_manager import PositionManager


class Strategy(Algorithm):
    """SMA 20 vs SMA 50 crossover strategy for Nifty options trading."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_account_type(account_type=AccountType.DERIVATIVE_POSITIONAL)
        self.set_position_manager(position_manager_class=PositionManager)
        # No interval - check every tick for signals

    async def initialize(self) -> None:
        """Initialize strategy with Nifty chart and SMA indicators."""
        self.nifty_symbol = await self.add_equity(symbol_name=SymbolType.Index.NIFTY)
        self.nifty_chart = await self.add_chart(
            broker_symbol=self.nifty_symbol,
            timeframe=timedelta(minutes=5),
            candle_type=CandleType.REGULAR,
        )

        self.sma_20 = SMA(period=20, column="close")
        self.sma_50 = SMA(period=50, column="close")

        await self.nifty_chart.add_indicator(key="sma_20", indicator=self.sma_20)
        await self.nifty_chart.add_indicator(key="sma_50", indicator=self.sma_50)

    async def next(self) -> None:
        """Main strategy logic - check for SMA crossover signals."""
        # Only check for new signals if no position
        if len(self.pending_orders) > 0 or len(self.positions) > 0:
            return

        signal = await self._get_crossover_signal()

        if signal == "BUY":
            await self._buy_ce_option()
        elif signal == "SELL":
            await self._buy_pe_option()

    async def _get_crossover_signal(self) -> Optional[str]:
        """Get SMA crossover signal."""
        if not self.sma_20 or not self.sma_50:
            return None

        try:
            sma_20_current = await self.sma_20.get_data(0, "sma_20_close")
            sma_50_current = await self.sma_50.get_data(0, "sma_50_close")
            sma_20_prev = await self.sma_20.get_data(-1, "sma_20_close")
            sma_50_prev = await self.sma_50.get_data(-1, "sma_50_close")

            if None in [sma_20_current, sma_50_current, sma_20_prev, sma_50_prev]:
                return None

            # Bullish crossover
            if sma_20_prev <= sma_50_prev and sma_20_current > sma_50_current:
                return "BUY"
            # Bearish crossover
            elif sma_20_prev >= sma_50_prev and sma_20_current < sma_50_current:
                return "SELL"

            return None
        except:
            raise

    async def _buy_ce_option(self) -> None:
        """Buy Nifty CE option."""
        ce_symbol = await self.add_option(
            symbol_name=SymbolType.Index.NIFTY,
            expiry_input=("Weekly", 0),
            option_type="CE",
            strike_price_input=0,
        )

        order_item = OrderItem(
            broker_symbol=ce_symbol,
            market_type=MarketType.Derivative,
            product_type=ProductType.NRML,
            order_type=OrderType.MARKET_ORDER,
            position_type=PositionType.BUY,
            quantities=50,
        )

        await self.create_order(order_item=order_item)

    async def _buy_pe_option(self) -> None:
        """Buy Nifty PE option."""
        pe_symbol = await self.add_option(
            symbol_name=SymbolType.Index.NIFTY,
            expiry_input=("Weekly", 0),
            option_type="PE",
            strike_price_input=0,
        )

        order_item = OrderItem(
            broker_symbol=pe_symbol,
            market_type=MarketType.Derivative,
            product_type=ProductType.NRML,
            order_type=OrderType.MARKET_ORDER,
            position_type=PositionType.BUY,
            quantities=50,
        )

        await self.create_order(order_item=order_item)
