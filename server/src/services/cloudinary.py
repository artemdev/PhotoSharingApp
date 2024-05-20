import cloudinary
import cloudinary.uploader
import cloudinary.api
from server.src.conf.config import config

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True
)


def upload_picture(file):
    response = cloudinary.uploader.upload(file)
    return response['url']


def transform_picture(url, transformations):
    return cloudinary.CloudinaryImage(url).build_url(**transformations)
