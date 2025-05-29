import os


class MyCmdOld:

    @staticmethod
    def run(cmd, mylog):

        code = 0
        try:
            mylog.info(f'begin run: {cmd}')

            code = os.system(cmd)

            if code == 0:
                mylog.info(f'success: {cmd} return {code}')
            else:
                mylog.warn(f'failed: {cmd} return {code}')

        except:
            code = -1

        finally:
            return code


import subprocess
import logging


class MyCmd:

    @staticmethod
    def run(src, outdir, dst_ext="pdf"):

        # 检查 soffice 是否在路径中
        result = subprocess.run(["which", "soffice"], capture_output=True, text=True)

        if result.returncode != 0:
            logging.info("soffice command not found in PATH.")
        else:
            soffice_path = result.stdout.strip()
            logging.info(f"Found soffice at: {soffice_path}")

            # 使用 soffice 转换文件
            try:
                result = subprocess.run(
                    [soffice_path, "--headless", "--convert-to", dst_ext, src, '--outdir', outdir],
                    check=True,
                    stdout=subprocess.PIPE,
                    timeout=30
                )

                a = result.stdout.decode()

                logging.info(f"Conversion stdout: {a}")

                return 0

            except subprocess.CalledProcessError as e:

                logging.error(f"Conversion failed with error code {e.returncode}: {e.stderr.decode()}")

                return -1

            except subprocess.TimeoutExpired as e:
                
                logging.error(f"Conversion timed out: {e}")

                return -1

            except Exception as e:
                
                logging.error(f"An unexpected error occurred: {e}")

                return -1

    @staticmethod
    def catdoc(doc_path):

        try:
            result = subprocess.run(['catdoc', doc_path], capture_output=True, text=True)
            return result.stdout

        except Exception as e:
            return None

