
from src.tools.MyCmd import MyCmd
from src.tools.MyPath import MyPath
import logging
import os

class FileTrans:

    # 各种转换工具对比: https://blog.csdn.net/lly1122334/article/details/122620790

    @staticmethod
    def docx2pdf(docx, pdf_dir, dst_ext='pdf'):

        """ 可行
        1. 下载安装：https://www.libreoffice.org/download/download-libreoffice/?type=mac-aarch64&version=7.6.4&lang=zh-CN
        2. https://gist.github.com/pankaj28843/3ad78df6290b5ba931c1

        sudo curl https://gist.githubusercontent.com/pankaj28843/3ad78df6290b5ba931c1/raw/soffice.sh
        sudo chmod +x soffice
        cd /Applications/LibreOffice.app/Contents/
        cp 政务智能助手测评报告-北京市人民政府门户网.docx a.docx
        soffice --headless --convert-to pdf:"calc_pdf_Export" a.docx
        """
        ret = docx

        try:

            ext = MyPath().ext(docx)

            if ext in ['.docx', '.doc', '.wps']:

                # outdir = MyPath().path(docx)
                # cmd = f'soffice --headless --convert-to pdf:"calc_pdf_Export" {docx} --outdir {outdir}'
                # cmd = f'soffice --headless --convert-to pdf {docx} --outdir {outdir}'

                code = MyCmd.run(docx, pdf_dir, dst_ext=dst_ext)

                if code == 0:
                    ret = MyPath().change_ext(docx, 'pdf')

                # logging.info(f'{docx} to pdf return {code}, new file: {ret}')

        except Exception as e:
            logging.error(e)

        finally:
            return ret

    @staticmethod
    def doc2txt(doc, txt_dir, biz_id):

        """ 可行
        1. 下载安装：https://www.libreoffice.org/download/download-libreoffice/?type=mac-aarch64&version=7.6.4&lang=zh-CN
        2. https://gist.github.com/pankaj28843/3ad78df6290b5ba931c1

        sudo curl https://gist.githubusercontent.com/pankaj28843/3ad78df6290b5ba931c1/raw/soffice.sh
        sudo chmod +x soffice
        cd /Applications/LibreOffice.app/Contents/
        cp 政务智能助手测评报告-北京市人民政府门户网.docx a.docx
        soffice --headless --convert-to pdf:"calc_pdf_Export" a.docx
        """

        code = -1
        try:

            code = MyCmd.run(doc, txt_dir, dst_ext='txt')

            if code == 0:
                logging.info(f'{txt_dir}/{biz_id}.txt ok')

            else:
                logging.warning(f'{txt_dir}/{biz_id}.txt failed')

        except Exception as e:
            logging.error(e)

        finally:
            return code
