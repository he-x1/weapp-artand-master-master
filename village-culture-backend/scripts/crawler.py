# # village-culture-backend/scripts/crawler.py
# """
# 乡村文化数据爬虫系统
# """
# import requests
# from bs4 import BeautifulSoup
# import os
# import time
# import re
# import json
# from datetime import datetime
# from PIL import Image
# from io import BytesIO
# import hashlib
# from loguru import logger
#
#
# class CultureCrawler:
#     """乡村文化数据爬虫"""
#
#     def __init__(self, upload_folder='../uploads'):
#         self.upload_folder = upload_folder
#         self.headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
#
#         # 确保上传文件夹存在
#         os.makedirs(upload_folder, exist_ok=True)
#
#     def download_image(self, img_url, category_name):
#         """下载图片并保存到本地"""
#         try:
#             if not img_url or not img_url.startswith('http'):
#                 return None
#
#             response = requests.get(img_url, headers=self.headers, timeout=15)
#             if response.status_code == 200:
#                 # 生成唯一文件名
#                 img_hash = hashlib.md5(img_url.encode()).hexdigest()[:10]
#                 ext = img_url.split('.')[-1].lower()
#                 if ext not in ['jpg', 'jpeg', 'png', 'gif']:
#                     ext = 'jpg'
#
#                 filename = f"{category_name}_{img_hash}.{ext}"
#                 filepath = os.path.join(self.upload_folder, filename)
#
#                 # 保存图片
#                 img = Image.open(BytesIO(response.content))
#                 img = img.convert('RGB')
#
#                 # 调整图片大小，适配移动端
#                 img.thumbnail((800, 600), Image.Resampling.LANCZOS)
#                 img.save(filepath, 'JPEG', quality=85)
#
#                 logger.info(f'下载图片成功: {filename}')
#                 return f'/uploads/{filename}'
#
#         except Exception as e:
#             logger.error(f'下载图片失败 {img_url}: {e}')
#         return None
#
#     def clean_text(self, text):
#         """清理文本，去除多余空白和HTML标签"""
#         if not text:
#             return ''
#         text = re.sub(r'<[^>]+>', '', text)
#         text = re.sub(r'\s+', ' ', text)
#         return text.strip()
#
#     def crawl_ihchina(self):
#         """爬取中国非物质文化遗产网"""
#         logger.info('开始爬取中国非遗网...')
#         data_list = []
#
#         try:
#             # 中国非遗网的非遗名录页面
#             urls = [
#                 'https://www.ihchina.cn/feiyi.html',
#                 'https://www.ihchina.cn/project.html',
#             ]
#
#             for url in urls:
#                 try:
#                     response = requests.get(url, headers=self.headers, timeout=10)
#                     soup = BeautifulSoup(response.text, 'html.parser')
#
#                     # 查找所有非遗项目
#                     items = soup.find_all('div', class_='item') or soup.find_all('li', class_='project-item')
#
#                     for item in items[:10]:  # 限制每次爬取数量
#                         try:
#                             # 提取标题
#                             title_elem = item.find('h3') or item.find('a', class_='title')
#                             title = self.clean_text(title_elem.get_text()) if title_elem else None
#
#                             # 提取描述
#                             desc_elem = item.find('p') or item.find('div', class_='desc')
#                             description = self.clean_text(desc_elem.get_text()) if desc_elem else ''
#
#                             # 提取图片
#                             img_elem = item.find('img')
#                             img_url = img_elem.get('src') if img_elem else None
#
#                             # 提取链接
#                             link_elem = item.find('a')
#                             link = link_elem.get('href') if link_elem else None
#
#                             if title and len(title) > 2:
#                                 # 判断分类
#                                 category_id = self.detect_category(title, description)
#
#                                 # 下载图片
#                                 cover_image = None
#                                 if img_url:
#                                     cover_image = self.download_image(img_url, f'ihchina_{category_id}')
#
#                                 data_list.append({
#                                     'name': title[:200],
#                                     'description': description[
#                                                    :1000] if description else f'{title}是中国的传统非物质文化遗产。',
#                                     'summary': description[:100] if description else f'{title}是中国传统技艺。',
#                                     'category_id': category_id,
#                                     'cover_image': cover_image or '/images/default_culture.jpg',
#                                     'source': '中国非遗网',
#                                     'source_url': link,
#                                     'origin': '中国',
#                                     'heritage_level': '国家级'
#                                 })
#
#                                 logger.info(f'爬取成功: {title}')
#
#                         except Exception as e:
#                             logger.error(f'解析项目失败: {e}')
#                             continue
#
#                     time.sleep(1)  # 礼貌爬取
#
#                 except Exception as e:
#                     logger.error(f'爬取页面失败 {url}: {e}')
#                     continue
#
#         except Exception as e:
#             logger.error(f'爬取中国非遗网失败: {e}')
#
#         return data_list
#
#     def crawl_folk_culture(self):
#         """爬取民俗文化相关网站"""
#         logger.info('开始爬取民俗文化网站...')
#         data_list = []
#
#         # 示例：爬取一些民俗文化网站
#         sources = [
#             {
#                 'url': 'http://www.chnfolk.com',
#                 'name': '中国民俗网',
#                 'category_keywords': {
#                     '手工': 1, '工艺': 1, '剪纸': 1, '刺绣': 1,
#                     '戏曲': 2, '表演': 2, '皮影': 2,
#                     '传说': 4, '故事': 4,
#                     '节庆': 6, '习俗': 6
#                 }
#             }
#         ]
#
#         for source in sources:
#             try:
#                 response = requests.get(source['url'], headers=self.headers, timeout=10)
#                 soup = BeautifulSoup(response.text, 'html.parser')
#
#                 # 提取文章或内容
#                 articles = soup.find_all('article') or soup.find_all('div', class_='content')
#
#                 for article in articles[:5]:
#                     try:
#                         title_elem = article.find('h1') or article.find('h2') or article.find('a')
#                         title = self.clean_text(title_elem.get_text()) if title_elem else None
#
#                         desc_elem = article.find('p') or article.find('div', class_='text')
#                         description = self.clean_text(desc_elem.get_text()) if desc_elem else ''
#
#                         img_elem = article.find('img')
#                         img_url = img_elem.get('src') if img_elem else None
#
#                         if title and len(title) > 2:
#                             category_id = self.detect_category_by_keywords(title, description,
#                                                                            source['category_keywords'])
#
#                             cover_image = None
#                             if img_url:
#                                 cover_image = self.download_image(img_url, f'folk_{category_id}')
#
#                             data_list.append({
#                                 'name': title,
#                                 'description': description or f'{title}是传统民俗文化的重要组成部分。',
#                                 'summary': description[:100] if description else f'{title}是民俗文化。',
#                                 'category_id': category_id,
#                                 'cover_image': cover_image or '/images/default_culture.jpg',
#                                 'source': source['name'],
#                                 'source_url': source['url'],
#                                 'origin': '中国',
#                                 'heritage_level': '地方级'
#                             })
#
#                     except Exception as e:
#                         logger.error(f'解析文章失败: {e}')
#                         continue
#
#                 time.sleep(2)
#
#             except Exception as e:
#                 logger.error(f'爬取 {source["name"]} 失败: {e}')
#                 continue
#
#         return data_list
#
#     def detect_category(self, title, description):
#         """自动检测分类"""
#         text = f"{title} {description}".lower()
#
#         # 分类关键词
#         categories = {
#             1: ['手工', '工艺', '剪纸', '刺绣', '陶瓷', '木雕', '竹编', '编织'],
#             2: ['戏曲', '表演', '皮影', '木偶', '杂技', '舞蹈'],
#             3: ['技艺', '制作', '生产', '农耕', '纺织', '酿造'],
#             4: ['传说', '故事', '风物', '神话', '民间'],
#             5: ['人物', '英雄', '名人', '历史'],
#             6: ['节庆', '习俗', '节日', '庆典', '仪式'],
#             7: ['文学', '歌谣', '谚语', '诗词']
#         }
#
#         for category_id, keywords in categories.items():
#             if any(keyword in text for keyword in keywords):
#                 return category_id
#
#         return 1  # 默认传统手工
#
#     def detect_category_by_keywords(self, title, description, keywords_dict):
#         """根据关键词字典检测分类"""
#         text = f"{title} {description}".lower()
#
#         for keyword, category_id in keywords_dict.items():
#             if keyword in text:
#                 return category_id
#
#         return 1
#
#     def crawl_all(self):
#         """爬取所有数据源"""
#         all_data = []
#
#         # 爬取中国非遗网
#         data = self.crawl_ihchina()
#         all_data.extend(data)
#         logger.info(f'中国非遗网: {len(data)} 条数据')
#
#         # 爬取民俗网站
#         data = self.crawl_folk_culture()
#         all_data.extend(data)
#         logger.info(f'民俗网站: {len(data)} 条数据')
#
#         return all_data
#
#
# # 使用示例
# if __name__ == '__main__':
#     crawler = CultureCrawler(upload_folder='./uploads')
#     data = crawler.crawl_all()
#
#     # 保存为JSON
#     with open('crawled_data.json', 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
#
#     print(f'共爬取 {len(data)} 条数据')



