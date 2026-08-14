import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security

# 通过用户名查询用户信息
async def get_user_by_username(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    hashed_pwd = security.get_hashed_password(user_data.password)
    user = User(username=user_data.username, password=hashed_pwd)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# 生成token
async def create_token(db: AsyncSession, user_id: int):
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token,expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token

# 登录验证用户密码
async def verify_user(db: AsyncSession, user_data: UserRequest):
    user = await get_user_by_username(db, user_data.username)
    if not user:
        return None
    if not security.verify_password(user_data.password, user.password):
        return None
    return user

# 根据token查询用户信息
async def get_user_by_token(db: AsyncSession, token: str):
    stmt = select(UserToken).where(UserToken.token == token)
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now():
        return None

    query = select(User).where(db_token.user_id == User.id)
    res = await db.execute(query)
    return res.scalar_one_or_none()

# 更新用户信息
async def update_user_info(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_none=True,
        exclude_unset=True
    ))
    res = await db.execute(query)
    await db.commit()

    # 检查是否更新了
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # 更新后的用户信息
    update_user = await get_user_by_username(db, username)
    return update_user

# 修改密码
async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    if not security.verify_password(old_password, user.password):
        return False

    pwd = security.get_hashed_password(new_password)
    user.password = pwd
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True