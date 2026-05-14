from datetime import datetime

import msgspec


class Transaction(msgspec.Struct):
    amount: float
    installments: int
    requested_at: datetime


class Customer(msgspec.Struct):
    avg_amount: float
    tx_count_24h: int
    known_merchants: list[str]


class Merchant(msgspec.Struct):
    id: str
    mcc: str
    avg_amount: float


class Terminal(msgspec.Struct):
    is_online: bool
    card_present: bool
    km_from_home: float


class LastTransaction(msgspec.Struct):
    timestamp: datetime
    km_from_current: float


class FraudScoreRequest(msgspec.Struct):
    id: str
    transaction: Transaction
    customer: Customer
    merchant: Merchant
    terminal: Terminal
    last_transaction: LastTransaction | None


class FraudScoreResponse(msgspec.Struct):
    approved: bool
    fraud_score: float
