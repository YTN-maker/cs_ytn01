import sqlite3


class SQLite3Helper:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)  # 连接到数据库（如果不存在则创建）
        self.cursor = self.conn.cursor()  # 创建游标对象

    def execute_sql(self, sql, params=None):
        """执行SQL语句"""
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            self.conn.commit()
            return self.cursor.rowcount  # 返回受影响的总行数
        except sqlite3.Error as e:
            self.conn.rollback()  # 发生错误时回滚
            raise e

    def execute_many_sql(self, sql, params_list):
        """批量执行SQL语句"""
        try:
            self.cursor.executemany(sql, params_list)
            self.conn.commit()
            return self.cursor.rowcount  # 返回受影响的总行数
        except sqlite3.Error as e:
            self.conn.rollback()  # 发生错误时回滚
            raise e

    def close_db(self):
        """关闭数据库连接"""
        try:
            self.cursor.close()
            self.conn.close()
        except:
            pass  # 如果已经关闭，忽略错误

    def insert_data(self, table_name, data):
        """插入单条数据"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql_clause = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        affected_rows = self.execute_sql(sql_clause, tuple(data.values()))
        return affected_rows

    def insert_many(self, table_name, data_list):
        """批量插入数据"""
        if not data_list:
            return
        # 检查所有字典是否有相同的键
        first_keys = set(data_list[0].keys())
        for i, data in enumerate(data_list[1:], start=1):
            current_keys = set(data.keys())
            if current_keys != first_keys:
                raise ValueError(f"第{i + 1}个数据的键与前一个不同: {current_keys} != {first_keys}")

        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['?'] * len(data_list[0]))
        sql_clause = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        # 准备参数列表
        params_list = [tuple(data.values()) for data in data_list]
        affected_rows = self.execute_many_sql(sql_clause, params_list)
        return affected_rows

    def update_data(self, table_name, data, condition):
        """更新数据"""
        columns = ', '.join([f"{column} = ?" for column in data.keys()])
        sql_clause = f"UPDATE {table_name} SET {columns} WHERE {condition}"
        affected_rows = self.execute_sql(sql_clause, tuple(data.values()))
        return affected_rows

    def delete_data(self, table_name, condition):
        """删除数据"""
        sql_clause = f"DELETE FROM {table_name} WHERE {condition}"
        affected_rows = self.execute_sql(sql_clause)
        return affected_rows

    def select_data(self, table_name, condition=None):
        """查询数据"""
        if condition is None:
            sql_clause = f"SELECT * FROM {table_name}"
        else:
            sql_clause = f"SELECT * FROM {table_name} WHERE {condition}"
        self.execute_sql(sql_clause)
        data = self.cursor.fetchall()
        if data:
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in data]
        return []


sqldb = SQLite3Helper('mydatabase.db')
# sqldb.insert_data('users', {'id': '2', 'name': 'eeeee'})
# a = sqldb.insert_many('users', [{'id': '4', 'name': 'eeeee'},{'id': '5', 'name': 'cccc'}])
# a = sqldb.select_data('users')
a = sqldb.update_data('users', {'name': '你好'}, 'name = "cccc"')
print(a)
sqldb.close_db()
