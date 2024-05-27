from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from src.routes import users, photos, comments, auth, admin
from src.conf.config import config
import cloudinary

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(users.router, prefix='/api')
app.include_router(photos.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(admin.router, prefix='/api')


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        db=0,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
