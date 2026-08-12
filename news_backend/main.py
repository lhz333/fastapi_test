from fastapi import FastAPI
from routers import news
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["*"])


@app.get("/")
async def root():
    return {"message": "Hello World666"}

# 注册新闻模块路由
app.include_router(news.router)
