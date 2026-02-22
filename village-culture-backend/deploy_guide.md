# 前后端连接部署指南

## 一、后端部署（PyCharm）

### 1. 数据库准备

#### 安装MySQL（如果未安装）
- Windows: 下载MySQL安装包并安装
- Mac: `brew install mysql`
- Linux: `sudo apt-get install mysql-server`

#### 创建数据库
```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE village_culture CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 退出
exit
```

### 2. PyCharm配置

#### 打开项目
1. File -> Open
2. 选择 village-culture-backend 文件夹

#### 配置Python虚拟环境
1. File -> Settings -> Project -> Python Interpreter
2. 点击齿轮图标 -> Add
3. 选择 Virtualenv Environment
4. 选择 New environment
5. 点击 OK

#### 安装依赖
在PyCharm的Terminal中运行：
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

修改 `.env` 文件：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_NAME=village_culture

# JWT配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=86400

# 应用配置
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
```

### 4. 初始化数据库

在PyCharm Terminal中运行：
```bash
mysql -u root -p village_culture < init_data.sql
```

或者在MySQL客户端中执行 `init_data.sql` 文件。

### 5. 运行后端服务

#### 方法1：直接运行
右键点击 `run.py` -> Run 'run'

#### 方法2：Terminal运行
```bash
python run.py
```

看到以下信息表示成功：
```
 * Running on http://0.0.0.0:5000
 * Restarting with stat
 * Debugger is active!
```

### 6. 测试后端API

打开浏览器访问：
- http://localhost:5000/api/content/categories
- 应该返回JSON格式的分类数据

## 二、前端配置

### 1. 修改小程序配置

#### 关闭Mock模式
打开 `utils/apiService.js`，修改第7行：
```javascript
const USE_MOCK = false  // 改为false使用真实API
```

#### 配置API地址
打开 `utils/config.js`，修改第10行：
```javascript
API: {
  BASE_URL: 'http://localhost:5000/api/v1',  // 本地开发
  TIMEOUT: 10000
}
```

注意：
- 本地开发使用 `http://localhost:5000/api/v1`
- 真机调试使用 `http://你的电脑IP:5000/api/v1`
- 生产环境使用 `https://你的域名/api/v1`

### 2. 配置微信开发者工具

#### 设置不校验合法域名（开发阶段）
1. 微信开发者工具 -> 右上角详情
2. 本地设置 -> 勾选 "不校验合法域名、web-view（业务域名）、TLS版本以及HTTPS证书"

### 3. 测试连接

在微信开发者工具中：
1. 打开项目
2. 打开控制台 Console
3. 刷新页面
4. 查看是否有API请求错误

## 三、常见问题

### 问题1：数据库连接失败
```
解决：
1. 确认MySQL服务已启动
2. 检查.env中的数据库配置是否正确
3. 确认数据库village_culture已创建
```

### 问题2：前端请求失败
```
解决：
1. 确认后端服务已启动（http://localhost:5000）
2. 检查前端apiService.js中USE_MOCK是否为false
3. 检查前端config.js中BASE_URL是否正确
4. 在微信开发者工具中勾选"不校验合法域名"
```

### 问题3：跨域问题
```
解决：
后端已配置CORS，允许所有域名访问
如果仍有问题，检查Flask-CORS配置
```

### 问题4：真机调试无法连接
```
解决：
1. 手机和电脑在同一个局域网
2. 前端config.js使用电脑IP地址（不是localhost）
3. 关闭电脑防火墙或允许5000端口
4. 查看电脑IP：ipconfig（Windows）或 ifconfig（Mac/Linux）
```

## 四、生产环境部署

### 1. 服务器部署

#### 安装依赖
```bash
pip install gunicorn
```

#### 使用Gunicorn运行
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 2. Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. HTTPS配置

微信小程序要求生产环境必须使用HTTPS：

1. 申请SSL证书（推荐使用免费的Let's Encrypt）
2. 配置Nginx HTTPS
3. 在微信公众平台配置服务器域名

## 五、数据采集（可选）

### 运行爬虫脚本
```bash
python scripts/spider.py
```

## 六、功能验证清单

- [ ] 后端服务启动成功
- [ ] 数据库连接正常
- [ ] API接口可访问（浏览器测试）
- [ ] 前端Mock模式已关闭
- [ ] 前端API地址配置正确
- [ ] 微信开发者工具设置正确
- [ ] 首页数据加载正常
- [ ] 登录注册功能正常
- [ ] 点赞收藏功能正常
- [ ] 搜索功能正常

## 七、开发流程建议

1. **开发阶段**：
   - 后端在PyCharm中运行
   - 前端在微信开发者工具中运行
   - 使用localhost连接

2. **测试阶段**：
   - 同一局域网内
   - 使用电脑IP地址
   - 手机端测试

3. **生产阶段**：
   - 后端部署到服务器
   - 配置HTTPS
   - 域名解析
   - 微信公众平台配置
