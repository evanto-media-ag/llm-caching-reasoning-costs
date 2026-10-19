"""Cost formula of the series (same as CompanyWizard's ModelCostCalculator)."""
from dataclasses import dataclass

from lab.usage import Usage


@dataclass
class Price:
    """Prices per 1M tokens. A missing cache price falls back to the input price."""
    input: float
    output: float
    cache_read: float | None
    cache_write_5m: float | None
    cache_write_1h: float | None
    currency: str


def compute_cost(u: Usage, p: Price) -> float:
    writes = u.cache_write_5m + u.cache_write_1h
    billed_input = max(0, u.input_total - u.cache_read - writes)
    read = p.cache_read if p.cache_read is not None else p.input
    w5m = p.cache_write_5m if p.cache_write_5m is not None else p.input
    # A 1h write without a 1h price is billed at the input price, not the 5 min price.
    w1h = p.cache_write_1h if p.cache_write_1h is not None else p.input
    total = (billed_input * p.input + u.cache_read * read + u.cache_write_5m * w5m
             + u.cache_write_1h * w1h + u.output * p.output)
    return total / 1e6
