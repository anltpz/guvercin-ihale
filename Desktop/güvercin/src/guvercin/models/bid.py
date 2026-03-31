from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from guvercin.models.base import Base


class Bid(Base):
    __tablename__ = "bids"

    auction_id: Mapped[int] = mapped_column(ForeignKey("auctions.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    auction = relationship("Auction", back_populates="bids")
    user = relationship("User", back_populates="bids")
