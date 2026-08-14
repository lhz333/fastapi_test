from fastapi import FastAPI
from routers import news, users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源（生产环境请指定具体域名）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World666"}

# 注册新闻模块路由
app.include_router(news.router)
app.include_router(users.router)
