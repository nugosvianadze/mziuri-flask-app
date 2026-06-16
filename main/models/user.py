from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin

from extensions import Base, db


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    email: Mapped[str | None]
    password: Mapped[str | None]
    age: Mapped[int]
    # Suggested fields for full implementation:
    # username: unique, display name
    # avatar_url: profile image
    # bio: short profile text
    # created_at / updated_at: timestamps

    posts: Mapped[list["Posts"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    profile: Mapped["Profile"] = relationship(
        back_populates="user",
        uselist=False
    )

    @property
    def username(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "id": self.id,
            "email": self.email,
        }

    def to_dict_with_posts(self):
        data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "posts": [post.to_dict() for post in self.posts]
        }
        return data