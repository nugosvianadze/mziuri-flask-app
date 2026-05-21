from sqlalchemy import Table, Column, ForeignKey, String
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
    # body: long text content
    # status: str (draft, published)
    # views_count: int default 0
    # likes_count: int default 0
    # published_at: datetime
    # created_at / updated_at: timestamps

    user: Mapped["User"] = relationship(back_populates="posts")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title
        }