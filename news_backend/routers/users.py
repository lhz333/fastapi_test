from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse
from crud import users
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["user"])

@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db),):
  existing_user = await users.get_user_by_username(db, user_data.username)
  if existing_user:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

  user = await users.create_user(db, user_data)

  token = await users.create_token(db, user.id)

  # return {
  #   "code": 200,
  #   "message": "注册成功",
  #   "data": {
  #     "token": token,
  #     "userInfo": user
  #   }
  # }
  res_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
  return success_response(message="注册成功!", data=res_data)