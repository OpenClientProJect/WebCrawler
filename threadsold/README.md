# Threads数据采集

### 采集说明
根据指定关键词进行搜索
- 采集指定关键词的帖子及发帖用户信息
- 采集发帖用户信息
- 采集发帖用户粉丝用户信息
- 采集帖子评论用户信息

### 目录结构
    threads/
    ├── app/                # 应用目录
    │   ├── __init__.py     # 包声明
    │   ├── config.py       # 配置模块
    │   ├── crawler.py      # 爬虫模块
    │   ├── database.py     # 数据库模块
    │   ├── logger.py       # 日志模块
    │   ├── task.py         # 任务调度模块
    ├── data/               # 数据目录
    │   ├── keywords.csv    # 采集指定关键词的搜索结果
    │   ├── threads.json    # 账号登陆状态数据
    ├── .env                # 配置文件
    ├── main.py             # 主入口
    └── requirements.txt    # 依赖文件

### 部署说明

```shell
# 安装项目依赖
pip install -r requirements.txt

# 安装headless浏览器
playwright install

# 复制配置文件，按需修改.env, 注意：REQUEST_DELAY建议设置为25，即每次请求等待25秒
cp example.env .env

# 运行项目
# 采集关键词的帖子/用户及评论/用户
python main.py --type search
# 采集用户的帖子/评论
python main.py --type userpost
# 采集用户粉丝
python main.py --type follower
```

### 配置说明
具体参考.env文件
