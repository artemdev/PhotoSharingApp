from src.conf.config import config
from fastapi import HTTPException, UploadFile, status, Depends
from cloudinary.uploader import upload
import cloudinary
from src.database.models import Picture

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET
)


async def upload_image(image: UploadFile, current_user: dict = Depends(get_current_user)):
    try:
        upload_result = upload(image.file)
        file_url = upload_result['secure_url']
        picture = Picture()
        return file_url
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading images: {e}")
