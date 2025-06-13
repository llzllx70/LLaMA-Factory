from minio import Minio
from minio.error import S3Error
from src.config.edubrainOAConf import EduBrainOAConf

class MyMinIO:

    def __init__(self, bucket, **kwargs):

        self.bucket = bucket
        self.client = Minio(**kwargs)

        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload(self, file_path):

        # 上传到 MinIO 后的对象名称
        object_name = file_path

        # 上传文件
        try:
            self.client.fput_object(self.bucket, object_name, file_path)
            print(f"'{file_path}' 已成功上传至存储桶 '{self.bucket}'")

            url = self.client.presigned_get_object(self.bucket, object_name)
            print(f"文件的外部访问 URL: {url}")

        except S3Error as e:
            print(f"上传文件失败: {e}")

    def download(self, src, dst):

        # key = '001-20220217115024755.png'
        # filename = f'download_{key}'

        try:
            # result = self.client.get_object_to_file(src, dst)

            result = self.client.fget_object(self.bucket, src, dst)

            print(result)
            return True

        except Exception as e:
            print(e)
            return None

    def get_url(self, path):

        try:

            stat = self.client.stat_object(self.bucket, path)

            url = self.client.presigned_get_object(self.bucket, path)
            print(f"文件的外部访问 URL: {url}")

            return url

        except Exception as e:
            return None


if __name__ == '__main__':

    conf = EduBrainOAConf.minio

    my_minio = MyMinIO(conf['bucket'], **conf['link'])

    my_minio.get_url('data/doc测试.doc')
    my_minio.upload('data/doc测试.pdf')
    my_minio.upload('data/wps测试.wps')
