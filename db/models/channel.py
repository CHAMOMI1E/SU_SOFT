from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class Channel(Base):
    __tablename__ = "channel"

    username: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("link.id", ondelete="CASCADE"))


class Link(Base):
    __tablename__ = "link"

    url: Mapped[str] = mapped_column(unique=True)
