from proalgotrader_core.protocols.algorithm import AlgorithmProtocol
from proalgotrader_core.protocols.position_manager import PositionManagerProtocol


class PositionManager(PositionManagerProtocol):
    """Single Position Manager - Manages all positions globally."""

    def __init__(self, algorithm: AlgorithmProtocol) -> None:
        self.algorithm = algorithm

    async def initialize(self) -> None:
        pass

    async def next(self) -> None:
        # print("net_pnl_profit", self.algorithm.net_pnl.profit)
        # print("net_pnl_loss", self.algorithm.net_pnl.loss)
        # print("unrealized_pnl_profit", self.algorithm.unrealized_pnl.profit)
        # print("unrealized_pnl_loss", self.algorithm.unrealized_pnl.loss)
        # print("\n")

        if (
            self.algorithm.unrealized_pnl.loss >= 500
            or self.algorithm.unrealized_pnl.profit >= 1000
        ):
            await self.algorithm.exit_all_positions()
