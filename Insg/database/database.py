import pymssql

from datetime import datetime

class Database:
    def __init__(self, server, user, password, database):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self._connect()

        self.progress_callback = None

    def set_progress_callback(self, callback):
        self.progress_callback = callback
    def _connect(self):
        try:
            self.connection = pymssql.connect(self.server, self.user, self.password, self.database)
            self.cursor = self.connection.cursor()
        except pymssql.DatabaseError as e:
            raise Exception(f"数据库连接失败({e})")
        
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def init_table(self):
        create_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        BEGIN
            CREATE TABLE [users] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id NVARCHAR(32) NOT NULL,
                user_name NVARCHAR(32) NOT NULL,
                user_fullname NVARCHAR(32) NOT NULL,
                created_at DATETIME DEFAULT GETDATE()
            )
        END
        """
        try:
            self.cursor.execute(create_table_sql)
            self.connection.commit()
        except pymssql.DatabaseError as e:
            raise Exception(f"数据库初始化失败({e})")
        
    def insert_data(self, user_id, user_name, user_fullname):
        insert_sql = """
        INSERT INTO [users] (user_id, user_name, user_fullname, created_at)
        VALUES (%s, %s, %s, %s)
        """
        created_at = datetime.now()
        try:
            self.cursor.execute(insert_sql, (user_id, user_name, user_fullname, created_at))
            self.connection.commit()
        except pymssql.DatabaseError as e:
            raise Exception(f"数据插入失败({e})")
        if self.progress_callback:
                    self.progress_callback()