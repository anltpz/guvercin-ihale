import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from guvercin.models.base import Base


class AuctionStatus(str, enum.Enum):
    ACTIVE = "active"
    ENDED = "ended"


class Auction(Base):
    __tablename__ = "auctions"

    pigeon_id: Mapped[int] = mapped_column(ForeignKey("pigeons.id"))
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default=AuctionStatus.ACTIVE.value)
    start_time: Mapped[datetime] = mapped_column(DateTime)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    starting_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0"
    )
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    pigeon = relationship("Pigeon", back_populates="auctions")
    seller = relationship("User", back_populates="auctions", foreign_keys=[seller_id])
    winner = relationship("User", foreign_keys=[winner_id])
    bids = relationship("Bid", back_populates="auction", lazy="selectin")
