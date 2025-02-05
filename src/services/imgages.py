import shutil

from src.services.base import BaseService
from src.tasks.tasks import resize_image


class ImageService(BaseService):
    @staticmethod
    def upload_file(file):
        file_path = f"src/static/images/{file.filename}"
        with open(file_path, "wb+") as new_file:
            shutil.copyfileobj(file.file, new_file)

        resize_image.delay(file_path)
