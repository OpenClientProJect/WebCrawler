import pymssql
from datetime import datetime
from threadsold.app.config import DB_HOST, DB_DATABASE, DB_USER, DB_PASSWORD

class Database:
    def __init__(self):
        self.server = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_DATABASE
        self.connection = None
        self.cursor = None
        self._connect()

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

    def init(self):
        create_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        BEGIN
            CREATE TABLE [users] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id NVARCHAR(64) NOT NULL,
                name NVARCHAR(64),
                full_name NVARCHAR(MAX),
                bio NVARCHAR(MAX),
                picture_url NVARCHAR(MAX),
                follower_count INT,
                following_count INT,
                created_at DATETIME DEFAULT GETDATE()
            )
        END

        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='posts' AND xtype='U')
        BEGIN
            CREATE TABLE [posts] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id NVARCHAR(64) NOT NULL,
                post_id NVARCHAR(64) NOT NULL,
                like_count INT,
                mention_count INT,
                quote_count INT,
                permalink NVARCHAR(MAX),
                taken_at DATETIME,
                text NVARCHAR(MAX),
                images NVARCHAR(MAX),
                video NVARCHAR(MAX),
                reply_count INT,
                repost_count INT,
                reshare_count INT,
                created_at DATETIME DEFAULT GETDATE()
            )
        END

        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='comments' AND xtype='U')
        BEGIN
            CREATE TABLE [comments] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id NVARCHAR(64) NOT NULL,
                post_id NVARCHAR(64) NOT NULL,
                comment_id NVARCHAR(64) NOT NULL,
                taken_at DATETIME,
                like_count INT,
                reply_count INT,
                text NVARCHAR(MAX),
                images NVARCHAR(MAX),
                video NVARCHAR(MAX),
                repost_count INT,
                reshare_count INT,
                created_at DATETIME DEFAULT GETDATE()
            )
        END

        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='user_followers' AND xtype='U')
        BEGIN
            CREATE TABLE [user_followers] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id NVARCHAR(64) NOT NULL,
                follower_user_id NVARCHAR(64) NOT NULL,
                created_at DATETIME DEFAULT GETDATE()
            )
        END
        """
        try:
            self.cursor.execute(create_table_sql)
            self.connection.commit()
        except pymssql.DatabaseError as e:
            raise Exception(f"数据库初始化失败({e})")

    def get_all_users(self):
        query = "SELECT id, user_id, name, full_name, bio, picture_url, follower_count, following_count, created_at FROM [users]"
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            columns = [col[0] for col in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except pymssql.DatabaseError as e:
            raise Exception(f"[Table:users] 获取所有用户失败({e})")
        
    def user_exists(self, user_id):
        check_sql = "SELECT 1 FROM [users] WHERE user_id = %s"
        try:
            self.cursor.execute(check_sql, (user_id,))
            result = self.cursor.fetchone()
            return result is not None
        except pymssql.DatabaseError as e:
            raise Exception(f"[Table:users] 检查用户是否存在失败({e})")
        
    def post_exists(self, post_id):
        check_sql = "SELECT 1 FROM [posts] WHERE post_id = %s"
        try:
            self.cursor.execute(check_sql, (post_id,))
            result = self.cursor.fetchone()
            return result is not None
        except pymssql.DatabaseError as e:
            raise Exception(f"[Table:posts] 检查帖子是否存在失败({e})")
        
    def comment_exists(self, comment_id):
        check_sql = "SELECT 1 FROM [comments] WHERE comment_id = %s"
        try:
            self.cursor.execute(check_sql, (comment_id,))
            result = self.cursor.fetchone()
            return result is not None
        except pymssql.DatabaseError as e:
            raise Exception(f"[Table:comments] 检查评论是否存在失败({e})")
        
    def follower_exists(self, user_id, follower_user_id):
        check_sql = "SELECT 1 FROM [user_followers] WHERE user_id = %s and follower_user_id = %s"
        try:
            self.cursor.execute(check_sql, (user_id, follower_user_id,))
            result = self.cursor.fetchone()
            return result is not None
        except pymssql.DatabaseError as e:
            raise Exception(f"[Table:user_followers] 检查粉丝是否存在失败({e})")
        
    def insert_user(self, user_id, name, full_name, bio, picture_url, follower_count, following_count):
        insert_sql = """
        INSERT INTO [users] (user_id, name, full_name, bio, picture_url, follower_count, following_count, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        created_at = datetime.now()
        try:
            self.cursor.execute(insert_sql, (user_id, name, full_name, bio, picture_url, follower_count, following_count, created_at))
            self.connection.commit()
        except pymssql.DatabaseError as e:
            raise Exception(f"[Table:users]数据插入失败({e})")
        
    def insert_post(self, user_id, post_id, text, images, video, like_count, mention_count, quote_count, reply_count, repost_count, reshare_count, permalink, taken_at):
        insert_sql = """
        INSERT INTO [posts] (user_id, post_id, text, images, video, like_count, mention_count, quote_count, reply_count, repost_count, reshare_count, permalink, taken_at, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        created_at = datetime.now()
        try:
            self.cursor.execute(insert_sql, (user_id, post_id, text, images, video, like_count, mention_count, quote_count, reply_count, repost_count, reshare_count, permalink, taken_at, created_at))
            self.connection.commit()
        except pymssql.DatabaseError as e:
            raise Exception(f"[Table:posts]数据插入失败({e})")
        
    def insert_comment(self, user_id, post_id, comment_id, text, images, video, like_count, reply_count, repost_count, reshare_count, taken_at):
        insert_sql = """
        INSERT INTO [comments] (user_id, post_id, comment_id, text, images, video, like_count, reply_count, repost_count, reshare_count, taken_at, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        created_at = datetime.now()
        try:
            self.cursor.execute(insert_sql, (user_id, post_id, comment_id, text, images, video, like_count, reply_count, repost_count, reshare_count, taken_at, created_at))
            self.connection.commit()
        except pymssql.DatabaseError as e:
            raise Exception(f"[Table:comments]数据插入失败({e})")
        
    def insert_follower(self, user_id, follower_user_id):
        insert_sql = """
        INSERT INTO [user_followers] (user_id, follower_user_id)
        VALUES (%s, %s)
        """
        created_at = datetime.now()
        try:
            self.cursor.execute(insert_sql, (user_id, follower_user_id, created_at))
            self.connection.commit()
        except pymssql.DatabaseError as e:
            raise Exception(f"[Table:user_followers]数据插入失败({e})")
