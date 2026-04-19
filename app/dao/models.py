from app.dao.database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import BigInteger, String

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]