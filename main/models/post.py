from datetime import datetime

from sqlalchemy import Table, Column, ForeignKey, String, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import Base, db


class Posts(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    # Suggested fields for full implementation:
    status: Mapped[str] = mapped_column(String(10), default="draft",
                                        server_default="draft")
    views_count: Mapped[int] = mapped_column(default=0, server_default='0')
    category: Mapped[str | None]
    # likes_count: int default 0
    published_at: Mapped[datetime | None]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Updates automatically every time the record is changed
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now()
    )


    user: Mapped["User"] = relationship(back_populates="posts")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title
        }