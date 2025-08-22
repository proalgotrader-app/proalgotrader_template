from proalgotrader_core.algorithm import Algorithm
from proalgotrader_core.position import Position
from proalgotrader_core.protocols.position_manager import PositionManagerProtocol


class PositionManager(PositionManagerProtocol):
    def __init__(self, algorithm: Algorithm, position: Position) -> None:
        self.algorithm = algorithm
        self.position = position

    async def initialize(self) -> None:
        self.risk_reward = await self.position.get_risk_reward(
            sl=40,
            tgt=120,
            tsl=10,
            on_exit=self.on_exit,
        )

    async def next(self) -> None:
        await self.risk_reward.next()

    async def on_exit(self) -> None:
        await self.position.exit()
