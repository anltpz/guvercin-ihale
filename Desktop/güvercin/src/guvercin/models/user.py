from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from guvercin.models.base import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    roles: Mapped[list] = mapped_column(JSON, default=list, server_default='["buyer"]')

    pigeons = relationship("Pigeon", back_populates="seller", lazy="selectin")
    auctions = relationship(
        "Auction",
        back_populates="seller",
        foreign_keys="Auction.seller_id",
        lazy="selectin",
    )
    bids = relationship("Bid", back_populates="user", lazy="selectin")
