from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CartItem:
    label: str
    category: str
    brand: Optional[str]
    specific: bool  # True = exact brand required, no substitutes. False = generic match is fine.


TEST_ITEMS = [
    CartItem(label="Toilet paper", category="toilet paper", brand="Charmin Ultra Strong", specific=True),
    CartItem(label="Dishwasher tablets", category="dishwasher tablets", brand="Finish Powerball", specific=True),
    CartItem(label="Kitchen towel", category="kitchen towel", brand=None, specific=False),
    CartItem(label="Paper towel", category="paper towel", brand=None, specific=False),
]
