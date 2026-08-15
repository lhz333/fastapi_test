from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud import favorite
from models.users import User
from config.db_conf import get_db
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite",tags=["favorite"])

# 获取收藏状态
@router.get("/check")
async def check(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
    is_favorite = await favorite.is_news_favorite(db,user.id,news_id)
    return success_response(message="获取收藏状态成功", data=FavoriteCheckResponse(isFavorite=is_favorite))

# 添加收藏
@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await favorite.add_favorite(db, user.id, data.news_id)
    return success_response(message="添加收藏成功", data=result)

# 取消收藏
@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await favorite.delete_favorite(db, user.id, news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="取消收藏失败")
    return success_response(message="取消收藏成功")

# 获取收藏列表
@router.get("/list")
async def get_favorite_list(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit
    news_list, total = await favorite.get_favorite_list(db, user.id, offset, limit)

    favorite_list = [{
        **news.__dict__,
        "favorite_id": favorite_id,
        "favorite_time": favorite_time
    } for news, favorite_id, favorite_time in news_list]

    has_more = (offset + len(favorite_list)) < total

    data = FavoriteListResponse(list=favorite_list, total=total, has_more=has_more)

    return success_response(message="获取收藏列表成功", data=data)


# 清空收藏列表
@router.delete("/clear")
async def clear_favorite(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count = await favorite.remove_favorite(db, user.id)
    print(count)
    return success_response(message=f"清空了{count}条收藏记录")