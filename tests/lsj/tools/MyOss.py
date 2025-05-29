
import oss2
from oss2.exceptions import OssError


class MyOss:

    def __init__(self, kwargs):

        self.endpoint = kwargs.get('endpoint', 'oss-cn-hangzhou-zjzwy01-d01-a.cloud-inner.zj.gov.cn/')
        self.accessKeyId = kwargs.get('accessKeyId', 'akzLyzovQG7Izm67')
        self.accessKeySecret = kwargs.get('accessKeySecret', 'SnDJ9LAiVREc1Zb4ytXNF1qGCEzwM6')
        self.bucketName = kwargs.get('bucketName', 'jytoaoss')

        self.bucket = oss2.Bucket(
            oss2.Auth(
                self.accessKeyId,
                self.accessKeySecret
            ),
            self.endpoint,
            self.bucketName,
        )

    def download(self, src, dst):

        result = self.bucket.get_object_to_file(src, dst)

        print(result)
        return True

    def get_url(self, path):

        try:

            result = self.bucket.head_object(path)

            # 生成带签名的URL。 指定URL的过期时间（单位为秒）。
            signed_url = self.bucket.sign_url('GET', path, expires=3600)

            # 跨域问题，手动修改，修改后可以下载doc/docx/pdf
            signed_url = signed_url.replace('http://', 'https://')

            print(signed_url)

            return signed_url

        except OssError as e:
            # 如果捕获到异常，说明对象不存在或有其他错误
            if e.status == 404:
                print('Object does not exist.')

            return None

        except Exception as e:
            return None


if __name__ == '__main__':

    from src.config.edubrainOAConf import EduBrainOAConf as oaconf
    myoss = MyOss(oaconf.oss)

    # key = '001-20220217115024755.png'
    # filename = f'download_{key}'

    # myoss.download()
