from django.conf import settings
from minio import Minio, S3Error
from rest_framework import status
from rest_framework.response import Response


def add_image(map_obj, image):
    try:
        minio_client = Minio(
            settings.MINIO_STORAGE_ENDPOINT,
            access_key=settings.MINIO_STORAGE_ACCESS_KEY,
            secret_key=settings.MINIO_STORAGE_SECRET_KEY,
            secure=False
        )
        bucket_name = settings.MINIO_STORAGE_BUCKET_NAME
        file_name = f"{map_obj.id}/{image.name}"

        minio_client.put_object(bucket_name, file_name, image, len(image))
        map_obj.image_url = f"http://{settings.MINIO_STORAGE_ENDPOINT}/{bucket_name}/{file_name}"
        map_obj.save()

        return Response({'message': 'Image uploaded successfully'}, status=status.HTTP_200_OK)
    except S3Error as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
