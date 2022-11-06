import dataclasses
from datetime import datetime
from decimal import Decimal


@dataclasses.dataclass
class Transaction:
    timestamp: datetime
    reason: bool  # True - покупка, False - продажа
    count: int
    price: Decimal


Portfolio = dict[str, list[Transaction]]
