from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, NewsList


# 获取新闻分类
async def get_news_category(db: AsyncSession ,skip: int = 0, limit: int = 10):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# 获取分类下的新闻列表
async def get_news_list(db: AsyncSession,category_id: int, skip: int =0, limit: int = 10):
    stmt = select(NewsList).where(NewsList.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# 获取分类下新闻总数
async def get_news_count(db: AsyncSession,category_id: int):
    stmt = select(func.count(NewsList.id)).where(NewsList.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one() # 只能有一个结果
    # return result.scalars().one()

# 获取新闻详情
async def get_news_detail(db: AsyncSession, id: int):
    stmt = select(NewsList).where(NewsList.id == id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# 更新新闻浏览量
async def increase_news_views(db: AsyncSession, id: int):
    stmt = update(NewsList).where(NewsList.id == id).values(views=NewsList.views + 1)
    await db.execute(stmt)
    await db.commit()

# 获取相关新闻
async def get_related_news(db: AsyncSession, id: int, category_id: int, limit: int = 5):
    # 查询同一分类下的新闻数据，限制5条，按照浏览量和发布时间排序
    stmt = select(NewsList).where(NewsList.category_id == category_id, NewsList.id != id).order_by(NewsList.views.desc(),NewsList.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()