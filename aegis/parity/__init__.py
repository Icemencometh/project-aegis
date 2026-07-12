"""Parity adapters comparing Aegis behavior to legacy surfaces."""

from .allocation_adapter import AllocationParityAdapter
from .execution_adapter import ExecutionParityAdapter
from .portfolio_adapter import PortfolioParityAdapter
from .regime_adapter import RegimeParityAdapter
from .risk_adapter import RiskParityAdapter
from .scoring_adapter import ScoringParityAdapter

__all__ = [
    "AllocationParityAdapter",
    "ExecutionParityAdapter",
    "PortfolioParityAdapter",
    "RegimeParityAdapter",
    "RiskParityAdapter",
    "ScoringParityAdapter",
]
