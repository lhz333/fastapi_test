from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from crud import users
from utils.response import success_response
from utils.auth import get_current_user
from models.users import User

router = APIRouter(prefix="/api/user", tags=["user"])

# 注册
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

# 登录
@router.post("/login")
async def user_login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
  user = await users.verify_user(db, user_data)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

  token = await users.create_token(db, user.id)
  res_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
  return success_response(message="登录成功!", data=res_data)

# 获取用户信息
@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
  return success_response(message="获取用户信息成功啦", data=UserInfoResponse.model_validate(user))

# 更新用户信息
@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
  update_user_info = await users.update_user_info(db, user.username,user_data)
  return success_response(message="修改用户信息成功啦",data=UserInfoResponse.model_validate(update_user_info))

# 更新密码
@router.put("/password")
async def update_password(pwd_data: UserChangePasswordRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
  result = await users.change_password(db, user, pwd_data.old_password, pwd_data.new_password)
  if not result:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="旧密码错误")
  return success_response(message="修改密码成功")
