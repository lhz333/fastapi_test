from datetime import datetime

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, Index, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.users import User
from models.news import NewsList

class Base(DeclarativeBase):
    pass

class Favorite(Base):
    """
    收藏表ORM模型
    """
    __tablename__ = "favorite"

    # 创建索引
    __table_args__ = (
        # 唯一约束，同一用户，同一新闻，只能收藏一次
        UniqueConstraint("user_id", "news_id", name="user_news_unique"),
        Index("idx_favorite_user_id", "user_id"),
        Index("idx_favorite_news_id", "news_id")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(NewsList.id), nullable=False,comment="新闻ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="创建时间")

    def __repr__(self):
        return f"<Favorite (id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"