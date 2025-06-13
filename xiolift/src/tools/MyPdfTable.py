from src.tools.BaseTable import BaseTable

class MyPdfTable(BaseTable):
    """
    pdf 中表格处理
    """

    def __init__(self, box):

        self.width = self.widths(box)
        self.hight = self.hights(box)

    def widths(self, box):

        width = [0] * len(box.rows[0].cells)

        for i, row in enumerate(box.rows):
            for j, cell in enumerate(row.cells):

                if cell is None:
                    continue

                w = cell[2] - cell[0]

                if width[j] == 0:
                    width[j] = w

                elif w < width[j]:
                    width[j] = w

        return width

    def hights(self, box):

        hight = [0] * len(box.rows)

        for i, row in enumerate(box.rows):
            for j, cell in enumerate(row.cells):

                if cell is None:
                    continue

                h = cell[3] - cell[1]

                if hight[i] == 0:
                    hight[i] = h

                elif h < hight[i]:
                    hight[i] = h

        return hight

    def left_is_wide(self, box_row, j):

        # row: 当前行, j: 当前列index
        for idx in range(j-1, -1, -1):

            cell = box_row.cells[idx]

            if cell is None:
                continue

            width = cell[2] - cell[0]

            if width > self.width[idx]:
                return True

        return False

    def top_is_tall(self, all_rows, i, j):

        # row: 当前行, i: 当前行index
        for idx in range(i-1, -1, -1):

            cell = all_rows[idx].cells[j]

            if cell is None:
                continue

            high = cell[3] - cell[1]

            if high > self.hight[idx]:
                return True

        return False

    def replace_none_in_table(self, box, info):

        for i, row in enumerate(info):
            for j, cell in enumerate(row):

                if cell is None:
                    if self.left_is_wide(box.rows[i], j):  # 左边比较宽
                        row[j] = row[j-1]

                    elif self.top_is_tall(box.rows, i, j):
                        row[j] = info[i-1][j]

    def parse(self, box, info):

        self.replace_none_in_table(box=box, info=info)
        return self.table_2_str(info)
