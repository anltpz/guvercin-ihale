from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from guvercin.models.base import Base


class Pigeon(Base):
    __tablename__ = "pigeons"

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100))
    breed: Mapped[str] = mapped_column(String(100))
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    seller = relationship("User", back_populates="pigeons")
    auctions = relationship("Auction", back_populates="pigeon", lazy="selectin")
