import json
from pathlib import Path

from api.schemas import FraudScoreRequest

_BASE = Path(__file__).parent.parent / "resources"

with open(_BASE / "normalization.json") as _f:
    _NORM: dict = json.load(_f)

with open(_BASE / "mcc_risk.json") as _f:
    _MCC_RISK: dict[str, float] = json.load(_f)

_MAX_AMOUNT: float = _NORM["max_amount"]
_MAX_INSTALLMENTS: float = _NORM["max_installments"]
_AMOUNT_VS_AVG_RATIO: float = _NORM["amount_vs_avg_ratio"]
_MAX_MINUTES: float = _NORM["max_minutes"]
_MAX_KM: float = _NORM["max_km"]
_MAX_TX_COUNT_24H: float = _NORM["max_tx_count_24h"]
_MAX_MERCHANT_AVG: float = _NORM["max_merchant_avg_amount"]

_MCC_RISK_DEFAULT: float = 0.5


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def vectorize(payload: FraudScoreRequest) -> list[float]:
    tx = payload.transaction
    customer = payload.customer
    merchant = payload.merchant
    terminal = payload.terminal
    last_tx = payload.last_transaction

    # dim 0 — amount
    d0 = _clamp(tx.amount / _MAX_AMOUNT)

    # dim 1 — installments
    d1 = _clamp(tx.installments / _MAX_INSTALLMENTS)

    # dim 2 — amount_vs_avg
    d2 = _clamp((tx.amount / customer.avg_amount) / _AMOUNT_VS_AVG_RATIO)

    # dim 3 — hour_of_day (UTC, 0-23)
    d3 = tx.requested_at.hour / 23

    # dim 4 — day_of_week (Mon=0, Sun=6)
    d4 = tx.requested_at.weekday() / 6

    # dim 5 — minutes_since_last_tx (-1 sentinel when no prior tx)
    if last_tx is None:
        d5: float = -1.0
    else:
        minutes = (tx.requested_at - last_tx.timestamp).total_seconds() / 60.0
        d5 = _clamp(minutes / _MAX_MINUTES)

    # dim 6 — km_from_last_tx (-1 sentinel when no prior tx)
    if last_tx is None:
        d6: float = -1.0
    else:
        d6 = _clamp(last_tx.km_from_current / _MAX_KM)

    # dim 7 — km_from_home
    d7 = _clamp(terminal.km_from_home / _MAX_KM)

    # dim 8 — tx_count_24h
    d8 = _clamp(customer.tx_count_24h / _MAX_TX_COUNT_24H)

    # dim 9 — is_online
    d9 = 1 if terminal.is_online else 0

    # dim 10 — card_present
    d10 = 1 if terminal.card_present else 0

    # dim 11 — unknown_merchant (1 = unknown, 0 = known)
    d11 = 0 if merchant.id in customer.known_merchants else 1

    # dim 12 — mcc_risk
    d12 = _MCC_RISK.get(merchant.mcc, _MCC_RISK_DEFAULT)

    # dim 13 — merchant_avg_amount
    d13 = _clamp(merchant.avg_amount / _MAX_MERCHANT_AVG)

    return [d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13]
