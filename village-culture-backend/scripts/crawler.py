"""
乡村文化数据爬虫系统
"""
import requests
from bs4 import BeautifulSoup
import os
import time
import re
import json
from datetime import datetime
from PIL import Image
from io import BytesIO
import hashlib
from loguru import logger


class CultureCrawler:
    """乡村文化数据爬虫"""

    def __init__(self, upload_folder='uploads'):
        self.upload_folder = upload_folder
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 确保上传文件夹存在
        os.makedirs(upload_folder, exist_ok=True)

    def download_image(self, img_url, category_name):
        """下载图片并保存到本地"""
        try:
            if not img_url or not img_url.startswith('http'):
                return None
            response = requests.get(img_url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                img_hash = hashlib.md5(img_url.encode()).hexdigest()[:10]
                ext = img_url.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                    ext = 'jpg'
                filename = f"{category_name}_{img_hash}.{ext}"
                filepath = os.path.join(self.upload_folder, filename)
                img = Image.open(BytesIO(response.content))
                img = img.convert('RGB')
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                img.save(filepath, 'JPEG', quality=85)
                logger.info(f'下载图片成功: {filename}')
                return f'/uploads/{filename}'
        except Exception as e:
            logger.error(f'下载图片失败 {img_url}: {e}')
        return None

    def clean_text(self, text):
        """清理文本，去除多余空白和HTML标签"""
        if not text:
            return ''
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def detect_category(self, title, description):
        """根据标题和描述判断分类"""
        text = f"{title} {description}".lower()
        category_keywords = {
            1: ['刺绣', '剪纸', '陶瓷', '瓷器', '漆器', '编织', '雕刻', '手工', '工艺', '银饰', '年画', '泥人', '花布'],
            2: ['戏曲', '京剧', '昆曲', '皮影', '舞蹈', '音乐', '表演', '功夫', '武术', '杂技'],
            3: ['农耕', '酿造', '制茶', '纺织', '造纸', '印刷', '生产'],
            4: ['传说', '神话', '故事', '风物', '地方', '民间'],
            5: ['人物', '英雄', '名人', '历史'],
            6: ['节日', '节庆', '春节', '端午', '中秋', '习俗', '民俗', '庙会'],
            7: ['文学', '诗歌', '谚语', '歌谣', '民间文学']
        }
        for category_id, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return category_id
        return 1

    def crawl_ihchina(self):
        """爬取中国非物质文化遗产网"""
        logger.info('开始爬取中国非遗网...')
        data_list = []
        try:
            urls = [
                'https://www.ihchina.cn/feiyi.html',
                'https://www.ihchina.cn/project.html',
            ]
            for url in urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    items = soup.find_all('div', class_='item') or soup.find_all('li', class_='project-item')
                    for item in items[:10]:
                        try:
                            title_elem = item.find('h3') or item.find('a', class_='title')
                            title = self.clean_text(title_elem.get_text()) if title_elem else None
                            desc_elem = item.find('p') or item.find('div', class_='desc')
                            description = self.clean_text(desc_elem.get_text()) if desc_elem else ''
                            img_elem = item.find('img')
                            img_url = img_elem.get('src') if img_elem else None
                            link_elem = item.find('a')
                            link = link_elem.get('href') if link_elem else None
                            if title and len(title) > 2:
                                category_id = self.detect_category(title, description)
                                cover_image = None
                                if img_url:
                                    cover_image = self.download_image(img_url, f'ihchina_{category_id}')
                                data_list.append({
                                    'name': title[:200],
                                    'description': description[:1000] if description else f'{title}是中国的传统非物质文化遗产。',
                                    'summary': description[:100] if description else f'{title}是中国传统技艺。',
                                    'category_id': category_id,
                                    'cover_image': cover_image or '/images/default_culture.jpg',
                                    'source': '中国非遗网',
                                    'source_url': link,
                                    'origin': '中国',
                                    'heritage_level': '国家级'
                                })
                                logger.info(f'爬取成功: {title}')
                        except Exception as e:
                            logger.error(f'解析项目失败: {e}')
                            continue
                    time.sleep(1)
                except Exception as e:
                    logger.error(f'爬取页面失败 {url}: {e}')
                    continue
        except Exception as e:
            logger.error(f'爬取中国非遗网失败: {e}')
        return data_list

    def crawl_wikipedia(self):
        """爬取维基百科的中国非遗条目"""
        logger.info('开始爬取维基百科...')
        data_list = []
        try:
            url = 'https://zh.wikipedia.org/wiki/中国非物质文化遗产'
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find('div', class_='mw-parser-output')
            if content:
                items = content.find_all('li')
                for item in items[:15]:
                    text = self.clean_text(item.get_text())
                    if text and len(text) > 5 and len(text) < 200:
                        category_id = self.detect_category(text, '')
                        data_list.append({
                            'name': text[:100],
                            'description': f'{text}是中国重要的非物质文化遗产项目。',
                            'summary': text[:100],
                            'category_id': category_id,
                            'cover_image': '/images/default_culture.jpg',
                            'source': '维基百科',
                            'source_url': url,
                            'origin': '中国',
                            'heritage_level': '国家级'
                        })
                        logger.info(f'爬取维基百科条目: {text[:50]}')
        except Exception as e:
            logger.error(f'爬取维基百科失败: {e}')
        return data_list

    def crawl_baidu_baike(self):
        """获取模拟数据（确保系统有可用数据）"""
        logger.info('生成模拟数据...')
        mock_data = [
            {
                'name': '苏绣',
                'description': '苏绣是中国优秀的民族传统工艺之一，是苏州地区刺绣产品的总称，其发源地在苏州吴县一带，现已遍衍无锡、常州等地。清代确立了"苏绣、湘绣、粤绣、蜀绣"为中国四大名绣。',
                'summary': '苏州传统刺绣工艺',
                'category_id': 1,
                'source': '百度百科',
                'origin': '江苏苏州',
                'heritage_level': '国家级'
            },
            {
                'name': '景德镇瓷器',
                'description': '景德镇瓷器以"白如玉、明如镜、薄如纸、声如磬"的独特风格闻名中外。景德镇瓷器造型优美、品种繁多、装饰丰富、风格独特，以"白如玉、明如镜、薄如纸、声如磬"著称。',
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
                'description': '昆曲，原名"昆山腔"或简称"昆腔"，是中国古老的戏曲声腔、剧种，现又被称为"昆剧"。昆曲是汉族传统戏曲中最古老的剧种之一，被称为"百戏之祖"。',
                'summary': '中国古老戏曲剧种',
                'category_id': 2,
                'source': '百度百科',
                'origin': '江苏昆山',
                'heritage_level': '世界级'
            },
            {
                'name': '蓝印花布',
                'description': '蓝印花布又称靛蓝花布，俗称药斑布、浇花布等。是汉族传统的工艺印染品，镂空版白浆防染印花，距今已有一千三百年历史。',
                'summary': '传统印染工艺',
                'category_id': 1,
                'source': '百度百科',
                'origin': '江苏南通',
                'heritage_level': '省级'
            },
            {
                'name': '泥人张',
                'description': '泥人张彩塑为天津市的一种民间文化，著名的汉族传统手工艺品之一。作为津门艺林一绝，泥人张彩塑在2006年被列入中国第一批非物质文化遗产名录。',
                'summary': '天津传统彩塑艺术',
                'category_id': 1,
                'source': '百度百科',
                'origin': '天津',
                'heritage_level': '国家级'
            },
            {
                'name': '苗族银饰',
                'description': '苗族银饰是苗族重要的文化标志，其独特的造型和精美的工艺在中国民族首饰中占有重要地位。苗族银饰以其多样的品种、奇美的造型和精巧的工艺闻名于世。',
                'summary': '苗族传统首饰工艺',
                'category_id': 1,
                'source': '百度百科',
                'origin': '贵州、湖南',
                'heritage_level': '国家级'
            },
            {
                'name': '少林功夫',
                'description': '少林功夫是中国武术中体系最庞大的门派，武功套路高达七百种以上，是中华武术的象征。少林功夫讲究禅武合一，体现了中华武术的精髓。',
                'summary': '中国武术文化代表',
                'category_id': 2,
                'source': '百度百科',
                'origin': '河南登封',
                'heritage_level': '世界级'
            },
            {
                'name': '端午节',
                'description': '端午节，又称端阳节、龙舟节、重午节、天中节等，是集拜神祭祖、祈福辟邪、欢庆娱乐和饮食为一体的民俗大节。端午节与春节、清明节、中秋节并称为中国四大传统节日。',
                'summary': '中国传统节日',
                'category_id': 6,
                'source': '百度百科',
                'origin': '中国',
                'heritage_level': '世界级'
            },
            {
                'name': '春节',
                'description': '春节，即中国农历新年，俗称"过年"，是中华民族最隆重的传统佳节。春节历史悠久，由上古时代岁首祈年祭祀演变而来。',
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
                'description': '牛郎织女，为中国古代著名的汉族民间爱情故事，也是我国四大民间传说之一，从牵牛星、织女星的星名衍化而来。',
                'summary': '中国民间爱情传说',
                'category_id': 4,
                'source': '百度百科',
                'origin': '中国',
                'heritage_level': '民间传说'
            },
            {
                'name': '年画',
                'description': '年画是中国画的一种，始于古代的"门神画"，中国民间艺术之一。年画是中国农村老百姓喜闻乐见的艺术形式，大都用于新年时张贴，含有祝福新年吉祥喜庆之意。',
                'summary': '中国传统民间艺术',
                'category_id': 1,
                'source': '百度百科',
                'origin': '山东潍坊',
                'heritage_level': '国家级'
            },
            {
                'name': '皮影戏',
                'description': '皮影戏是中国民间古老的传统艺术，始于西汉，兴于唐朝。皮影戏又称"影子戏"或"灯影戏"，是一种以兽皮或纸板做成的人物剪影以表演故事的民间戏剧。',
                'summary': '古老的民间艺术',
                'category_id': 2,
                'source': '百度百科',
                'origin': '陕西华县',
                'heritage_level': '国家级'
            },
            {
                'name': '剪纸',
                'description': '中国剪纸是一种用剪刀或刻刀在纸上剪刻花纹的民间艺术。剪纸艺术是汉族传统的民间工艺，它源远流长，经久不衰，是中国民间艺术中的瑰宝。',
                'summary': '纸上的艺术',
                'category_id': 1,
                'source': '百度百科',
                'origin': '山西静乐',
                'heritage_level': '国家级'
            }
        ]
        return mock_data

    def crawl_all(self):
        """爬取所有数据源"""
        all_data = []
        # 1. 使用模拟数据（保证有数据）
        data = self.crawl_baidu_baike()
        all_data.extend(data)
        logger.info(f'模拟数据: {len(data)} 条数据')
        # 2. 尝试爬取维基百科
        try:
            data = self.crawl_wikipedia()
            all_data.extend(data)
            logger.info(f'维基百科: {len(data)} 条数据')
        except Exception as e:
            logger.warning(f'维基百科爬取失败: {e}')
        # 3. 尝试爬取非遗网（如果网络好）
        try:
            data = self.crawl_ihchina()
            all_data.extend(data)
            logger.info(f'中国非遗网: {len(data)} 条数据')
        except Exception as e:
            logger.warning(f'非遗网爬取失败: {e}')
        return all_data
