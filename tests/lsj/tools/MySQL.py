import pymysql


class MySQL:

    def __init__(self, log, kwargs):
        self.mysql_conn = pymysql.connect(**kwargs)
        self.log = log

    def query(self, cmd, q=True):

        def inner():

            cursor = self.mysql_conn.cursor()
            cursor.execute(cmd)

            self.mysql_conn.commit()

            # if not q:
            #     self.mysql_conn.commit()

            if q:
                ret = cursor.fetchall()
                self.log.info(f'{cmd} return: {ret}')

                return ret

        try:

            return inner()

        except OperationalError as e:

            if e.args[0] in (2006, 2013):  # MySQL server has gone away 或者 Lost connection to MySQL server

                self.log.info("Reconnecting to the database...")
                self.mysql_conn.ping(reconnect=True)  # 重新连接

                return inner()

            else:
                return ()
