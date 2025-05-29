from src.tools.MyStr import MyStr
from src.tools.MyList import MyList


class BaseTable:

    def valid_table_row(self, row):

        for c in row:
            if c not in ['', ' ', None]:
                return True

        return False

    def append_head_2_value(self, info):

        head = [MyStr.to_plain(str(i)) for i in info[0]]
        a = []

        for row in info[1:]:

            if self.valid_table_row(row):

                r = []
                for i, c in enumerate(row):
                    r.append(f'{head[i]}: {MyStr.to_plain(str(c))}')

                a.append(', '.join(r))

        return a

    def table_2_str(self, info):

        try:
            a = self.append_head_2_value(info)

            if not a:
                return MyList.concat_ll(info)

            return '\n'.join(a)

        except Exception as e:

            return MyList.concat_ll(info)
