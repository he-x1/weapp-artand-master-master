"""
文本摘要生成服务
使用 BERT 模型生成高质量的文本摘要
"""
import re
from loguru import logger

# 尝试导入摘要生成模块
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning('未安装transformers库，将使用规则生成摘要')

# 全局摘要器实例
_summarizer = None
_tokenizer = None


def init_summarizer():
    """初始化摘要生成器"""
    global _summarizer, _tokenizer

    if not HAS_TRANSFORMERS:
        return None

    try:
        # 使用中文摘要模型
        model_name = "uer/bart-base-chinese-cluecorpussmall"
        logger.info(f'正在加载摘要模型: {model_name}')

        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _summarizer = pipeline(
            "summarization",
            model=model_name,
            tokenizer=_tokenizer,
            device=-1  # 使用CPU
        )
        logger.info('摘要模型加载完成')
        return _summarizer
    except Exception as e:
        logger.warning(f'加载中文摘要模型失败: {e}，尝试使用备用模型')
        try:
            # 备用模型
            model_name = "sshleifer/distilbart-cnn-12-6"
            _summarizer = pipeline("summarization", model=model_name, device=-1)
            logger.info('备用摘要模型加载完成')
            return _summarizer
        except Exception as e2:
            logger.error(f'加载备用摘要模型也失败: {e2}')
            return None


def get_summarizer():
    """获取摘要生成器实例"""
    global _summarizer
    if _summarizer is None and HAS_TRANSFORMERS:
        _summarizer = init_summarizer()
    return _summarizer


def clean_text(text):
    """清理文本"""
    if not text:
        return ''
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？、；：""''（）【】《》]', '', text)
    return text.strip()


def extract_key_sentences(text, max_sentences=3):
    """提取关键句子"""
    if not text:
        return []

    # 分句
    sentences = re.split(r'[。！？\n]', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

    # 简单的关键词权重
    keywords = [
        '传统', '文化', '历史', '艺术', '技艺', '民间', '传承',
        '特色', '著名', '重要', '代表', '国家级', '世界级',
        '起源', '发展', '特点', '价值', '意义'
    ]

    scored_sentences = []
    for s in sentences:
        score = 0
        for kw in keywords:
            if kw in s:
                score += 1
        # 长度适中的句子得分更高
        if 20 < len(s) < 100:
            score += 1
        scored_sentences.append((s, score))

    # 排序并返回
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scored_sentences[:max_sentences]]


def generate_summary_by_rules(title, description, max_length=150):
    """基于规则生成摘要"""
    if not description:
        return f"{title}是中国传统文化的重要组成部分，承载着深厚的历史文化内涵。"

    # 清理文本
    clean_desc = clean_text(description)

    # 提取关键句子
    key_sentences = extract_key_sentences(clean_desc, 3)

    if key_sentences:
        summary = '。'.join(key_sentences)
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'
        return summary

    # 如果无法提取关键句子，截取前部分
    if len(clean_desc) > max_length:
        return clean_desc[:max_length] + '...'

    return clean_desc


def generate_summary_by_model(text, max_length=150, min_length=50):
    """使用模型生成摘要"""
    summarizer = get_summarizer()

    if not summarizer:
        return None

    try:
        # 清理文本
        clean_desc = clean_text(text)

        if len(clean_desc) < min_length:
            return None

        # 截取过长的文本
        if len(clean_desc) > 1024:
            clean_desc = clean_desc[:1024]

        # 生成摘要
        result = summarizer(
            clean_desc,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            truncation=True
        )

        if result and len(result) > 0:
            return result[0]['summary_text']

    except Exception as e:
        logger.error(f'模型生成摘要失败: {e}')

    return None


def generate_summary(title, description, max_length=150):
    """
    生成文本摘要
    优先使用模型，失败则使用规则

    Args:
        title: 标题
        description: 描述内容
        max_length: 最大长度

    Returns:
        生成的摘要文本
    """
    # 组合标题和描述
    full_text = f"{title}。{description}" if description else title

    # 尝试使用模型生成
    if HAS_TRANSFORMERS and len(full_text) > 100:
        model_summary = generate_summary_by_model(full_text, max_length)
        if model_summary:
            logger.info(f'使用模型生成摘要: {title}')
            return model_summary

    # 使用规则生成
    logger.info(f'使用规则生成摘要: {title}')
    return generate_summary_by_rules(title, description, max_length)


# 文化领域专用摘要模板
CATEGORY_SUMMARY_TEMPLATES = {
    1: '传统手工',  # 传统手工
    2: '表演艺术',  # 表演艺术
    3: '生产技艺',  # 生产技艺
    4: '风物传说',  # 风物传说
    5: '人物传说',  # 人物传说
    6: '节庆习俗',  # 节庆习俗
    7: '民间文学',  # 民间文学
}


def generate_cultural_summary(title, description, category_id=1, origin=None, heritage_level=None):
    """
    生成文化内容专用摘要
    包含更丰富的上下文信息

    Args:
        title: 标题
        description: 描述
        category_id: 分类ID
        origin: 产地
        heritage_level: 遗产级别

    Returns:
        格式化的摘要
    """
    # 基础摘要
    base_summary = generate_summary(title, description, max_length=120)

    # 添加上下文信息
    context_parts = []

    category_name = CATEGORY_SUMMARY_TEMPLATES.get(category_id, '传统文化')

    if origin and origin not in base_summary:
        context_parts.append(f"源自{origin}")

    if heritage_level and heritage_level not in base_summary:
        context_parts.append(f"属{heritage_level}非物质文化遗产")

    if context_parts:
        context = '，'.join(context_parts)
        return f"{base_summary}。{context}。"

    return base_summary if base_summary.endswith('。') else f"{base_summary}。"


if __name__ == '__main__':
    # 测试
    test_cases = [
        {
            'title': '苏绣',
            'description': '苏绣是中国四大名绣之一，以针法精细、色彩雅致著称，主要产于江苏苏州地区。苏绣具有图案秀丽、构思巧妙、绣工细致、针法活泼、色彩清雅的独特风格，被誉为"东方艺术明珠"。',
            'category_id': 1,
            'origin': '江苏苏州',
            'heritage_level': '国家级'
        },
        {
            'title': '京剧',
            'description': '京剧，又称平剧、京戏，是中国五大戏曲剧种之一，被视为中国国粹。京剧以其独特的唱腔、精湛的表演和华丽的服饰著称，融合了唱、念、做、打等多种表演形式。',
            'category_id': 2,
            'origin': '北京',
            'heritage_level': '世界级'
        }
    ]

    for case in test_cases:
        summary = generate_cultural_summary(**case)
        print(f"标题: {case['title']}")
        print(f"摘要: {summary}")
        print("-" * 50)
