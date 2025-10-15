### 目录结构
    crawler/
    ├── config/             # 项目配置
    │   ├── config.json     # 配置文件
    ├── cookies/            # 账号登录状态
    │   ├── instagram.json  # IG账号登录状态
    ├── data/               # 采集目标数据文件
    │   ├── follower.json   # 采集账号粉丝的作者主页URL
    │   ├── keyword.json    # 采集指定用户列表的关键词
    │   ├── post.json       # 采集指定作品(文章/Reels)点赞/评论用户的作品URL
    ├── database/           # 数据库模块
    │   ├── __init__.py     # 包声明
    │   ├── database.py     # 数据库连接
    ├── logger/             # 日志模块
    │   ├── __init__.py     # 包声明
    │   ├── logger.py       # 格式化日志
    ├── scraper/            # 爬虫模块
    │   ├── __init__.py     # 包声明
    │   ├── instagram.py    # Instagram 登录和数据爬取逻辑
    │   ├── tasks.py        # 任务调度逻辑
    ├── main.py             # 主入口
    └── requirements.txt    # 依赖文件

### 部署说明

```shell
# 安装项目依赖
pip install -r requirements.txt

# 安装headless浏览器
playwright install

# 运行项目
python main.py
```

### 配置说明
```json
{
    "account": {
        "username": "IG账号",
        "password": "IG密码"
    },
    "database": {
        "host": "数据地址(TCP/IP)",
        "name": "数据库名称",
        "username": "数据库用户名",
        "password": "数据库密码"
    },
    "crawler": {
        "delay": 15, // 每次爬取暂停时间（单位：秒），建议15秒，太小容易封号
        "proxy": "http://127.0.0.1:10809" // 代理服务器地址
    }
}
```
