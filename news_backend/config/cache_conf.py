import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 创建REDIS连接对象
redis_client = redis.Redis(
    host=REDIS_HOST, # Redis服务器的主机地址
    port=REDIS_PORT, # Redis 端口号
    db=REDIS_DB, # Redis 数据库编号 0-15
    decode_responses=True # 是否将字节数据解码为字符串
)