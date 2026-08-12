from fastapi import FastAPI
from routers import news

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World666"}

# 注册新闻模块路由
app.include_router(news.router)
