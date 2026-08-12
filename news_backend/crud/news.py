from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category

# 获取新闻分类
async def get_news_category(db: AsyncSession ,skip: int = 0, limit: int = 10):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
