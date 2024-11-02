import os
from dotenv import load_dotenv
import boto3

load_dotenv()

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID_STUDENT')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY_STUDENT')
aws_endpoint_url = 'https://storage.yandexcloud.net/'
aws_bucket_name = os.getenv('STUDENT_S3_BUCKET')

session = boto3.session.Session()
s3_client = session.client(
    service_name='s3',
    endpoint_url=aws_endpoint_url,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

def download_from_s3(filename):
    """
    Загружает в текущий каталог файлы из облачного хранилища
    """
    local_path = f'./{filename}'

    if os.path.exists(local_path):
        print(f"{filename} already exists, skipping download.")
        return

    try:
        s3_client.download_file(aws_bucket_name, f'recsys/data/{filename}', local_path)
        print(f"Downloaded {filename}")
    except Exception as error:
        print(f"Error downloading {filename}: {error}")

if __name__ == "__main__":
    files_to_download = ["recommendations.parquet", "similar.parquet", "top_popular.parquet"]

    for filename in files_to_download:
        download_from_s3(filename)

    s3_client.close()
