import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
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
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    pigeon = relationship("Pigeon", back_populates="auctions")
    seller = relationship("User", back_populates="auctions", foreign_keys=[seller_id])
    winner = relationship("User", foreign_keys=[winner_id])
    bids = relationship("Bid", back_populates="auction", lazy="selectin")
