from fastapi import APIRouter, UploadFile

from src.services.imgages import ImageService

router = APIRouter(prefix="/images", tags=["images"])


@router.post("")
def upload_file(file: UploadFile):
    ImageService().upload_file(file)
