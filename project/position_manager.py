"""
Position Manager for SMA Crossover Strategy
"""

from proalgotrader_core.protocols.algorithm import AlgorithmProtocol
from proalgotrader_core.protocols.position_manager import PositionManagerProtocol


class PositionManager(PositionManagerProtocol):
    """Single Position Manager - Manages all positions globally based on net PnL."""

    def __init__(self, algorithm: AlgorithmProtocol) -> None:
        self.algorithm = algorithm

    async def initialize(self) -> None:
        """Initialize the position manager."""
        pass

    async def next(self) -> None:
        """Called on every algorithm iteration - check net PnL and exit if needed."""
        # Check net PnL and exit all positions if conditions are met
        if self.algorithm.unrealized_pnl.profit >= 1000:
            print("Net profit target reached - exiting all positions")
            await self.algorithm.exit_all_positions()
        elif self.algorithm.unrealized_pnl.loss >= 500:
            print("Net loss limit reached - exiting all positions")
            await self.algorithm.exit_all_positions()
