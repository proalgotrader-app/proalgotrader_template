from proalgotrader_core.algorithm import Algorithm
from proalgotrader_core.enums.account_type import AccountType
from proalgotrader_core.enums.market_type import MarketType
from proalgotrader_core.enums.order_type import OrderType
from proalgotrader_core.enums.position_type import PositionType
from proalgotrader_core.enums.product_type import ProductType
from proalgotrader_core.enums.risk_reward_unit import RiskRewardUnit
from proalgotrader_core.enums.symbol_type import SymbolType
from proalgotrader_core.order_item import OrderItem
from proalgotrader_core.protocols.position import PositionProtocol
from proalgotrader_core.risk_reward import Stoploss, Target
from project.signal_manager import SignalManager


class Strategy(Algorithm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.set_account_type(account_type=AccountType.DERIVATIVE_POSITIONAL)

    async def on_position_open(self, position: PositionProtocol) -> None:
        print("on position open", position)

        await self.create_risk_reward(
            position=position,
            stoploss=Stoploss(value=10, trailing_value=5),
            target=Target(value=20),
            unit=RiskRewardUnit.PERCENTAGE,
        )

    async def initialize(self) -> None:
        await self.add_signals(
            signal_manager=SignalManager,
            symbol_names=[SymbolType.Stock.ADANIENT],
        )

    async def next(self) -> None:
        if self.positions:
            return

        next_week_ce_atm_symbol = await self.add_option(
            symbol_name=SymbolType.Index.NIFTY,
            expiry_input=("Weekly", 1),
            option_type="CE",
            strike_price_input=0,
        )

        order_item = OrderItem(
            broker_symbol=next_week_ce_atm_symbol,
            market_type=MarketType.Derivative,
            product_type=ProductType.NRML,
            order_type=OrderType.MARKET_ORDER,
            position_type=PositionType.BUY,
            quantities=self.lot_to_quantities(next_week_ce_atm_symbol, 1),
        )

        await self.create_order(order_item=order_item)
