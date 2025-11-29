"""Optimization strategies module."""

from src.analyzers.strategies.deductions_strategy import DeductionsStrategy
from src.analyzers.strategies.fcpi_fip_strategy import FCPIFIPStrategy
from src.analyzers.strategies.girardin_strategy import GirardinStrategy
from src.analyzers.strategies.lmnp_strategy import LMNPStrategy
from src.analyzers.strategies.per_strategy import PERStrategy
from src.analyzers.strategies.regime_strategy import RegimeStrategy
from src.analyzers.strategies.structure_strategy import StructureStrategy

__all__ = [
    "DeductionsStrategy",
    "FCPIFIPStrategy",
    "GirardinStrategy",
    "LMNPStrategy",
    "PERStrategy",
    "RegimeStrategy",
    "StructureStrategy",
]
