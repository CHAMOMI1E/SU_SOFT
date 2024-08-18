from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class Channel(Base):
    username: Mapped[str]
    user_id: Mapped[str] = mapped_column(ForeignKey("Link.id", ondelete="CASCADE"))


class Link(Base):
    url: Mapped[str]