def crawl_wikipedia(self):
    """爬取维基百科的中国文化相关页面"""
    logger.info('开始爬取维基百科...')
    data_list = []

    # 维基百科的文化相关页面
    wiki_pages = [
        'https://zh.wikipedia.org/wiki/中国非物质文化遗产',
        'https://zh.wikipedia.org/wiki/中国传统工艺',
        'https://zh.wikipedia.org/wiki/中国民俗',
    ]

    for url in wiki_pages:
        try:
            response = self.safe_request(url)
            if not response:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取链接和文化项目
            links = soup.find_all('a', href=True)

            for link in links[:20]:  # 限制数量
                title = link.get_text().strip()
                href = link.get('href')

                # 过滤有效内容
                if title and len(title) > 2 and len(title) < 50:
                    # 检测分类
                    category_id = self.detect_category(title, '')

                    data_list.append({
                        'name': title,
                        'description': f'{title}是中国传统文化的重要组成部分。',
                        'summary': f'{title}是传统文化。',
                        'category_id': category_id,
                        'cover_image': '/images/default_culture.jpg',
                        'source': '维基百科',
                        'source_url': f'https://zh.wikipedia.org{href}' if href.startswith('/') else href,
                        'origin': '中国',
                        'heritage_level': '其他'
                    })

            time.sleep(2)

        except Exception as e:
            logger.error(f'爬取维基百科失败: {e}')
            continue

    return data_list


