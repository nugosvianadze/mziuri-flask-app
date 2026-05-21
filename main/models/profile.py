from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)
    # Suggested fields for full implementation:
    # location: string
    # website_url: string
    # socials_json: serialized links

    user: Mapped["User"] = relationship(back_populates="profile")