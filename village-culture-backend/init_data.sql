CREATE DATABASE IF NOT EXISTS village_culture CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE village_culture;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(100),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    openid VARCHAR(100) UNIQUE,
    phone VARCHAR(11) UNIQUE,
    password_hash VARCHAR(255),
    nickname VARCHAR(50),
    avatar VARCHAR(500),
    gender INT DEFAULT 0,
    province VARCHAR(50),
    city VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_openid (openid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cultures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category_id INT NOT NULL,
    description TEXT,
    summary VARCHAR(500),
    origin VARCHAR(200),
    heritage_level VARCHAR(50),
    cover_image VARCHAR(500),
    images TEXT,
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    collect_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    score FLOAT DEFAULT 0.0,
    is_hot BOOLEAN DEFAULT FALSE,
    is_recommend BOOLEAN DEFAULT TRUE,
    source VARCHAR(200),
    source_url VARCHAR(500),
    status INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_score (score),
    FULLTEXT idx_search (name, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    culture_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (culture_id) REFERENCES cultures(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_culture_like (user_id, culture_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS collects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    culture_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (culture_id) REFERENCES cultures(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_culture_collect (user_id, culture_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS view_histories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    culture_id INT NOT NULL,
    view_duration INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (culture_id) REFERENCES cultures(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_behaviors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    culture_id INT NOT NULL,
    behavior_type VARCHAR(20) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (culture_id) REFERENCES cultures(id) ON DELETE CASCADE,
    INDEX idx_user_behavior (user_id, behavior_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO categories (name, description, sort_order) VALUES
('传统手工', '传统手工艺技艺', 1),
('表演艺术', '传统表演艺术', 2),
('生产技艺', '传统生产技艺', 3),
('风物传说', '地方风物传说', 4),
('人物传说', '历史人物传说', 5),
('节庆习俗', '传统节庆习俗', 6),
('民间文学', '民间文学作品', 7);

INSERT INTO cultures (name, category_id, description, summary, origin, heritage_level, cover_image, view_count, like_count, collect_count, share_count, score) VALUES
('年画', 1, '年画是中国画的一种，始于古代的"门神画"，中国民间艺术之一。', '中国传统民间艺术', '山东潍坊', '国家级', '/images/New_Year_pictures.png', 128, 36, 35, 12, 85.5),
('皮影戏', 2, '皮影戏是中国民间古老的传统艺术，始于西汉，兴于唐朝。', '古老的民间艺术', '陕西华县', '国家级', '/images/Shadow_puppetry.png', 95, 24, 30, 8, 78.3),
('剪纸', 1, '中国剪纸是一种用剪刀或刻刀在纸上剪刻花纹的民间艺术。', '纸上的艺术', '山西静乐', '国家级', '/images/Cookie_cutter.png', 210, 58, 40, 15, 92.1),
('苏绣', 1, '苏绣是中国优秀的民族传统工艺之一，是苏州地区刺绣产品的总称。', '苏州传统刺绣工艺', '江苏苏州', '国家级', '/images/default_culture.jpg', 156, 42, 38, 10, 88.5),
('京剧', 2, '京剧是中国五大戏曲剧种之一，被视为中国国粹。', '中国国粹戏曲艺术', '北京', '国家级', '/images/default_culture.jpg', 189, 55, 45, 18, 91.2),
('昆曲', 2, '昆曲是中国古老的戏曲声腔、剧种，被称为"百戏之祖"。', '中国古老戏曲剧种', '江苏昆山', '世界级', '/images/default_culture.jpg', 145, 38, 32, 9, 85.0),
('端午节', 6, '端午节是集拜神祭祖、祈福辟邪、欢庆娱乐和饮食为一体的民俗大节。', '中国传统节日', '中国', '世界级', '/images/default_culture.jpg', 230, 68, 52, 22, 95.5),
('春节', 6, '春节是中华民族最隆重的传统佳节。', '中国最重要的传统节日', '中国', '国家级', '/images/default_culture.jpg', 280, 85, 72, 35, 98.8),
('少林功夫', 2, '少林功夫是中国武术中体系最庞大的门派，是中华武术的象征。', '中国武术文化代表', '河南登封', '世界级', '/images/default_culture.jpg', 175, 48, 42, 14, 89.3);
