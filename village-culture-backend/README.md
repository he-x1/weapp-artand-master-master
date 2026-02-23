# 乡村文化传播小程序后端系统

## 项目简介
这是一个乡村文化传播微信小程序的后端系统，基于Python Flask框架开发，提供数据爬取、用户管理、互动功能和智能推荐等服务。

## 功能特性
- **数据爬取**: 使用Python爬虫定向爬取乡村文化数据
- **用户管理**: 支持微信登录和手机号登录
- **互动功能**: 点赞、收藏、浏览历史记录
- **智能推荐**: 基于协同过滤和内容特征的混合推荐算法
- **搜索功能**: 支持关键词搜索文化内容

## 技术栈
- **框架**: Flask 2.3.3
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy
- **认证**: JWT
- **爬虫**: Scrapy, BeautifulSoup
- **推荐算法**: 协同过滤 + 内容推荐

## 安装部署

### 1. 环境要求
- Python 3.8+
- MySQL 8.0+
- pip

### 2. 安装依赖

cd village-culture-backend
pip install -r requirements.txt

### 3. 配置数据库

创建MySQL数据库:

mysql -u root -p < init_data.sql

或手动创建:

CREATE DATABASE village_culture CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

修改 `.env` 文件中的数据库配置:

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=village_culture

### 4. 初始化数据

# 初始化示例数据
python scripts/init_sample_data.py

### 5. 启动服务

# 开发模式
python run.py

# 生产模式（带定时任务）
python run_with_scheduler.py

## API接口文档

### 用户相关
- POST /api/user/wx-login - 微信登录
- POST /api/user/login - 手机号登录
- POST /api/user/register - 用户注册
- POST /api/user/send-sms - 发送验证码
- GET /api/user/info - 获取用户信息

### 内容相关
- GET /api/content/banners - 获取轮播图
- GET /api/content/recommend - 获取推荐内容
- GET /api/content/latest - 获取最新内容
- GET /api/content/detail/<id> - 获取内容详情
- GET /api/content/search - 搜索内容
- GET /api/content/categories - 获取分类列表
- GET /api/content/category/<id> - 获取分类内容
- POST /api/content/refresh - 刷新内容数据

### 互动相关
- POST /api/interaction/like - 点赞
- POST /api/interaction/unlike - 取消点赞
- POST /api/interaction/collect - 收藏
- POST /api/interaction/uncollect - 取消收藏
- GET /api/interaction/likes - 获取点赞列表
- GET /api/interaction/collects - 获取收藏列表
- GET /api/interaction/history - 获取浏览历史
- POST /api/interaction/add-history - 记录浏览历史
- GET /api/interaction/status/<id> - 获取互动状态

### 推荐相关
- GET /api/recommend/personal - 获取个性化推荐
- GET /api/recommend/hot - 获取热门推荐
- GET /api/recommend/similar/<id> - 获取相似内容推荐
- POST /api/recommend/refresh - 刷新推荐系统

## 定时任务
系统支持定时任务:
- 每天凌晨2点自动爬取数据
- 每小时更新推荐系统

## 推荐算法说明

### 协同过滤推荐
基于用户行为数据，通过计算用户-物品矩阵，找出相似用户感兴趣的物品进行推荐。

### 内容推荐
根据用户的浏览历史、点赞、收藏行为，分析用户偏好的分类，推荐相似分类的内容。

### 混合推荐
将协同过滤推荐和内容推荐的结果进行加权融合:
- 协同过滤权重: 0.6
- 内容推荐权重: 0.4

新用户(行为数据<3次)推荐热门内容。

## 项目结构

village-culture-backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── user.py          # 用户模型
│   │   ├── culture.py       # 文化内容模型
│   │   └── interaction.py   # 互动模型
│   ├── routes/
│   │   ├── auth.py          # 用户认证路由
│   │   ├── culture.py       # 内容路由
│   │   ├── interaction.py   # 互动路由
│   │   └── recommend.py     # 推荐路由
│   └── services/
│       └── recommender.py   # 推荐系统服务
├── scripts/
│   ├── crawler.py           # 数据爬虫
│   ├── import_data.py       # 数据导入
│   ├── init_sample_data.py  # 初始化示例数据
│   └── scheduler.py         # 定时任务调度
├── config.py                # 配置文件
├── run.py                   # 启动文件
├── run_with_scheduler.py    # 带定时任务的启动文件
└── requirements.txt         # 依赖列表

## 注意事项
1. 生产环境请修改 `.env` 中的密钥
2. 建议使用HTTPS协议
3. 定时任务需要保持进程运行
4. MySQL需要支持中文(utf8mb4)

## 更新日志

### v1.0.0 (2024-02-23)
- 完善爬虫功能，支持多数据源爬取
- 修复推荐系统bug
- 添加用户互动状态查询
- 优化搜索功能，支持分页
- 添加刷新内容API
