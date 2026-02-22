# 乡村文化传播系统 - Python后端

基于Flask的乡村文化传播系统后端服务。

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置数据库
修改 `.env` 文件中的数据库配置

### 3. 初始化数据库
```bash
mysql -u root -p < init_data.sql
```

### 4. 运行应用
```bash
python run.py
```

## API接口
- 用户认证: /api/user/*
- 文化内容: /api/content/*
- 用户交互: /api/interaction/*
- 推荐系统: /api/recommend/*

## 技术栈
- Flask 2.3.3
- MySQL 8.0
- SQLAlchemy
- JWT认证
