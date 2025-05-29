

class MyRect:

    @staticmethod
    def contain(r1, r2):

        # r1 是否包含r2
        # 模糊边界, 解决表格中的字符区域超出表格边界的问题
        bound = 1

        return r1['x0'] <= r2['x0'] + 1 and \
            r1['top'] <= r2['top'] + 1 and \
            r1['x1'] >= r2['x1'] - 1 and \
            r1['bottom'] >= r2['bottom'] - 1

    @staticmethod
    def intersection(r1, r2):

        # r1和r2 是否有交集, 判断r2的左上和右下是否有一个在r1中
        return r1['x0'] <= r2['x0'] <= r1['x1'] and r1['top'] <= r2['top'] <= r1['bottom'] or \
            r1['x0'] <= r2['x1'] <= r1['x1'] and r1['top'] <= r2['bottom'] <= r1['bottom']

    @staticmethod
    def merge(r1, r2):

        # 两个区域合并为一个大区域
        return {
            'x0': r1['x0'] if r1['x0'] < r2['x0'] else r2['x0'],
            'top': r1['top'] if r1['top'] < r2['top'] else r2['top'],
            'x1': r1['x1'] if r1['x1'] > r2['x1'] else r2['x1'],
            'bottom': r1['bottom'] if r1['bottom'] > r2['bottom'] else r2['bottom']
        }

    @staticmethod
    def near(r1, r2):

        # 目前只考虑上下挨的近
        x0, x1, top, bottom = r1['x0'], r1['x1'], r1['top'], r1['bottom']
        x0_, x1_, top_, bottom_ = r2['x0'], r2['x1'], r2['top'], r2['bottom']

        # r1 在上, r2 在下
        if bottom < top_ and top_ - bottom < 2:
            return True

        # r2 在上， r1 在下
        if bottom_ < top and top - bottom_ < 2:
            return True

        return False

    @staticmethod
    def same_line(last_line, this_line):

        top, bottom = last_line['top'], last_line['bottom']
        top_, bottom_ = this_line['top'], this_line['bottom']

        if top_ <= (top + bottom) / 2 <= bottom_:
            return True

        if top <= (top_ + bottom_) / 2 <= bottom:
            return True

        return False

    @staticmethod
    def comp_area(item):

        # 返回直接用于比较的区域
        return [
            item['x0'],
            item['top'],
            item['x1'],
            item['bottom']
        ]

    @staticmethod
    def info_area(area, type='text'):

        # 包括图片和文本
        a = {
            'x0': area['x0'],
            'x1': area['x1'],
            'top': area['top'],
            'bottom': area['bottom'],
            'type': type
        }

        if 'text' in area.keys():
            a['text'] = area['text']

        return a

    @staticmethod
    def table_area(t):

        return {
            'x0': t.bbox[0],
            'top': t.bbox[1],
            'x1': t.bbox[2],
            'bottom': t.bbox[3],
            'type': 'table'
        }

