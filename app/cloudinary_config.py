import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def upload_photo(file: bytes, folder: str = "contacts") -> tuple[str, str]:
    """
    Upload a photo to Cloudinary
    Returns: tuple of (photo_url, public_id)
    """
    try:
        upload_result = cloudinary.uploader.upload(
            file, folder=folder, resource_type="auto"
        )
        return upload_result["secure_url"], upload_result["public_id"]
    except Exception as e:
        raise Exception(f"Failed to upload photo: {str(e)}")
