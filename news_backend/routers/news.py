from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news
from utils.orm import to_dict

# 创建APIRouter实例
router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/categories")
async def categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    categories = await news.get_news_category(db, skip, limit)
    return {
        "code": 200,
        "message": "success",
        "data": categories,
    }


@router.get("/list")
async def new_list(
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10,le=100, alias="pageSize"),
        db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    news_list = await news.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    has_more = (offset + len(news_list)) < total
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more,
        }
    }

@router.get("/detail")
async def news_detail(id: int = Query(...), db: AsyncSession = Depends(get_db)):
    info = await news.get_news_detail(db, id)
    if not info:
        raise HTTPException(status_code=404, detail="Not Found")

    await news.increase_news_views(db, id)

    related_news = await news.get_related_news(db, id, info.category_id)

    data = to_dict(info) | {"relatedNews": [to_dict(r) for r in related_news]}

    return {
        "code": 200,
        "message": "success",
        "data": data
    }
