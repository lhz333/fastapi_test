from sqlalchemy import Select, Delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import NewsList
# 获取新闻收藏状态
async def is_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
) -> bool:
    query = Select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    # 是否有收藏记录
    return result.scalar_one_or_none() is not None

# 添加收藏
async def add_favorite(db: AsyncSession, user_id: int, news_id: int) -> None:
    favorite = Favorite(news_id=news_id, user_id=user_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

# 取消收藏
async def delete_favorite(db: AsyncSession, user_id: int, news_id: int) -> None:
    stmt = Delete(Favorite).where(Favorite.news_id == news_id, Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# 获取收藏列表
async def get_favorite_list(db: AsyncSession, user_id: int, skip: int, limit: int):
    total_query = Select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    total_result = await db.execute(total_query)
    total_count = total_result.scalar_one()

    sql = (
            Select(NewsList, Favorite.id.label("favorite_id"), Favorite.created_at.label("favorite_time"))
           .join(Favorite, Favorite.news_id == NewsList.id)
           .where(Favorite.user_id == user_id)
           .order_by(Favorite.created_at.desc())
           .offset(skip)
           .limit(limit)
    )
    result = await db.execute(sql)
    news_list = result.all()

    return news_list, total_count


# 清空用户下的收藏列表
async def remove_favorite(db: AsyncSession, user_id: int):
    sql = Delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(sql)
    await db.commit()
    return result.rowcount or 0

