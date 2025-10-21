# database_manager.py
import pyodbc
import re
from typing import List, Optional
from urllib.parse import urlparse


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化数据库连接"""
        self.connection_string = (
            r"Driver={SQL Server};"
            r"Server=dbs.kydb.vip;"
            r"Database=FbSocietiesUser;"
            r"UID=sa;"
            r"PWD=Yunsin@#861123823_shp4;"
            r"timeout=35;"
        )
        self._connection = None

    def get_connection(self):
        """获取数据库连接"""
        if self._connection is None:
            try:
                self._connection = pyodbc.connect(self.connection_string)
            except Exception as e:
                print(f"数据库连接失败: {e}")
                raise
        return self._connection

    def close_connection(self):
        """关闭数据库连接"""
        if self._connection:
            self._connection.close()
            self._connection = None

    def extract_group_id_from_url(self, url: str) -> Optional[str]:
        """从Facebook群组URL中提取群组ID"""
        try:
            # 移除查询参数
            clean_url = url.split('?')[0]

            # 匹配多种可能的群组URL格式
            patterns = [
                r'https?://(?:www\.)?facebook\.com/groups/([^/?]+)/?',
                r'/groups/([^/?]+)/?',
            ]

            for pattern in patterns:
                match = re.search(pattern, clean_url)
                if match:
                    return match.group(1)

            return None
        except Exception as e:
            print(f"提取群组ID时出错: {e}")
            return None

    def get_existing_societies_ids(self) -> List[str]:
        """获取所有已存在的 societiesid"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT societiesid FROM societiesInf")
            existing_ids = [str(row[0]).strip() for row in cursor.fetchall()]
            return existing_ids
        except Exception as e:
            print(f"查询数据库失败: {e}")
            raise

    def check_duplicate_addresses(self, urls: List[str]) -> dict:
        """
        检查地址是否重复
        返回: {'duplicate': 重复地址列表, 'unique': 唯一地址列表, 'failed_to_parse': 解析失败的地址列表}
        """
        try:
            existing_ids = self.get_existing_societies_ids()

            duplicate_urls = []
            unique_urls = []
            failed_urls = []

            for url in urls:
                group_id = self.extract_group_id_from_url(url)

                if not group_id:
                    failed_urls.append(url)
                    continue

                if group_id in existing_ids:
                    duplicate_urls.append(url)
                else:
                    unique_urls.append(url)

            return {
                'duplicate': duplicate_urls,
                'unique': unique_urls,
                'failed': failed_urls
            }
        except Exception as e:
            print(f"检查重复地址失败: {e}")
            # 如果检查失败，将所有地址视为唯一
            return {
                'duplicate': [],
                'unique': urls,
                'failed': []
            }

    def insert_societies_info(self, url: str, societies_name: str, member_count: str) -> bool:
        """插入新的社团信息"""
        try:
            group_id = self.extract_group_id_from_url(url)
            if not group_id:
                print(f"无法从URL提取群组ID: {url}")
                return False

            conn = self.get_connection()
            cursor = conn.cursor()

            # 检查是否已存在（双重保险）
            cursor.execute("SELECT COUNT(*) FROM societiesInf WHERE societiesid = ?", group_id)
            if cursor.fetchone()[0] > 0:
                print(f"群组ID已存在: {group_id}")
                return False

            # 插入新记录
            query = """
            INSERT INTO societiesInf (societiesid, societiesname, member_count, crawl_time) 
            VALUES (?, ?, ?, GETDATE())
            """

            cursor.execute(query, group_id, societies_name, member_count)
            conn.commit()
            print(f"成功插入社团信息: {group_id} - {societies_name}")
            return True
        except Exception as e:
            print(f"插入数据失败: {e}")
            if conn:
                conn.rollback()
            return False


# 创建全局实例
db_manager = DatabaseManager()