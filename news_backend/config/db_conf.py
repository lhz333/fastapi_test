from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 数据库URL
DATABASE_URL="mysql+aiomysql://root:mysql666@localhost:3306/news_app?charset=utf8"

# 创建异步引擎
async_engine = create_async_engine(DATABASE_URL, echo=True, pool_size=5, max_overflow=10)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

# 依赖项，用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as db_session:
        try:
            yield db_session
            await db_session.commit()
        except:
            await db_session.rollback()
            raise
        finally:
            await db_session.close()