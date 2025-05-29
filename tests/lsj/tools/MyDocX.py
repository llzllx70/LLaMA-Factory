import docx

# 主要针对docx类型

class MyDocX:

    @staticmethod
    def doc_2_str(file_, meta_info=None):

        doc = docx.Document(file_)
        doc_str = ''

        for p in doc.paragraphs:

            if meta_info and p.text in meta_info:
                continue

            ll = p.text.split('\n')
            for l in ll:
                if len(l) > 0:
                    doc_str += l.strip() + '\n'

        return doc_str

    def doc_2_str_plain(self, file_):

        doc_str = self.doc_2_str(file_)
        # 去掉转义字符
        return ''.join(str(doc_str).split())

    @staticmethod
    def txt_2_str(file_):

        with open(file_, 'r', encoding='utf-8') as file:
            content = file.read()

            return content



