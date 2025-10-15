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

    def check_connection(self):
        """检查连接有效性，失效时自动重连"""
        try:
            # 如果游标不存在则直接重连
            if not self.cursor:
                self._connect()
                return

            # 执行简单查询测试连接
            self.cursor.execute("SELECT 1")
            self.connection.commit()
        except pymssql.DatabaseError:
            # 连接失效，关闭旧连接后重新连接
            self.close()
            self._connect()
        except Exception:
            self.close()
            self._connect()
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def init_table(self):
        create_table_sql = """
        BEGIN TRANSACTION

        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='instagraminf' AND xtype='U')
        BEGIN
            CREATE TABLE [instagraminf] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                instagram_id NVARCHAR(255) NOT NULL UNIQUE,
                instagram_num NVARCHAR(64) NOT NULL,
                created_at DATETIME DEFAULT GETDATE(),
                Types INT NOT NULL
            )
        END

        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        BEGIN
            CREATE TABLE [users] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id NVARCHAR(32) NOT NULL,
                user_name NVARCHAR(64) NOT NULL,
                user_fullname NVARCHAR(MAX) NOT NULL,
                instagram_id NVARCHAR(MAX) NOT NULL,
                instagraminf_id INT NOT NULL,
                created_at DATETIME DEFAULT GETDATE(),
                Types INT NOT NULL,
                FOREIGN KEY (instagraminf_id) REFERENCES instagraminf(id)
            )
        END

        COMMIT TRANSACTION
        """
        try:
            self.cursor.execute(create_table_sql)
            self.connection.commit()
        except pymssql.DatabaseError as e:
            self.connection.rollback()
            raise Exception(f"数据库初始化失败({e})")

    def get_or_create_instagram(self, instagram_id, types):
        """获取或创建instagram记录并返回ID"""
        self.check_connection()
        try:
            # 检查是否存在
            check_sql = "SELECT id FROM instagraminf WHERE instagram_id = %s AND Types = %s"
            self.cursor.execute(check_sql, (instagram_id, types))
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                # 插入新记录
                insert_sql = """
                INSERT INTO instagraminf (instagram_id, instagram_num, created_at, Types)
                VALUES (%s, 0, %s, %s)
                """
                created_at = datetime.now()
                self.cursor.execute(insert_sql, (instagram_id, created_at, types))
                self.connection.commit()

                # 获取新插入的ID
                self.cursor.execute("SELECT @@IDENTITY AS id")
                return self.cursor.fetchone()[0]
        except pymssql.DatabaseError as e:
            raise Exception(f"Instagram记录操作失败({e})")

    def insert_data(self, user_id, user_name, user_fullname, instagram_id, types):
        """插入用户数据"""
        self.check_connection()
        try:
            # 获取或创建Instagram记录
            instagraminf_id = self.get_or_create_instagram(instagram_id, types)

            insert_sql = """
            INSERT INTO users 
                (user_id, user_name, user_fullname, instagram_id, instagraminf_id, created_at, Types)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            created_at = datetime.now()
            self.cursor.execute(insert_sql, (
                user_id,
                user_name,
                user_fullname,
                instagram_id,
                instagraminf_id,
                created_at,
                types
            ))
            self.connection.commit()

            # 更新统计数（+1）
            self.update_instagram_count(instagram_id, types, 1)

        except pymssql.DatabaseError as e:
            raise Exception(f"数据插入失败({e})")

    def update_instagram_count(self, instagram_id, types, increment):
        """更新统计数"""
        self.check_connection()
        update_sql = """
        UPDATE instagraminf 
        SET instagram_num = instagram_num + %s 
        WHERE instagram_id = %s AND Types = %s
        """
        self.cursor.execute(update_sql, (increment, instagram_id, types))
        self.connection.commit()
