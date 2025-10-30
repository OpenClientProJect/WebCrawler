import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from FBmain import Crawler


class TestCrawlerGetSupportId(unittest.TestCase):

    def setUp(self):
        """在每个测试方法之前运行"""
        # 创建Crawler实例
        self.crawler = Crawler(None, {})

    def test_posts_url_parsing(self):
        """测试解析包含/posts/的URL"""
        url = "https://www.facebook.com/groups/739908139519943/posts/2605929742917764/"
        expected = {
            'group_id': '739908139519943',
            'post_id': '2605929742917764',
            'permalink_id': None
        }
        result = self.crawler.get_support_id(url)
        self.assertEqual(result, expected)

    def test_permalink_url_parsing(self):
        """测试解析包含/permalink/的URL"""
        url = "https://m.facebook.com/groups/1589495621275375/permalink/3585049678386616"
        expected = {
            'group_id': '1589495621275375',
            'post_id': None,
            'permalink_id': '3585049678386616'
        }
        result = self.crawler.get_support_id(url)
        self.assertEqual(result, expected)

    def test_multi_permalinks_url_parsing(self):
        """测试解析包含multi_permalinks参数的URL"""
        url = "https://www.facebook.com/groups/1918586732330126/?multi_permalinks=1988963085292490&hoisted_section_header_type=recently_seen"
        expected = {
            'group_id': '1918586732330126',
            'post_id': None,
            'permalink_id': '1988963085292490'
        }
        result = self.crawler.get_support_id(url)
        self.assertEqual(result, expected)

    def test_url_with_multiple_query_params(self):
        """测试解析包含多个查询参数的URL"""
        url = "https://www.facebook.com/groups/123456789/?param1=value1&multi_permalinks=987654321&param2=value2"
        expected = {
            'group_id': '123456789',
            'post_id': None,
            'permalink_id': '987654321'
        }
        result = self.crawler.get_support_id(url)
        self.assertEqual(result, expected)

    def test_malformed_url(self):
        """测试解析格式错误的URL"""
        url = "https://www.example.com/invalid/url"
        expected = {
            'group_id': None,
            'post_id': None,
            'permalink_id': None
        }
        result = self.crawler.get_support_id(url)
        self.assertEqual(result, expected)

    def test_empty_url(self):
        """测试解析空URL"""
        url = ""
        expected = {
            'group_id': None,
            'post_id': None,
            'permalink_id': None
        }
        result = self.crawler.get_support_id(url)
        self.assertEqual(result, expected)

    def test_url_with_exception(self):
        """测试当URL解析出现异常时的处理"""
        # 使用patch模拟urlparse抛出异常的情况
        with patch('FBmain.urlparse', side_effect=Exception("Mocked Exception")):
            url = "https://www.facebook.com/groups/123/posts/456"
            result = self.crawler.get_support_id(url)
            expected = {
                'group_id': None,
                'post_id': None,
                'permalink_id': None
            }
            self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
