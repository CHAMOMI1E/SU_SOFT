from sqlalchemy.orm import Mapped, mapped_column

from SU_SOFT.db.models.base import Base


class User(Base):
    id_tg: Mapped[int]
    username: Mapped[str]
    status: Mapped[str] = mapped_column(default="None")