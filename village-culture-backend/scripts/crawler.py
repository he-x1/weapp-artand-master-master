"""
乡村文化数据爬虫系统
支持网络图片下载、图像预处理、文本摘要生成
"""
import requests
from bs4 import BeautifulSoup
import os
import time
import re
import json
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
import hashlib
from loguru import logger

# 尝试导入OpenCV
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except:
    HAS_CV2 = False
    logger.warning('未安装opencv-python，将使用PIL进行图像处理')

# 尝试导入摘要生成模块
try:
    from transformers import pipeline
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    HAS_SUMMARIZER = True
except:
    HAS_SUMMARIZER = False
    logger.warning('未安装transformers库，将使用简单的摘要生成')


class CultureCrawler:
    """乡村文化数据爬虫"""

    def __init__(self, upload_folder='uploads', base_url='http://localhost:5000'):
        self.upload_folder = upload_folder
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        # 确保上传文件夹存在
        os.makedirs(upload_folder, exist_ok=True)
        logger.info(f'爬虫初始化完成，图片保存路径: {upload_folder}')

    def download_image(self, img_url, category_name):
        """下载图片并保存到本地，支持图像预处理"""
        try:
            if not img_url or not img_url.startswith('http'):
                # 如果是网络图片URL但缺少协议
                if img_url and img_url.startswith('//'):
                    img_url = 'https:' + img_url
                else:
                    return None
            
            logger.info(f'正在下载图片: {img_url}')
            
            # 禁用SSL验证警告
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.get(img_url, headers=self.headers, timeout=20, verify=False)
            if response.status_code == 200:
                img_hash = hashlib.md5(img_url.encode()).hexdigest()[:10]
                ext = img_url.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    ext = 'jpg'
                filename = f"{category_name}_{img_hash}.{ext}"
                filepath = os.path.join(self.upload_folder, filename)
                
                # 使用OpenCV进行高质量图像预处理
                if HAS_CV2:
                    try:
                        img_array = np.frombuffer(response.content, np.uint8)
                        img_cv = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        
                        if img_cv is not None:
                            # 1. 图像锐化
                            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                            img_cv = cv2.filter2D(img_cv, -1, kernel)
                            
                            # 2. 对比度调整 (CLAHE)
                            lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
                            l, a, b = cv2.split(lab)
                            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                            l = clahe.apply(l)
                            lab = cv2.merge((l, a, b))
                            img_cv = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                            
                            # 3. 尺寸归一化 - 适配移动端显示
                            height, width = img_cv.shape[:2]
                            if width > 800 or height > 600:
                                scale = min(800/width, 600/height)
                                new_width = int(width * scale)
                                new_height = int(height * scale)
                                img_cv = cv2.resize(img_cv, (new_width, new_height), interpolation=cv2.INTER_AREA)
                            
                            # 保存处理后的图片
                            cv2.imwrite(filepath, img_cv, [cv2.IMWRITE_JPEG_QUALITY, 90])
                            logger.info(f'下载并预处理图片成功: {filename}')
                            return f'{self.base_url}/uploads/{filename}'
                    except Exception as e:
                        logger.warning(f'OpenCV处理失败，尝试PIL: {e}')
                
                # 如果OpenCV处理失败或未安装，使用PIL
                img = Image.open(BytesIO(response.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 锐化
                img = img.filter(ImageFilter.SHARPEN)
                
                # 对比度增强
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
                
                # 亮度调整
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.1)
                
                # 尺寸归一化
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                img.save(filepath, 'JPEG', quality=90)
                logger.info(f'下载图片成功(PIL): {filename}')
                return f'{self.base_url}/uploads/{filename}'
                
        except Exception as e:
            logger.error(f'下载图片失败 {img_url}: {e}')
        return None

    def generate_summary(self, title, description):
        """生成丰富的文本摘要"""
        text = f"{title}。{description}" if description else title
        
        # 使用预训练模型生成摘要
        if HAS_SUMMARIZER and len(text) > 100:
            try:
                summary = summarizer(text, max_length=80, min_length=30, do_sample=False)
                return summary[0]['summary_text']
            except Exception as e:
                logger.warning(f'摘要生成失败: {e}')
        
        # 如果没有摘要器或生成失败，使用规则生成摘要
        if description:
            # 提取关键信息，生成更详细的摘要
            sentences = re.split(r'[。！？]', description)
            key_sentences = []
            
            # 提取有意义的句子
            for s in sentences:
                s = s.strip()
                if len(s) > 15 and not s.startswith('http'):
                    key_sentences.append(s)
                    if len(key_sentences) >= 3:
                        break
            
            if key_sentences:
                summary = '。'.join(key_sentences)
                if len(summary) > 50:
                    return summary + '。'
        
        # 根据关键词生成摘要
        keywords_summary = {
            '刺绣': '刺绣是中国古老的手工技艺之一，以针引线，在织物上绣出各种图案，工艺精湛，色彩绚丽，是中华民族智慧的结晶。',
            '剪纸': '剪纸艺术是中国民间艺术中的瑰宝，以纸为材料，用剪刀或刻刀剪刻出各种图案，寓意吉祥，寄托美好愿望。',
            '陶瓷': '陶瓷是中国古代伟大发明之一，历经千年发展，形成了独特的艺术风格和精湛的制作工艺，是中国文化的重要象征。',
            '京剧': '京剧是中国传统戏曲艺术的代表，融合了唱、念、做、打等多种表演形式，被誉为"国粹"，是中国戏曲艺术的精华。',
            '节日': '中国传统节日承载着深厚的文化内涵，体现了中华民族对自然、祖先和美好生活的敬畏与追求，是中华文化的重要组成部分。'
        }
        
        for keyword, summary in keywords_summary.items():
            if keyword in title or (description and keyword in description):
                return summary
        
        # 默认摘要
        return f"{title}是中国传统文化的重要组成部分，承载着深厚的历史文化内涵，体现了中华民族的智慧和创造力。"

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
            1: ['刺绣', '剪纸', '陶瓷', '瓷器', '漆器', '编织', '雕刻', '手工', '工艺', '银饰', '年画', '泥人', '花布', '书法', '绘画', '建筑'],
            2: ['戏曲', '京剧', '昆曲', '皮影', '舞蹈', '音乐', '表演', '功夫', '武术', '杂技', '相声', '评书'],
            3: ['农耕', '酿造', '制茶', '纺织', '造纸', '印刷', '生产', '茶道', '茶文化'],
            4: ['传说', '神话', '故事', '风物', '地方', '民间传说'],
            5: ['人物', '英雄', '名人', '历史人物'],
            6: ['节日', '节庆', '春节', '端午', '中秋', '习俗', '民俗', '庙会', '元宵'],
            7: ['文学', '诗歌', '谚语', '歌谣', '民间文学', '诗词']
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
                    import urllib3
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    response = requests.get(url, headers=self.headers, timeout=15, verify=False)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    items = soup.find_all('div', class_='item') or soup.find_all('li', class_='project-item') or soup.find_all('a', class_='item')
                    
                    for item in items[:10]:
                        try:
                            title_elem = item.find('h3') or item.find('a', class_='title') or item.find('h2')
                            title = self.clean_text(title_elem.get_text()) if title_elem else None
                            
                            desc_elem = item.find('p') or item.find('div', class_='desc') or item.find('div', class_='content')
                            description = self.clean_text(desc_elem.get_text()) if desc_elem else ''
                            
                            img_elem = item.find('img')
                            img_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
                            
                            link_elem = item.find('a')
                            link = link_elem.get('href') if link_elem else None
                            
                            if title and len(title) > 2:
                                category_id = self.detect_category(title, description)
                                cover_image = None
                                if img_url:
                                    cover_image = self.download_image(img_url, f'ihchina_{category_id}')
                                
                                # 生成摘要
                                summary = self.generate_summary(title, description)
                                
                                data_list.append({
                                    'name': title[:200],
                                    'description': description[:1000] if description else f'{title}是中国的传统非物质文化遗产，具有重要的历史文化价值。',
                                    'summary': summary,
                                    'category_id': category_id,
                                    'source': '中国非遗网',
                                    'source_url': link,
                                    'cover_image': cover_image
                                })
                                logger.info(f'爬取成功: {title}')
                                time.sleep(0.5)
                        except Exception as e:
                            logger.error(f'解析条目失败: {e}')
                            continue
                except Exception as e:
                    logger.error(f'爬取页面失败 {url}: {e}')
                    continue
        except Exception as e:
            logger.error(f'爬取非遗网失败: {e}')
        
        logger.info(f'非遗网爬取完成，共 {len(data_list)} 条数据')
        return data_list

    def crawl_wikipedia(self):
        """爬取维基百科"""
        logger.info('开始爬取维基百科...')
        data_list = []
        
        keywords = ['中国传统文化', '中国非物质文化遗产', '中国传统节日', '中国民间艺术', '中国书法']
        
        for keyword in keywords:
            try:
                url = f"https://zh.wikipedia.org/wiki/{keyword}"
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                response = requests.get(url, headers=self.headers, timeout=15, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取内容
                content_div = soup.find('div', class_='mw-parser-output')
                if content_div:
                    paragraphs = content_div.find_all('p', recursive=False)[:5]
                    description = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    
                    if description:
                        # 提取图片
                        img = content_div.find('img')
                        cover_image = None
                        if img:
                            img_url = img.get('src')
                            if img_url and not img_url.startswith('http'):
                                img_url = 'https:' + img_url
                            cover_image = self.download_image(img_url, f'wiki_{keyword}')
                        
                        category_id = self.detect_category(keyword, description)
                        summary = self.generate_summary(keyword, description)
                        
                        data_list.append({
                            'name': keyword,
                            'description': description[:1000],
                            'summary': summary,
                            'category_id': category_id,
                            'source': '维基百科',
                            'source_url': url,
                            'cover_image': cover_image
                        })
                        logger.info(f'爬取维基百科成功: {keyword}')
                        
                time.sleep(1)
            except Exception as e:
                logger.error(f'爬取维基百科失败 {keyword}: {e}')
                continue
        
        logger.info(f'维基百科爬取完成，共 {len(data_list)} 条数据')
        return data_list

    def crawl_baidu_baike(self):
        """获取模拟数据（包含网络图片）"""
        logger.info('加载模拟数据...')
        
        # 先下载一些网络图片作为封面
        network_images = {}
        themes = ['chinese+tradition', 'chinese+art', 'chinese+festival', 'village', 'culture']
        for i, theme in enumerate(themes):
            try:
                img_url = f"https://source.unsplash.com/800x600/?{theme}"
                cover_image = self.download_image(img_url, f'mock_{i}')
                if cover_image:
                    network_images[theme] = cover_image
                time.sleep(0.5)
            except:
                pass
        
        mock_data = [
            {
                'name': '苏绣',
                'description': '苏绣是中国四大名绣之一，以针法精细、色彩雅致著称，主要产于江苏苏州地区。苏绣具有图案秀丽、构思巧妙、绣工细致、针法活泼、色彩清雅的独特风格，被誉为"东方艺术明珠"。苏绣历史悠久，已有两千多年的历史，是中国传统刺绣工艺的杰出代表。',
                'summary': '苏绣是中国四大名绣之一，以精细的针法、雅致的色彩和独特的艺术风格闻名于世，被誉为东方艺术明珠，是中华传统工艺的瑰宝。',
                'category_id': 1,
                'source': '中国非遗网',
                'origin': '江苏苏州',
                'heritage_level': '国家级',
                'cover_image': network_images.get('chinese+art')
            },
            {
                'name': '京剧',
                'description': '京剧，又称平剧、京戏，是中国五大戏曲剧种之一，被视为中国国粹。京剧以其独特的唱腔、精湛的表演和华丽的服饰著称，融合了唱、念、做、打等多种表演形式。京剧的角色分为生、旦、净、丑四大行当，每个行当都有其独特的表演程式和艺术特色。',
                'summary': '京剧是中国国粹，以独特的唱腔、精湛的表演和华丽的服饰著称，融合唱念做打于一体，是中华民族传统文化的瑰宝。',
                'category_id': 2,
                'source': '中国非遗网',
                'origin': '北京',
                'heritage_level': '世界级',
                'cover_image': network_images.get('chinese+tradition')
            },
            {
                'name': '少林功夫',
                'description': '少林功夫是中国武术中体系最庞大的门派，武功套路高达七百种以上，是中华武术的象征。少林功夫讲究禅武合一，体现了中华武术的精髓。少林功夫以实战威猛、博大精深而饮誉天下，是中华武术的重要代表。',
                'summary': '少林功夫是中国武术的杰出代表，套路繁多，讲究禅武合一，以实战威猛著称，体现了中华武术的精髓和博大精深。',
                'category_id': 2,
                'source': '百度百科',
                'origin': '河南登封',
                'heritage_level': '世界级',
                'cover_image': network_images.get('culture')
            },
            {
                'name': '端午节',
                'description': '端午节，又称端阳节、龙舟节、重午节、天中节等，是集拜神祭祖、祈福辟邪、欢庆娱乐和饮食为一体的民俗大节。端午节与春节、清明节、中秋节并称为中国四大传统节日。端午节有吃粽子、赛龙舟、挂艾草、饮雄黄酒等习俗。',
                'summary': '端午节是中国四大传统节日之一，以吃粽子、赛龙舟等习俗著称，承载着深厚的历史文化内涵和民族情感。',
                'category_id': 6,
                'source': '百度百科',
                'origin': '中国',
                'heritage_level': '世界级',
                'cover_image': network_images.get('chinese+festival')
            },
            {
                'name': '春节',
                'description': '春节，即中国农历新年，俗称"过年"，是中华民族最隆重的传统佳节。春节历史悠久，由上古时代岁首祈年祭祀演变而来。春节期间，人们会贴春联、放鞭炮、吃年夜饭、拜年、发红包等，寓意辞旧迎新、祈福纳祥。',
                'summary': '春节是中国最重要、最隆重的传统节日，以贴春联、放鞭炮、吃年夜饭等习俗著称，寓意辞旧迎新、祈福纳祥。',
                'category_id': 6,
                'source': '百度百科',
                'origin': '中国',
                'heritage_level': '国家级',
                'cover_image': network_images.get('village')
            },
            {
                'name': '嫦娥奔月',
                'description': '嫦娥奔月是中国上古时代神话传说故事，讲述了嫦娥被逢蒙所逼，无奈之下，吃下了仙药西王母赐给丈夫后羿的两粒不死之药后，飞到了月宫的事情。这个传说寄托了人们对美好生活的向往，也是中秋节的重要文化内涵。',
                'summary': '嫦娥奔月是中国古代著名的神话传说，讲述了嫦娥飞天的故事，寄托了人们对美好生活的向往，是中秋节的文化内涵之一。',
                'category_id': 4,
                'source': '百度百科',
                'origin': '中国',
                'heritage_level': '民间传说',
                'cover_image': network_images.get('chinese+tradition')
            },
            {
                'name': '牛郎织女',
                'description': '牛郎织女，为中国古代著名的汉族民间爱情故事，也是我国四大民间传说之一，从牵牛星、织女星的星名衍化而来。传说牛郎与织女因触犯天条被银河隔开，每年七夕才能在鹊桥相会，形成了七夕节的文化内涵。',
                'summary': '牛郎织女是中国四大民间传说之一，讲述了人神相恋的爱情故事，是七夕节的文化内涵，象征着忠贞不渝的爱情。',
                'category_id': 4,
                'source': '百度百科',
                'origin': '中国',
                'heritage_level': '民间传说',
                'cover_image': network_images.get('culture')
            },
            {
                'name': '年画',
                'description': '年画是中国画的一种，始于古代的"门神画"，中国民间艺术之一。年画是中国农村老百姓喜闻乐见的艺术形式，大都用于新年时张贴，含有祝福新年吉祥喜庆之意。年画题材丰富，色彩鲜艳，构图饱满，具有浓郁的地方特色。',
                'summary': '年画是中国民间艺术瑰宝，以祝福新年吉祥为主题，色彩鲜艳、构图饱满，是春节期间不可缺少的装饰艺术。',
                'category_id': 1,
                'source': '百度百科',
                'origin': '山东潍坊',
                'heritage_level': '国家级',
                'cover_image': network_images.get('chinese+art')
            },
            {
                'name': '皮影戏',
                'description': '皮影戏是中国民间古老的传统艺术，始于西汉，兴于唐朝。皮影戏又称"影子戏"或"灯影戏"，是一种以兽皮或纸板做成的人物剪影以表演故事的民间戏剧。艺人们在白色幕布后面，一边操纵影人，一边用当地流行的曲调讲述故事。',
                'summary': '皮影戏是中国古老的民间艺术，以兽皮或纸板剪影表演故事，始于西汉，是中国民间艺术的珍贵遗产。',
                'category_id': 2,
                'source': '百度百科',
                'origin': '陕西华县',
                'heritage_level': '国家级',
                'cover_image': network_images.get('chinese+tradition')
            },
            {
                'name': '剪纸',
                'description': '中国剪纸是一种用剪刀或刻刀在纸上剪刻花纹的民间艺术。剪纸艺术是汉族传统的民间工艺，它源远流长，经久不衰，是中国民间艺术中的瑰宝。剪纸常用于节庆装饰，寓意吉祥，寄托了人们对美好生活的向往。',
                'summary': '剪纸是中国民间艺术的瑰宝，以纸为材料剪刻花纹，寓意吉祥，寄托美好愿望，是中国传统民间工艺的代表。',
                'category_id': 1,
                'source': '百度百科',
                'origin': '山西静乐',
                'heritage_level': '国家级',
                'cover_image': network_images.get('chinese+art')
            },
            {
                'name': '景德镇陶瓷',
                'description': '景德镇陶瓷是中国陶瓷艺术的杰出代表，以"白如玉、明如镜、薄如纸、声如磬"的独特风格著称于世。景德镇有"瓷都"之称，制瓷历史悠久，技艺精湛，是中国陶瓷文化的重要象征。',
                'summary': '景德镇陶瓷以"白如玉、明如镜、薄如纸、声如磬"著称，是中华陶瓷文化的杰出代表，享有"瓷都"之美誉。',
                'category_id': 1,
                'source': '百度百科',
                'origin': '江西景德镇',
                'heritage_level': '世界级',
                'cover_image': network_images.get('chinese+tradition')
            },
            {
                'name': '中国书法',
                'description': '中国书法是一门古老的汉字书写艺术，被誉为"无言的诗，无行的舞；无图的画，无声的乐"。书法是中国特有的艺术形式，以汉字为载体，通过笔墨纸砚表现出独特的艺术魅力，是中华文化的重要组成部分。',
                'summary': '中国书法是汉字书写艺术，被誉为无言的诗、无行的舞、无图的画、无声的乐，是中华文化的重要象征。',
                'category_id': 1,
                'source': '百度百科',
                'origin': '中国',
                'heritage_level': '世界级',
                'cover_image': network_images.get('chinese+tradition')
            }
        ]
        return mock_data

    def crawl_network_images(self):
        """从免费图片网站获取乡村文化相关图片"""
        logger.info('开始爬取网络图片...')
        data_list = []
        
        # 使用Unsplash Source API获取免费图片
        culture_themes = [
            {'keyword': 'chinese+tradition', 'name': '中国传统文化艺术', 'category': 1, 'desc': '中国传统文化源远流长，包含诗词歌赋、琴棋书画等多种艺术形式，是中华民族智慧的结晶，承载着深厚的历史文化内涵。'},
            {'keyword': 'chinese+festival', 'name': '中国传统节日庆典', 'category': 6, 'desc': '中国传统节日丰富多彩，春节、元宵、端午、中秋等节日承载着深厚的文化内涵和民族情感，是中华民族的重要文化遗产。'},
            {'keyword': 'chinese+craft', 'name': '传统手工艺', 'category': 3, 'desc': '中国传统手工艺历史悠久，技艺精湛，包括陶瓷制作、丝绸织造、漆器工艺等，是中华文明的瑰宝，体现了劳动人民的智慧。'},
            {'keyword': 'village+life', 'name': '乡村生活文化', 'category': 4, 'desc': '乡村文化是中华文化的重要组成部分，包含农耕文化、民俗风情、民间传说等丰富内容，展现了浓郁的乡土气息和人文情怀。'},
            {'keyword': 'tea+ceremony', 'name': '中国茶文化', 'category': 3, 'desc': '中国茶文化源远流长，茶道讲究和、静、怡、真，是中国人待客之道和修身养性的重要方式，蕴含着深厚的哲学思想。'},
            {'keyword': 'ancient+architecture', 'name': '传统建筑艺术', 'category': 1, 'desc': '中国传统建筑风格独特，讲究天人合一，以木结构为主，飞檐斗拱、雕梁画栋，展现了高超的建筑技艺和审美情趣。'},
        ]
        
        for theme in culture_themes:
            try:
                # 使用Unsplash Source API获取图片
                img_url = f"https://source.unsplash.com/800x600/?{theme['keyword']}"
                
                # 下载并处理图片
                cover_image = self.download_image(img_url, f"network_{theme['category']}")
                
                if cover_image:
                    summary = self.generate_summary(theme['name'], theme['desc'])
                    
                    data_list.append({
                        'name': theme['name'],
                        'description': theme['desc'],
                        'summary': summary,
                        'category_id': theme['category'],
                        'source': 'Unsplash',
                        'origin': '中国',
                        'heritage_level': '传统文化',
                        'cover_image': cover_image
                    })
                    logger.info(f"添加网络图片: {theme['name']}")
                    time.sleep(1)  # 避免请求过快
                    
            except Exception as e:
                logger.error(f"获取网络图片失败 {theme['name']}: {e}")
                continue
        
        logger.info(f'网络图片爬取完成，共 {len(data_list)} 条')
        return data_list

    def crawl_all(self):
        """爬取所有数据源"""
        all_data = []
        
        # 1. 使用模拟数据（保证有数据）
        mock_data = self.crawl_baidu_baike()
        all_data.extend(mock_data)
        logger.info(f'模拟数据: {len(mock_data)} 条数据')
        
        # 2. 尝试爬取网络图片
        try:
            network_data = self.crawl_network_images()
            all_data.extend(network_data)
            logger.info(f'网络图片: {len(network_data)} 条数据')
        except Exception as e:
            logger.warning(f'网络图片爬取失败: {e}')
        
        # 3. 尝试爬取维基百科
        try:
            wiki_data = self.crawl_wikipedia()
            all_data.extend(wiki_data)
            logger.info(f'维基百科: {len(wiki_data)} 条数据')
        except Exception as e:
            logger.warning(f'维基百科爬取失败: {e}')
        
        # 4. 尝试爬取非遗网（如果网络好）
        try:
            ihchina_data = self.crawl_ihchina()
            all_data.extend(ihchina_data)
            logger.info(f'中国非遗网: {len(ihchina_data)} 条数据')
        except Exception as e:
            logger.warning(f'非遗网爬取失败: {e}')
        
        logger.info(f'总共爬取 {len(all_data)} 条数据')
        return all_data