def crawl_baidu_baike(self):
    """爬取百度百科（模拟数据）"""
    logger.info('生成模拟数据...')

    # 模拟一些真实的文化内容数据
    mock_data = [
        {
            'name': '苏绣',
            'description': '苏绣是中国优秀的民族传统工艺之一，是苏州地区刺绣产品的总称，其发源地在苏州吴县一带，现已遍衍无锡、常州等地。',
            'summary': '苏州地区传统刺绣工艺',
            'category_id': 1,
            'source': '百度百科',
            'origin': '江苏苏州',
            'heritage_level': '国家级'
        },
        {
            'name': '景德镇瓷器',
            'description': '景德镇瓷器以"白如玉、明如镜、薄如纸、声如磬"的独特风格闻名中外，历史悠久，品种繁多。',
            'summary': '景德镇传统制瓷工艺',
            'category_id': 1,
            'source': '百度百科',
            'origin': '江西景德镇',
            'heritage_level': '国家级'
        },
        {
            'name': '京剧',
            'description': '京剧，又称平剧、京戏，是中国五大戏曲剧种之一，被视为中国国粹，分布地以北京为中心，遍及全国。',
            'summary': '中国国粹戏曲艺术',
            'category_id': 2,
            'source': '百度百科',
            'origin': '北京',
            'heritage_level': '国家级'
        },
        {
            'name': '昆曲',
            'description': '昆曲，原名"昆山腔"或简称"昆腔"，是中国古老的戏曲声腔、剧种，现又被称为"昆剧"。',
            'summary': '中国古老戏曲剧种',
            'category_id': 2,
            'source': '百度百科',
            'origin': '江苏昆山',
            'heritage_level': '世界级'
        },
        {
            'name': '蓝印花布',
            'description': '蓝印花布又称靛蓝花布，俗称药斑布、浇花布等。是汉族传统的工艺印染品。',
            'summary': '传统印染工艺',
            'category_id': 1,
            'source': '百度百科',
            'origin': '江苏南通',
            'heritage_level': '省级'
        },
        {
            'name': '泥人张',
            'description': '泥人张彩塑为天津市的一种民间文化，著名的汉族传统手工艺品之一。',
            'summary': '天津传统彩塑艺术',
            'category_id': 1,
            'source': '百度百科',
            'origin': '天津',
            'heritage_level': '国家级'
        },
        {
            'name': '苗族银饰',
            'description': '苗族银饰是苗族重要的文化标志，其独特的造型和精美的工艺在中国民族首饰中占有重要地位。',
            'summary': '苗族传统首饰工艺',
            'category_id': 1,
            'source': '百度百科',
            'origin': '贵州、湖南',
            'heritage_level': '国家级'
        },
        {
            'name': '少林功夫',
            'description': '少林功夫是中国武术中体系最庞大的门派，武功套路高达七百种以上，是中华武术的象征。',
            'summary': '中国武术文化代表',
            'category_id': 2,
            'source': '百度百科',
            'origin': '河南登封',
            'heritage_level': '世界级'
        },
        {
            'name': '端午节',
            'description': '端午节，又称端阳节、龙舟节、重午节、天中节等，是集拜神祭祖、祈福辟邪、欢庆娱乐和饮食为一体的民俗大节。',
            'summary': '中国传统节日',
            'category_id': 6,
            'source': '百度百科',
            'origin': '中国',
            'heritage_level': '世界级'
        },
        {
            'name': '春节',
            'description': '春节，即中国农历新年，俗称"过年"，是中华民族最隆重的传统佳节。',
            'summary': '中国最重要的传统节日',
            'category_id': 6,
            'source': '百度百科',
            'origin': '中国',
            'heritage_level': '国家级'
        },
        {
            'name': '嫦娥奔月',
            'description': '嫦娥奔月是中国上古时代神话传说故事，讲述了嫦娥被逢蒙所逼，无奈之下，吃下了仙药西王母赐给丈夫后羿的两粒不死之药后，飞到了月宫的事情。',
            'summary': '中国古代神话传说',
            'category_id': 4,
            'source': '百度百科',
            'origin': '中国',
            'heritage_level': '民间传说'
        },
        {
            'name': '牛郎织女',
            'description': '牛郎织女，为中国古代著名的汉族民间爱情故事，也是我国四大民间传说之一。',
            'summary': '中国民间爱情传说',
            'category_id': 4,
            'source': '百度百科',
            'origin': '中国',
            'heritage_level': '民间传说'
        }
    ]

    return mock_data


def crawl_all(self):
    """爬取所有数据源"""
    all_data = []

    # 1. 尝试爬取维基百科
    try:
        data = self.crawl_wikipedia()
        all_data.extend(data)
        logger.info(f'维基百科: {len(data)} 条数据')
    except Exception as e:
        logger.error(f'维基百科爬取失败: {e}')

    # 2. 使用模拟数据（保证有数据）
    data = self.crawl_baidu_baike()
    all_data.extend(data)
    logger.info(f'模拟数据: {len(data)} 条数据')

    # 3. 尝试爬取非遗网（如果网络好）
    try:
        data = self.crawl_ihchina()
        all_data.extend(data)
        logger.info(f'中国非遗网: {len(data)} 条数据')
    except Exception as e:
        logger.warning(f'非遗网爬取失败: {e}')

    return all_data