from fastapi import APIRouter, UploadFile, HTTPException, status
from src.repositories.photos import upload_image

router = APIRouter(prefix='/photos', tags=['photos'])


@router.post('/photos/upload')
async def handle_upload(image: UploadFile):
    try:
        url = await upload_image(image)
        return {
            "data": {
                "url": url
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
