# -*- coding: utf-8 -*-

# bilili 平台配置

# 每天爬取视频/帖子的数量控制
MAX_NOTES_PER_DAY = 1

# 指定B站视频URL列表 (支持完整URL或BV号)
# 示例:
# - 完整URL: "https://www.bilibili.com/video/BV1dwuKzmE26/?spm_id_from=333.1387.homepage.video_card.click"
# - BV号: "BV1d54y1g7db"
BILI_SPECIFIED_ID_LIST = [
    "https://www.bilibili.com/video/BV1dwuKzmE26/?spm_id_from=333.1387.homepage.video_card.click",
    "BV1Sz4y1U77N",
    "BV14Q4y1n7jz",
    # ........................
]

# 指定B站创作者URL列表 (支持完整URL或UID)
# 示例:
# - 完整URL: "https://space.bilibili.com/434377496?spm_id_from=333.1007.0.0"
# - UID: "20813884"
BILI_CREATOR_ID_LIST = [
    "https://space.bilibili.com/434377496?spm_id_from=333.1007.0.0",
    "20813884",
    # ........................
]

# 指定时间范围
START_DAY = "2024-01-01"
END_DAY = "2024-01-01"

# 搜索模式
BILI_SEARCH_MODE = "normal"

# 视频清晰度（qn）配置，常见取值：
# 16=360p, 32=480p, 64=720p, 80=1080p, 112=1080p高码率, 116=1080p60, 120=4K
# 注意：更高清晰度需要账号/视频本身支持
BILI_QN = 80

# 是否爬取用户信息
CREATOR_MODE = True

# 开始爬取用户信息页码
START_CONTACTS_PAGE = 1

# 单个视频/帖子最大爬取评论数
CRAWLER_MAX_CONTACTS_COUNT_SINGLENOTES = 100

# 单个视频/帖子最大爬取动态数
CRAWLER_MAX_DYNAMICS_COUNT_SINGLENOTES = 50
