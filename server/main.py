from fastapi import FastAPI
import uvicorn
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from src.routes import users, photos, comments

app = FastAPI()

# test3
app.include_router(users.router, prefix='/api')
app.include_router(photos.router, prefix='/api')
app.include_router(comments.router, prefix='/api')


@app.on_event("startup")
async def startup():
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
