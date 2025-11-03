# database_manager.py
import re
from typing import List, Optional

import pyodbc


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

    def insert_supportUser(self, userData: any) -> bool:
        try:
            print('接收的数据', userData)

            # 如果userData为空或None，直接返回
            if not userData:
                print("没有数据需要插入")
                return False

            conn = self.get_connection()
            cursor = conn.cursor()

            # 批量插入数据
            inserted_count = 0
            for item in userData:
                if isinstance(item, tuple) and len(item) >= 3:
                    userid, username, supportid = item
                    
                    # 检查是否已存在相同的记录
                    cursor.execute("SELECT COUNT(*) FROM SupportUser_copy1 WHERE userid = ? AND Supportid = ?", 
                                   userid, supportid)
                    if cursor.fetchone()[0] == 0:
                        # 不存在相同记录，执行插入
                        query = """
                        INSERT INTO SupportUser_copy1 (userid, username, Supportid)
                        VALUES (?, ?, ?)
                        """
                        cursor.execute(query, userid, username, supportid)
                        inserted_count += 1
                        print(f"插入用户: {username} (ID: {userid})")
                    else:
                        print(f"用户 {username} 已存在，跳过插入")

            conn.commit()
            print(f"成功插入 {inserted_count} 条用户数据")
            return inserted_count
            
        except Exception as e:
            print(f"插入数据失败: {e}")
            if 'conn' in locals():
                try:
                    conn.rollback()
                except:
                    pass
            return False

    ##插入贴文info
    def insert_post_info(self, post_info: any) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 使用 UPSERT 操作（如果记录存在则更新，否则插入）
            cursor.execute(
                """
                IF EXISTS (SELECT 1 FROM SupportInf_copy1 WHERE Supportid = ?)
                    UPDATE SupportInf_copy1 
                    SET number = number + ?, SupportName = ?
                    WHERE Supportid = ?
                ELSE
                    INSERT INTO SupportInf_copy1 (Supportid, SupportName, number)
                    VALUES (?, ?, ?)
                """,
                post_info['Supportid'], 
                post_info['number'], 
                post_info['SupportName'], 
                post_info['Supportid'],
                post_info['Supportid'], 
                post_info['SupportName'], 
                post_info['number']
            )
            conn.commit()
            print(f"成功插入或更新贴文 {post_info['SupportName']} 数据成功")
            return True
        except Exception as e:
            print(f"插入数据失败: {e}")
            if 'conn' in locals():
                try:
                    conn.rollback()
                except:
                    pass
            return False

    def insert_societies_user_batch(self, data):
        """批量插入社团用户数据"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 使用executemany批量插入数据
            cursor.executemany(
                "INSERT INTO societiesUser (userid, username, societiesid) VALUES (?, ?, ?)",
                data
            )
            conn.commit()
            print(f"成功插入 {len(data)} 条社团用户数据")
            return True
        except Exception as e:
            print(f"插入社团用户数据时出错: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def insert_fans_user_batch(self, data):
        """批量插入粉丝用户数据"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 使用executemany批量插入数据
            cursor.executemany(
                "INSERT INTO FansUser (userid, username, societiesid) VALUES (?, ?, ?)",
                data
            )
            conn.commit()
            print(f"成功插入 {len(data)} 条粉丝用户数据")
            return True
        except Exception as e:
            print(f"插入粉丝用户数据时出错: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()


    def insert_societies_inf(self, societiesid, societiesname, number, getnum):
        """插入社团信息到 societiesInf 表"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO societiesInf (societiesid, societiesname, number, getnum) VALUES (?, ?, ?, ?)",
                societiesid, societiesname, number, getnum
            )
            conn.commit()
            print(f"成功插入社团信息: {societiesid} - {societiesname}")
            return True
        except Exception as e:
            print(f"插入社团信息失败: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()


    def insert_fans_inf(self, userid, fansname, number, getnum):
        """插入粉丝专页信息到 FansInf 表"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO FansInf (userid, fansname, number, getnum) VALUES (?, ?, ?, ?)",
                userid, fansname, number, getnum
            )
            conn.commit()
            print(f"成功插入粉丝专页信息: {userid} - {fansname}")
            return True
        except Exception as e:
            print(f"插入粉丝专页信息失败: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def update_updata_table(self, device_name, updatanumber, uptime):
        """
        更新 upData 表
        使用 MERGE 语句，如果同一天有同一个设备，则更新数量（累加），否则插入新记录

        参数:
            device_name: 设备名称
            updatanumber: 更新数据数量
            uptime: 更新时间
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                MERGE INTO upData AS target
                USING (VALUES (?, ?, ?)) AS source(deviceName, updatanumber, uptime)
                ON target.deviceName = source.deviceName AND CAST(target.uptime AS DATE) = CAST(source.uptime AS DATE)
                WHEN MATCHED THEN
                    UPDATE SET target.updatanumber = target.updatanumber + source.updatanumber,
                               target.uptime = source.uptime
                WHEN NOT MATCHED THEN
                    INSERT (deviceName, updatanumber, uptime)
                    VALUES (source.deviceName, source.updatanumber, source.uptime);
            """, device_name, updatanumber, uptime)

            conn.commit()
            print(f"成功更新 upData 表: {device_name} - {updatanumber} - {uptime}")
            return True
        except Exception as e:
            print(f"更新 upData 表失败: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
# 创建全局实例
db_manager = DatabaseManager()