# 乡村文化传播小程序

一个专注于传播中华传统乡村文化的微信小程序，致力于让更多人了解和喜爱乡村文化。

## 功能特性

### 已实现功能
- ✅ 用户登录注册（微信授权 + 手机号登录）
- ✅ 首页推荐内容展示
- ✅ 发现页内容浏览
- ✅ 分类浏览功能
- ✅ 内容详情展示
- ✅ 点赞、收藏功能
- ✅ 搜索功能（关键词搜索 + 搜索历史）
- ✅ 用户个人中心
- ✅ 智能推荐基础架构

### 待开发功能
- 🔲 后端API对接
- 🔲 Python爬虫数据采集
- 🔲 数据库集成
- 🔲 个性化智能推荐算法优化
- 🔲 用户互动功能（评论、分享）

## 项目结构

```
/workspace
├── components/           # 公共组件
│   ├── culture-card/    # 文化内容卡片组件
│   └── search-bar/      # 搜索栏组件
├── pages/               # 页面文件
│   ├── index/           # 首页
│   ├── discover/        # 发现页
│   ├── exhibition/      # 分类页
│   ├── setting/         # 个人中心
│   ├── work-detail/     # 内容详情页
│   ├── login/           # 登录页
│   ├── register/        # 注册页
│   └── search/          # 搜索页
├── utils/               # 工具模块
│   ├── api.js           # API接口定义
│   ├── apiService.js    # API服务封装
│   ├── config.js        # 配置文件
│   ├── userManager.js   # 用户状态管理
│   ├── recommendEngine.js # 智能推荐引擎
│   └── util.js          # 工具函数
├── mock/                # 模拟数据
│   └── data.js          # 开发阶段模拟数据
├── images/              # 图片资源
├── app.js               # 应用入口
├── app.json             # 应用配置
└── app.wxss             # 全局样式
```

## 技术栈

- **前端**: 微信小程序原生框架
- **UI设计**: 乡村文化主题（大地色系）
- **状态管理**: 全局App + 本地缓存
- **网络请求**: Promise封装

## 开发指南

### 1. 环境准备

1. 安装[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 克隆项目到本地
3. 使用微信开发者工具打开项目目录

### 2. 配置后端接口

在 `utils/config.js` 中修改API地址：

```javascript
API: {
  BASE_URL: 'https://your-api-domain.com/api/v1',
  TIMEOUT: 10000
}
```

在 `utils/apiService.js` 中关闭Mock模式：

```javascript
const USE_MOCK = false  // 改为false使用真实API
```

### 3. API接口说明

#### 用户相关接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/user/wx-login` | POST | 微信登录 |
| `/user/login` | POST | 手机号登录 |
| `/user/register` | POST | 用户注册 |
| `/user/send-sms` | POST | 发送验证码 |
| `/user/info` | GET | 获取用户信息 |

#### 内容相关接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/content/banners` | GET | 获取轮播图 |
| `/content/recommend` | GET | 获取推荐内容 |
| `/content/latest` | GET | 获取最新内容 |
| `/content/detail/:id` | GET | 获取内容详情 |
| `/content/search` | GET | 搜索内容 |
| `/content/categories` | GET | 获取分类列表 |
| `/content/category/:id` | GET | 根据分类获取内容 |

#### 互动相关接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/interaction/like` | POST | 点赞 |
| `/interaction/unlike` | POST | 取消点赞 |
| `/interaction/collect` | POST | 收藏 |
| `/interaction/uncollect` | POST | 取消收藏 |
| `/interaction/likes` | GET | 获取点赞列表 |
| `/interaction/collects` | GET | 获取收藏列表 |
| `/interaction/history` | GET | 获取浏览历史 |

#### 推荐相关接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/recommend/personal` | GET | 个性化推荐 |
| `/recommend/preference` | POST | 更新用户偏好 |
| `/recommend/hot` | GET | 热门推荐 |

### 4. 后端开发建议

#### Python后端框架推荐
- **Flask**: 轻量级，适合小型项目
- **Django**: 功能全面，适合中大型项目
- **FastAPI**: 高性能，支持异步

#### 数据库建议
- **MySQL**: 存储用户信息、内容数据
- **Redis**: 缓存热门数据、用户会话
- **MongoDB**: 存储用户行为日志（可选）

#### 爬虫技术栈
- **Scrapy**: Python爬虫框架
- **BeautifulSoup**: HTML解析
- **Selenium**: 动态网页爬取

#### 数据源建议
- 中国非物质文化遗产网
- 各地文化馆官网
- 维基百科相关条目
- 权威文化机构网站

### 5. 部署说明

1. 后端部署到服务器（推荐使用nginx + gunicorn）
2. 配置HTTPS证书（微信小程序要求）
3. 在微信公众平台配置服务器域名
4. 在 `project.config.json` 中配置AppID

## 主题设计

### 配色方案（乡村文化主题）
- **主色调**: #8B7355（深棕色）
- **次色调**: #D4A574（浅棕色）
- **强调色**: #7A9E7E（自然绿）
- **背景色**: #F5F1E8（米色）
- **文字色**: #2C2416（深色）

### 设计理念
- 采用大地色系，体现乡村文化的质朴与自然
- 卡片式布局，简洁清晰
- 渐变效果，增加层次感
- 圆角设计，柔和友好

## 智能推荐算法

### 推荐策略
1. **基于用户行为**: 记录用户的浏览、点赞、收藏行为
2. **分类偏好**: 统计用户喜欢的文化分类
3. **热度加权**: 结合内容的浏览量、点赞数、收藏数
4. **去重过滤**: 避免推荐已浏览过的内容

### 优化方向
- 协同过滤算法
- 内容相似度计算
- 时间衰减因子
- A/B测试优化

## 注意事项

1. **Mock数据**: 开发阶段使用 `utils/apiService.js` 中的Mock数据，生产环境需切换为真实API
2. **用户隐私**: 遵守微信小程序用户隐私保护规范
3. **内容审核**: 爬取的内容需经过审核后展示
4. **性能优化**: 注意图片压缩、请求缓存、懒加载等优化

## 更新日志

### v1.0.0 (2024-02-16)
- 完成基础架构重构
- 实现核心功能
- 设计乡村文化主题UI
- 完善前后端接口

## 开发者

本项目由Claude AI助手协助开发

## 许可证

MIT License
