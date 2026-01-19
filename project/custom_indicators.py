"""
Custom Indicators Example

This file demonstrates how to create custom indicators using the Indicators utility class.
Users can compose multiple indicators together using the Indicators.build_xxx() methods.

Example Usage:
    import polars as pl
    from proalgotrader_core.indicators.indicators import Indicators
    from proalgotrader_core.indicators.indicator import Indicator

    class MyCustomIndicator(Indicator):
        def build(self) -> pl.Expr:
            # Combine RSI and SMA
            rsi_value = Indicators.build_rsi(pl.col("close"), 14)
            return Indicators.build_sma(rsi_value, timeperiod=20)
"""

import polars as pl
from proalgotrader_core.indicators.indicators import Indicators
from proalgotrader_core.indicators.indicator import Indicator
from typing import List, Optional


class MyCustomIndicator(Indicator):
    """
    Custom MACD indicator implementation.

    This demonstrates how to use the Indicators utility class
    to compose and build custom indicators.
    """

    def __init__(
        self,
        fastperiod: int = 12,
        slowperiod: int = 26,
        signalperiod: int = 9,
        output_columns: Optional[List[str]] = None,
    ):
        super().__init__()
        self.fastperiod = fastperiod
        self.slowperiod = slowperiod
        self.signalperiod = signalperiod
        self.output_columns_list = output_columns or ["custom_macd", "custom_macd_signal", "custom_macd_hist"]

    def build(self) -> pl.Expr:
        """Build custom MACD using Indicators utility class."""
        return Indicators.build_macd(
            pl.col("close"),
            fastperiod=self.fastperiod,
            slowperiod=self.slowperiod,
            signalperiod=self.signalperiod,
        )

    def _exprs(self) -> List[pl.Expr]:
        """Return list of expressions."""
        struct_expr = self.build()
        return [
            struct_expr.struct.field("macd").alias(self.output_columns_list[0]),
            struct_expr.struct.field("macdsignal").alias(self.output_columns_list[1]),
            struct_expr.struct.field("macdhist").alias(self.output_columns_list[2]),
        ]

    def output_columns(self) -> List[str]:
        """Return output column names."""
        return self.output_columns_list

    def required_columns(self) -> List[str]:
        """Return required input columns."""
        return ["close"]

    def validate_output_columns(self) -> None:
        """Validate output columns."""
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 3:
                raise ValueError(
                    "MyCustomIndicator expects exactly 3 output column names"
                )
            if not all(isinstance(name, str) and name for name in self._requested_output_columns):
                raise ValueError("All output column names must be non-empty strings")
            self.output_columns_list = self._requested_output_columns

    def window_size(self) -> int:
        """Return the window size needed for the indicator."""
        return self.slowperiod

    def warmup_size(self) -> int:
        """Return the warmup size needed for stable output."""
        return self.slowperiod * 3


class RSISMA(Indicator):
    """
    Custom indicator: SMA of RSI.

    This demonstrates composition of multiple indicators using
    the Indicators utility class.
    """

    def __init__(
        self,
        rsi_period: int = 14,
        sma_period: int = 20,
        column: str = "close",
        output_columns: Optional[List[str]] = None,
    ):
        super().__init__()
        self.rsi_period = rsi_period
        self.sma_period = sma_period
        self.column = column
        self.output_column = f"rsi_sma_{rsi_period}_{sma_period}_{column}"
        self._requested_output_columns = output_columns

    def build(self) -> pl.Expr:
        """Build RSI SMA by composing RSI and SMA."""
        rsi_value = Indicators.build_rsi(pl.col(self.column), self.rsi_period)
        return Indicators.build_sma(rsi_value, timeperiod=self.sma_period)

    def _exprs(self) -> List[pl.Expr]:
        """Return list of expressions."""
        return [self.build().alias(self.output_column)]

    def output_columns(self) -> List[str]:
        """Return output column names."""
        return [self.output_column]

    def required_columns(self) -> List[str]:
        """Return required input columns."""
        return [self.column]

    def validate_output_columns(self) -> None:
        """Validate output columns."""
        if self._requested_output_columns is not None:
            if len(self._requested_output_columns) != 1:
                raise ValueError("RSISMA expects exactly 1 output column name")
            requested = self._requested_output_columns[0]
            if not isinstance(requested, str) or not requested:
                raise ValueError("RSISMA requires a non-empty output column name")
            self.output_column = requested

    def window_size(self) -> int:
        """Return the window size needed for the indicator."""
        return self.sma_period

    def warmup_size(self) -> int:
        """Return the warmup size needed for stable output."""
        return max(self.rsi_period, self.sma_period) * 3
