# -*- coding: utf-8 -*-
import base64
import requests
import boto3
from functools import wraps
from io import BytesIO


def retry(retry_times=3):
    """重试函数 用来放在请求中 网络超时的情况"""

    def decorated(func):
        @wraps(func)
        def inner(*args, **kwargs):
            exce = None
            for _ in range(retry_times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    exce = Exception(str(e))
            if exce:
                raise exce

        return inner

    return decorated


class R2Loader:
    def __init__(self, aws_access_key_id, aws_access_secret_key, bucket_name, endpoint_url, domain):
        self.aws_access_key_id = aws_access_key_id
        self.aws_access_secret_key = aws_access_secret_key
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.domain = domain

    @property
    def resource(self):
        return boto3.resource(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_access_secret_key
        )

    @property
    def client(self):
        return boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_access_secret_key
        )

    @retry()
    def _download(self, image_url):
        r = requests.get(image_url, stream=True)
        io = BytesIO()
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                io.write(chunk)
        io.seek(0)
        return io

    @retry()
    def upload(self, image_base64, file_key):
        content = base64.b64decode(image_base64.encode())
        self.resource.Bucket(self.bucket_name).put_object(Key=file_key, Body=content)
        return f"https://{self.domain}/{file_key}"

    def download(self, image_url):
        io = self._download(image_url)
        base64_string = base64.b64encode(io.getbuffer())
        return base64_string.decode()
