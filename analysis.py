import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import jieba
import jieba.analyse
from wordcloud import WordCloud
from snownlp import SnowNLP
import warnings
from datetime import datetime
import os
import yaml
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class BilibiliTextAnalyzer:
    def __init__(self, config_path="config.yaml"):
        self.comments_data = []
        self.contents_data = []
        self.creators_data = []
        self.config = self._load_config(config_path)
  
        # 精简停用词列表，保留更多有意义词汇
        self.stop_words = self._load_stop_words()

        # 添加自定义词典
        self._add_custom_words()

    def _load_config(self, config_path):
        """加载配置文件"""
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        else:
            print(f"⚠️ 未找到配置文件 {config_path}，将使用默认参数")
            return {}

    def _load_stop_words(self):
        """加载停用词列表 - 精简版本"""
        # 只保留最核心的停用词，减少过度过滤
        basic_stop_words = {
            # 最基础的无意义词
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '都', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
            '还', '这', '那', '把', '被', '从', '与', '及', '以', '为', '而', '或',
            '但', '可', '能', '将', '已', '所', '之', '其', '等', '如', '比',
            '再', '还是', '这个', '那个', '什么', '怎么', '为什么', '哪里',
            
            # B站平台相关无意义词（减少）
            '回复', '评论', '关注', '点赞', '收藏', '分享', '弹幕', '投币',
            '三连', '一键三连', 'up', 'UP', 'up主', 'UP主',
            
            # 明显的无意义表达
            '哈哈', '哈哈哈', '嘻嘻', '呵呵', '嗯', '啊', '哦', '额',
            'doge', 'hhh', 'hhhh', 'emmm', '6666', '666',
            
            # 过于通用的词汇
            '东西', '地方', '时间', '空间', '机会', '可能性',
            '好的', '不错', '挺好', '很好', '太好了', '觉得', 
            '可能', '还有', '需要', '时候', '事情', '问题', 
            '方法', '不会', '应该', '可以', '想要', '知道', 
            '了解', '只能', '希望', '相信', '期待', '喜欢', 
            '爱', '视频', '内容', '创作', '作品', '分享',
            '不能', '不行', '不可以', '不想', '不喜欢',
        }
        
        return basic_stop_words
    
    def _add_custom_words(self):
        """添加自定义词典"""
        # 经济金融相关专业词汇
        economic_words = [
            '宏观经济', '微观经济', '货币政策', '财政政策', '通胀', '通缩', 'GDP',
            '消费升级', '消费降级', '产业升级', '供给侧改革', '需求侧管理',
            '资本市场', '股票市场', '债券市场', '外汇市场', '期货市场',
            '利率', '汇率', '通胀率', '失业率', '增长率', '经济危机', '金融危机',
            '房地产', '股票', '基金', '债券', '期货', '外汇', '投资', '理财',
            '央行', '银行', '保险', '证券', '信贷', '贷款', '存款', '储蓄'
        ]
        
        # B站相关专业词汇
        bilibili_words = [
            '哔哩哔哩', 'bilibili', 'B站', '鬼畜', '番剧', '纪录片', '生活区',
            '科技区', '游戏区', '音乐区', '舞蹈区', '影视区', '知识区'
        ]
        
        # 社会经济热词
        social_economic_words = [
            '内卷', '躺平', '996', '007', '打工人', '社畜', '佛系', '摆烂',
            '消费主义', '极简主义', '断舍离', '精神内耗', '社会达尔文',
            '阶级固化', '社会流动', '教育内卷', '就业压力', '生育率',
            '老龄化', '少子化', '人口红利', '产业转型', '数字经济'
        ]
        
        # 添加到jieba词典
        for word in economic_words + bilibili_words + social_economic_words:
            jieba.add_word(word)
    
    def load_data(self):
        """加载数据"""
        try:
            with open('data/search_comments_2025-07-14.json', 'r', encoding='utf-8') as f:
                self.comments_data = json.load(f)
            with open('data/search_contents_2025-07-14.json', 'r', encoding='utf-8') as f:
                self.contents_data = json.load(f)
            with open('data/search_creators_2025-07-14.json', 'r', encoding='utf-8') as f:
                self.creators_data = json.load(f)
            print("✅ 数据加载成功")
            print(f"评论数据: {len(self.comments_data)} 条")
            print(f"视频数据: {len(self.contents_data)} 条")
            print(f"创作者数据: {len(self.creators_data)} 条")
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
    
    def clean_text(self, text):
        """清理文本数据 - 保留更多有用信息"""
        if not text or pd.isna(text):
            return ""
        
        text = str(text)
        
        # 移除URL链接
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 移除邮箱
        text = re.sub(r'\S+@\S+', '', text)
        
        # 移除@用户名
        text = re.sub(r'@[^\s]+', '', text)
        
        # 移除#话题#
        text = re.sub(r'#[^#]+#', '', text)
        
        # 保留有意义的数字组合（年份、金额等）
        # 只移除单独的纯数字，保留与文字组合的数字
        text = re.sub(r'\b\d{1,3}\b(?!\d)', '', text)  # 只移除1-3位的独立数字
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def is_meaningful_word(self, word):
        """判断词语是否有意义 - 放宽条件"""
        # 长度过滤 - 放宽到1个字符也可以（如"美"、"中"等）
        if len(word) < 1:
            return False
        
        # 对于单字符，只保留有意义的
        if len(word) == 1:
            meaningful_single_chars = {
                '中', '美', '日', '韩', '欧', '俄', '印', '英', '法', '德', '澳',
                '钱', '房', '车', '股', '债', '金', '银', '油', '气', '煤', '铁',
                '工', '农', '商', '学', '医', '法', '理', '文', '史', '哲'
            }
            return word in meaningful_single_chars
        
        # 停用词过滤
        if word.lower() in self.stop_words:
            return False
        
        # 纯数字过滤（但保留年份等）
        if word.isdigit():
            # 保留年份
            if len(word) == 4 and word.startswith(('19', '20')):
                return True
            # 保留大额数字（可能是金额、播放量等）
            if len(word) >= 4:
                return True
            return False
        
        # 重复字符过滤（如：哈哈哈、呵呵呵）
        if len(set(word)) == 1 and len(word) > 2:
            return False
        
        # 明显的网络用语过滤（减少数量）
        obvious_internet_slang = {
            'hhh', 'hhhh', 'emmm', 'awsl', 'orz', 'qaq', 'tql', 'yyds',
            '绝绝子', '爱了爱了', '冲冲冲', '杀杀杀', '呜呜呜', '嘤嘤嘤',
            '笑哭', '捂脸', '狗头', '滑稽'
        }
        if word.lower() in obvious_internet_slang:
            return False
        
        return True
    
    def extract_keywords_advanced(self, text_list, top_k=30):
        """高级关键词提取 - 多种方法组合"""
        # 将 top_k 参数传递给方法时，优先使用 config.yaml
        top_k = self.config.get("analysis", {}).get("top_keywords", top_k)

        # 清理和合并文本
        cleaned_texts = []
        for text in text_list:
            if text:
                cleaned = self.clean_text(text)
                if cleaned:
                    cleaned_texts.append(cleaned)
        
        if not cleaned_texts:
            return []
        
        combined_text = ' '.join(cleaned_texts)
        
        # 方法1: TF-IDF (权重较高)
        tfidf_keywords = jieba.analyse.extract_tags(
            combined_text, 
            topK=top_k*2,
            withWeight=True,
            allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'vn', 'an', 'v', 'a', 'nrt')
        )
        
        # 方法2: TextRank (权重中等)
        textrank_keywords = jieba.analyse.textrank(
            combined_text, 
            topK=top_k*2,
            withWeight=True,
            allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'vn', 'an', 'v', 'a', 'nrt')
        )
        
        # 方法3: 词频统计 (权重较低)
        words = jieba.lcut(combined_text)
        word_freq = Counter([w for w in words if len(w) > 1 and self.is_meaningful_word(w)])
        freq_keywords = [(word, freq/len(words)) for word, freq in word_freq.most_common(top_k*2)]
        
        # 合并结果并加权
        keyword_scores = {}
        
        # TF-IDF权重 * 0.5
        for word, weight in tfidf_keywords:
            if self.is_meaningful_word(word):
                keyword_scores[word] = keyword_scores.get(word, 0) + weight * 0.5
        
        # TextRank权重 * 0.3
        for word, weight in textrank_keywords:
            if self.is_meaningful_word(word):
                keyword_scores[word] = keyword_scores.get(word, 0) + weight * 0.3
        
        # 词频权重 * 0.2
        for word, weight in freq_keywords:
            if self.is_meaningful_word(word):
                keyword_scores[word] = keyword_scores.get(word, 0) + weight * 0.2
        
        # 排序并返回
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_keywords[:top_k]
    
    def extract_keywords(self, text_list, top_k=20, method='tfidf'):
        """提取关键词 - 兼容原接口"""
        # 将 top_k 参数传递给方法时，优先使用 config.yaml
        top_k = self.config.get("analysis", {}).get("top_keywords", top_k)

        if method == 'advanced':
            return self.extract_keywords_advanced(text_list, top_k)
        
        # 清理和合并文本
        cleaned_texts = []
        for text in text_list:
            if text:
                cleaned = self.clean_text(text)
                if cleaned:
                    cleaned_texts.append(cleaned)
        
        if not cleaned_texts:
            return []
        
        combined_text = ' '.join(cleaned_texts)
        
        if method == 'tfidf':
            # 使用TF-IDF方法 - 放宽词性限制
            keywords = jieba.analyse.extract_tags(
                combined_text, 
                topK=top_k*3,  # 提取更多，然后过滤
                withWeight=True,
                allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'vn', 'an', 'v', 'a', 'nrt', 'ad', 'vd')
            )
        else:
            # 使用TextRank方法
            keywords = jieba.analyse.textrank(
                combined_text, 
                topK=top_k*3, 
                withWeight=True,
                allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'vn', 'an', 'v', 'a', 'nrt', 'ad', 'vd')
            )
        
        # 过滤无意义词汇
        meaningful_keywords = []
        for word, weight in keywords:
            if self.is_meaningful_word(word):
                meaningful_keywords.append((word, weight))
        
        # 返回前top_k个有意义的关键词
        return meaningful_keywords[:top_k]
    
    def sentiment_analysis(self, text):
        """情绪分析"""
        if not text or pd.isna(text):
            return 0.5, "中性"
        try:
            s = SnowNLP(str(text))
            sentiment_score = s.sentiments
            # 使用 config.yaml 的阈值
            pos_thres = self.config.get("analysis", {}).get("positive_threshold", 0.6)
            neg_thres = self.config.get("analysis", {}).get("negative_threshold", 0.4)
            if sentiment_score > pos_thres:
                sentiment_label = "积极"
            elif sentiment_score < neg_thres:
                sentiment_label = "消极"
            else:
                sentiment_label = "中性"
            return sentiment_score, sentiment_label
        except:
            return 0.5, "中性"
    
    def analyze_comments(self):
        """分析评论数据"""
        print("\n=== 评论文本分析 ===")
        if not self.comments_data:
            print("❌ 没有评论数据")
            return None

        df_comments = pd.DataFrame(self.comments_data)
        total_comments = len(df_comments)
        valid_comments = df_comments['content'].notna().sum()
        print(f"总评论数: {total_comments}")
        print(f"有效评论数: {valid_comments}")

        df_comments['content_length'] = df_comments['content'].astype(str).str.len()
        print(f"平均评论长度: {df_comments['content_length'].mean():.2f} 字符")
        print(f"最长评论: {df_comments['content_length'].max()} 字符")
        print(f"最短评论: {df_comments['content_length'].min()} 字符")

        # === 使用配置参数 ===
        sample_size = self.config.get("analysis", {}).get("comment_sample_size", 5000)
        top_k = self.config.get("analysis", {}).get("top_keywords", 20)

        # 情绪分析
        print("\n--- 评论情绪分析 ---")
        sentiments = []
        sentiment_labels = []
        sample_size = min(sample_size, len(df_comments))
        sample_comments = df_comments.sample(n=sample_size)['content'].tolist()
        for comment in sample_comments:
            score, label = self.sentiment_analysis(comment)
            sentiments.append(score)
            sentiment_labels.append(label)
        sentiment_counts = Counter(sentiment_labels)
        print(f"积极评论: {sentiment_counts['积极']} ({sentiment_counts['积极']/len(sentiment_labels)*100:.1f}%)")
        print(f"中性评论: {sentiment_counts['中性']} ({sentiment_counts['中性']/len(sentiment_labels)*100:.1f}%)")
        print(f"消极评论: {sentiment_counts['消极']} ({sentiment_counts['消极']/len(sentiment_labels)*100:.1f}%)")
        print(f"平均情绪得分: {np.mean(sentiments):.3f}")

        # 关键词提取
        print("\n--- 评论关键词分析 ---")
        comment_texts = [str(comment) for comment in df_comments['content'].dropna()]
        print("🔍 使用高级组合方法提取关键词:")
        advanced_keywords = self.extract_keywords_advanced(comment_texts, top_k=top_k)
        for i, (word, weight) in enumerate(advanced_keywords[:15], 1):
            print(f"{i:2d}. {word}: {weight:.4f}")

        print("\n🔍 使用TF-IDF方法提取关键词:")
        tfidf_keywords = self.extract_keywords(comment_texts, top_k=top_k, method='tfidf')
        for i, (word, weight) in enumerate(tfidf_keywords[:15], 1):
            print(f"{i:2d}. {word}: {weight:.4f}")

        print("\n🔍 使用TextRank方法提取关键词:")
        textrank_keywords = self.extract_keywords(comment_texts, top_k=top_k, method='textrank')
        for i, (word, weight) in enumerate(textrank_keywords[:15], 1):
            print(f"{i:2d}. {word}: {weight:.4f}")

        like_counts = pd.to_numeric(df_comments['like_count'], errors='coerce').fillna(0)
        print(f"\n--- 点赞数统计 ---")
        print(f"平均点赞数: {like_counts.mean():.2f}")
        print(f"最高点赞数: {like_counts.max()}")
        print(f"点赞数中位数: {like_counts.median()}")

        return {
            'sentiment_distribution': dict(sentiment_counts),
            'sentiment_scores': sentiments,
            'advanced_keywords': advanced_keywords,
            'tfidf_keywords': tfidf_keywords,
            'textrank_keywords': textrank_keywords,
            'keywords': advanced_keywords,
            'basic_stats': {
                'total': int(total_comments),
                'valid': int(valid_comments),
                'avg_length': float(df_comments['content_length'].mean()),
                'max_length': int(df_comments['content_length'].max()),
                'min_length': int(df_comments['content_length'].min()),
                'avg_likes': float(like_counts.mean()),
                'max_likes': int(like_counts.max()),
                'median_likes': float(like_counts.median())
            }
        }
    
    def analyze_video_content(self):
        """分析视频内容"""
        print("\n=== 视频内容分析 ===")
        
        if not self.contents_data:
            print("❌ 没有视频内容数据")
            return None
        
        df_contents = pd.DataFrame(self.contents_data)
        
        # 基本统计
        print(f"总视频数: {len(df_contents)}")
        
        # 播放量统计
        play_counts = pd.to_numeric(df_contents['video_play_count'], errors='coerce').fillna(0)
        print(f"平均播放量: {play_counts.mean():.0f}")
        print(f"最高播放量: {play_counts.max():.0f}")
        print(f"播放量中位数: {play_counts.median():.0f}")
        
        # 标题分析
        print("\n--- 视频标题分析 ---")
        titles = df_contents['title'].dropna().tolist()
        title_keywords = self.extract_keywords_advanced(titles, top_k=20)
        
        print("标题热门关键词:")
        for i, (word, weight) in enumerate(title_keywords[:15], 1):
            print(f"{i:2d}. {word}: {weight:.4f}")
        
        # 描述分析
        print("\n--- 视频描述分析 ---")
        descriptions = df_contents['desc'].dropna().tolist()
        desc_keywords = self.extract_keywords_advanced(descriptions, top_k=20)
        
        print("描述热门关键词:")
        for i, (word, weight) in enumerate(desc_keywords[:15], 1):
            print(f"{i:2d}. {word}: {weight:.4f}")
        
        # 标题情绪分析
        print("\n--- 标题情绪分析 ---")
        title_sentiments = []
        title_sentiment_labels = []
        
        for title in titles:
            score, label = self.sentiment_analysis(title)
            title_sentiments.append(score)
            title_sentiment_labels.append(label)
        
        title_sentiment_counts = Counter(title_sentiment_labels)
        print(f"积极标题: {title_sentiment_counts['积极']} ({title_sentiment_counts['积极']/len(title_sentiment_labels)*100:.1f}%)")
        print(f"中性标题: {title_sentiment_counts['中性']} ({title_sentiment_counts['中性']/len(title_sentiment_labels)*100:.1f}%)")
        print(f"消极标题: {title_sentiment_counts['消极']} ({title_sentiment_counts['消极']/len(title_sentiment_labels)*100:.1f}%)")
        
        return {
            'title_keywords': title_keywords,
            'desc_keywords': desc_keywords,
            'title_sentiment': dict(title_sentiment_counts),
            'title_sentiment_scores': title_sentiments,
            'video_stats': {
                'total_videos': int(len(df_contents)),
                'avg_play_count': float(play_counts.mean()),
                'max_play_count': int(play_counts.max()),
                'median_play_count': float(play_counts.median())
            }
        }
    
    def analyze_creators(self):
        """分析创作者数据"""
        print("\n=== 创作者分析 ===")
        
        if not self.creators_data:
            print("❌ 没有创作者数据")
            return None
        
        df_creators = pd.DataFrame(self.creators_data)
        
        # 性别分布
        gender_dist = df_creators['sex'].value_counts()
        print("--- 创作者性别分布 ---")
        for gender, count in gender_dist.items():
            print(f"{gender}: {count} ({count/len(df_creators)*100:.1f}%)")
        
        # 粉丝数分析
        fan_counts = pd.to_numeric(df_creators['total_fans'], errors='coerce').fillna(0)
        print(f"\n--- 粉丝数统计 ---")
        print(f"平均粉丝数: {fan_counts.mean():.0f}")
        print(f"最高粉丝数: {fan_counts.max():.0f}")
        print(f"粉丝数中位数: {fan_counts.median():.0f}")
        
        # 个性签名关键词分析
        print("\n--- 个性签名关键词 ---")
        signs = df_creators['sign'].dropna().tolist()
        sign_keywords = self.extract_keywords_advanced(signs, top_k=15)
        
        for i, (word, weight) in enumerate(sign_keywords[:15], 1):
            print(f"{i:2d}. {word}: {weight:.4f}")
        
        return {
            'gender_distribution': dict(gender_dist),
            'fan_stats': {
                'avg_fans': float(fan_counts.mean()),
                'max_fans': int(fan_counts.max()),
                'median_fans': float(fan_counts.median())
            },
            'sign_keywords': sign_keywords
        }
    
    def generate_wordcloud(self, keywords, title="词云图", save_path=None):
        """生成词云图"""
        if not keywords:
            print("❌ 没有关键词数据，无法生成词云")
            return
        word_freq = {word: weight for word, weight in keywords}
        # 读取词云配置
        wc_cfg = self.config.get("analysis", {}).get("wordcloud", {})
        width = wc_cfg.get("width", 1000)
        height = wc_cfg.get("height", 500)
        max_words = wc_cfg.get("max_words", 150)
        background_color = wc_cfg.get("background_color", "white")
        colormap = wc_cfg.get("colormap", "viridis")
        wordcloud = WordCloud(
            font_path='C:/Windows/Fonts/simhei.ttf',
            width=width,
            height=height,
            background_color=background_color,
            max_words=max_words,
            colormap=colormap,
            prefer_horizontal=0.7
        ).generate_from_frequencies(word_freq)
        plt.figure(figsize=(15, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title(title, fontsize=18)
        plt.axis('off')
        plt.tight_layout()
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 词云图已保存到: {save_path}")
        plt.show()
    
    def create_visualizations(self, comment_analysis, content_analysis, creator_analysis):
        """创建可视化图表"""
        fig, axes = plt.subplots(2, 3, figsize=(20, 14))
        
        # 1. 评论情绪分布
        if comment_analysis and 'sentiment_distribution' in comment_analysis:
            sentiment_data = comment_analysis['sentiment_distribution']
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            axes[0, 0].pie(sentiment_data.values(), labels=sentiment_data.keys(), 
                          autopct='%1.1f%%', colors=colors)
            axes[0, 0].set_title('评论情绪分布', fontsize=14)
        
        # 2. 评论长度分布
        if self.comments_data:
            df_comments = pd.DataFrame(self.comments_data)
            df_comments['content_length'] = df_comments['content'].astype(str).str.len()
            axes[0, 1].hist(df_comments['content_length'], bins=50, alpha=0.7, color='skyblue')
            axes[0, 1].set_title('评论长度分布', fontsize=14)
            axes[0, 1].set_xlabel('评论长度 (字符)')
            axes[0, 1].set_ylabel('频次')
        
        # 3. 创作者性别分布
        if creator_analysis and 'gender_distribution' in creator_analysis:
            gender_data = creator_analysis['gender_distribution']
            axes[0, 2].bar(gender_data.keys(), gender_data.values(), color=['pink', 'lightblue', 'lightgreen'])
            axes[0, 2].set_title('创作者性别分布', fontsize=14)
            axes[0, 2].set_ylabel('人数')
        
        # 4. 视频播放量分布
        if self.contents_data:
            df_contents = pd.DataFrame(self.contents_data)
            play_counts = pd.to_numeric(df_contents['video_play_count'], errors='coerce').dropna()
            axes[1, 0].hist(play_counts, bins=30, alpha=0.7, color='lightgreen')
            axes[1, 0].set_title('视频播放量分布', fontsize=14)
            axes[1, 0].set_xlabel('播放量')
            axes[1, 0].set_ylabel('频次')
        
        # 5. 热门关键词
        if comment_analysis and 'keywords' in comment_analysis:
            keywords = comment_analysis['keywords'][:12]  # 显示更多关键词
            words = [word for word, _ in keywords]
            weights = [weight for _, weight in keywords]
            
            y_pos = range(len(words))
            axes[1, 1].barh(y_pos, weights, color='orange')
            axes[1, 1].set_yticks(y_pos)
            axes[1, 1].set_yticklabels(words)
            axes[1, 1].set_title('评论热门关键词', fontsize=14)
            axes[1, 1].set_xlabel('权重')
        
        # 6. 标题情绪分布
        if content_analysis and 'title_sentiment' in content_analysis:
            title_sentiment = content_analysis['title_sentiment']
            axes[1, 2].pie(title_sentiment.values(), labels=title_sentiment.keys(), 
                          autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99'])
            axes[1, 2].set_title('视频标题情绪分布', fontsize=14)
        
        plt.tight_layout()
        
        # 保存图表
        save_path = 'results/analysis_charts.png'
        os.makedirs('results', exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"💾 分析图表已保存到: {save_path}")
        
        plt.show()
    
    def convert_to_serializable(self, obj):
        """将对象转换为JSON可序列化的格式"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self.convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_to_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return [self.convert_to_serializable(item) for item in obj]
        else:
            return obj
    
    def comprehensive_analysis(self):
        """综合分析"""
        print("🚀 开始综合文本分析...")
        
        # 加载数据
        self.load_data()
        
        # 分析评论
        comment_analysis = self.analyze_comments()
        
        # 分析视频内容
        content_analysis = self.analyze_video_content()
        
        # 分析创作者
        creator_analysis = self.analyze_creators()
        
        # 生成可视化
        print("\n=== 生成可视化图表 ===")
        self.create_visualizations(comment_analysis, content_analysis, creator_analysis)
        
        # 生成词云图
        if comment_analysis and 'keywords' in comment_analysis:
            print("\n=== 生成评论词云图 ===")
            self.generate_wordcloud(comment_analysis['keywords'], 
                                  "评论关键词词云", 
                                  "results/comment_wordcloud.png")
        
        if content_analysis and 'title_keywords' in content_analysis:
            print("\n=== 生成标题词云图 ===")
            self.generate_wordcloud(content_analysis['title_keywords'], 
                                  "视频标题关键词词云",
                                  "results/title_wordcloud.png")
        
        print("\n✅ 分析完成！")
        
        return {
            'comment_analysis': comment_analysis,
            'content_analysis': content_analysis,
            'creator_analysis': creator_analysis
        }

def main():
    """主函数"""
    analyzer = BilibiliTextAnalyzer()
    results = analyzer.comprehensive_analysis()
    
    # 保存分析结果
    try:
        # 转换为可序列化的格式
        serializable_results = analyzer.convert_to_serializable(results)
        
        # 保存更多关键词
        if 'comment_analysis' in serializable_results and serializable_results['comment_analysis']:
            if 'keywords' in serializable_results['comment_analysis']:
                serializable_results['comment_analysis']['keywords'] = serializable_results['comment_analysis']['keywords'][:30]
            if 'advanced_keywords' in serializable_results['comment_analysis']:
                serializable_results['comment_analysis']['advanced_keywords'] = serializable_results['comment_analysis']['advanced_keywords'][:30]
            if 'tfidf_keywords' in serializable_results['comment_analysis']:
                serializable_results['comment_analysis']['tfidf_keywords'] = serializable_results['comment_analysis']['tfidf_keywords'][:30]
            if 'textrank_keywords' in serializable_results['comment_analysis']:
                serializable_results['comment_analysis']['textrank_keywords'] = serializable_results['comment_analysis']['textrank_keywords'][:30]
        
        if 'content_analysis' in serializable_results and serializable_results['content_analysis']:
            if 'title_keywords' in serializable_results['content_analysis']:
                serializable_results['content_analysis']['title_keywords'] = serializable_results['content_analysis']['title_keywords'][:30]
            if 'desc_keywords' in serializable_results['content_analysis']:
                serializable_results['content_analysis']['desc_keywords'] = serializable_results['content_analysis']['desc_keywords'][:30]
        
        if 'creator_analysis' in serializable_results and serializable_results['creator_analysis']:
            if 'sign_keywords' in serializable_results['creator_analysis']:
                serializable_results['creator_analysis']['sign_keywords'] = serializable_results['creator_analysis']['sign_keywords'][:30]
        
        # 添加分析时间戳
        serializable_results['analysis_timestamp'] = datetime.now().isoformat()
        
        # 保存到文件
        os.makedirs('results', exist_ok=True)
        with open('results/analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        print("📁 分析结果已保存到 results/analysis_results.json")
        
        # 生成分析报告
        generate_analysis_report(serializable_results)
        
    except Exception as e:
        print(f"⚠️ 保存结果时出错: {e}")

def generate_analysis_report(results):
    """生成分析报告"""
    try:
        report_content = f"""# B站数据分析报告

## 分析时间
{results.get('analysis_timestamp', '未知')}

## 数据概览
"""
        
        # 评论分析部分
        if 'comment_analysis' in results and results['comment_analysis']:
            comment_stats = results['comment_analysis']['basic_stats']
            sentiment_dist = results['comment_analysis']['sentiment_distribution']
            
            report_content += f"""
### 评论数据分析
- **总评论数**: {comment_stats['total']:,} 条
- **有效评论数**: {comment_stats['valid']:,} 条
- **平均评论长度**: {comment_stats['avg_length']:.2f} 字符
- **平均点赞数**: {comment_stats['avg_likes']:.2f}

#### 情绪分布
- 积极评论: {sentiment_dist.get('积极', 0)} 条 ({sentiment_dist.get('积极', 0)/(sentiment_dist.get('积极', 0)+sentiment_dist.get('中性', 0)+sentiment_dist.get('消极', 0))*100:.1f}%)
- 中性评论: {sentiment_dist.get('中性', 0)} 条 ({sentiment_dist.get('中性', 0)/(sentiment_dist.get('积极', 0)+sentiment_dist.get('中性', 0)+sentiment_dist.get('消极', 0))*100:.1f}%)
- 消极评论: {sentiment_dist.get('消极', 0)} 条 ({sentiment_dist.get('消极', 0)/(sentiment_dist.get('积极', 0)+sentiment_dist.get('中性', 0)+sentiment_dist.get('消极', 0))*100:.1f}%)

#### 热门关键词 (高级组合算法)
"""
            if 'advanced_keywords' in results['comment_analysis']:
                keywords = results['comment_analysis']['advanced_keywords'][:20]
                for i, (word, weight) in enumerate(keywords, 1):
                    report_content += f"{i}. {word} (权重: {weight:.4f})\n"
            
            if 'tfidf_keywords' in results['comment_analysis']:
                report_content += "\n#### 热门关键词 (TF-IDF)\n"
                keywords = results['comment_analysis']['tfidf_keywords'][:15]
                for i, (word, weight) in enumerate(keywords, 1):
                    report_content += f"{i}. {word} (权重: {weight:.4f})\n"
            
            if 'textrank_keywords' in results['comment_analysis']:
                report_content += "\n#### 热门关键词 (TextRank)\n"
                keywords = results['comment_analysis']['textrank_keywords'][:15]
                for i, (word, weight) in enumerate(keywords, 1):
                    report_content += f"{i}. {word} (权重: {weight:.4f})\n"
        
        # 视频内容分析部分
        if 'content_analysis' in results and results['content_analysis']:
            video_stats = results['content_analysis']['video_stats']
            title_sentiment = results['content_analysis']['title_sentiment']
            
            report_content += f"""
### 视频内容分析
- **总视频数**: {video_stats['total_videos']} 个
- **平均播放量**: {video_stats['avg_play_count']:,.0f}
- **最高播放量**: {video_stats['max_play_count']:,}
- **播放量中位数**: {video_stats['median_play_count']:,.0f}

#### 标题情绪分布
- 积极标题: {title_sentiment.get('积极', 0)} 个
- 中性标题: {title_sentiment.get('中性', 0)} 个
- 消极标题: {title_sentiment.get('消极', 0)} 个

#### 视频标题热门关键词
"""
            if 'title_keywords' in results['content_analysis']:
                keywords = results['content_analysis']['title_keywords'][:15]
                for i, (word, weight) in enumerate(keywords, 1):
                    report_content += f"{i}. {word} (权重: {weight:.4f})\n"
        
        # 创作者分析部分  
        if 'creator_analysis' in results and results['creator_analysis']:
            gender_dist = results['creator_analysis']['gender_distribution']
            fan_stats = results['creator_analysis']['fan_stats']
            
            report_content += f"""
### 创作者分析
#### 性别分布
"""
            for gender, count in gender_dist.items():
                report_content += f"- {gender}: {count} 人\n"
            
            report_content += f"""
#### 粉丝数统计
- **平均粉丝数**: {fan_stats['avg_fans']:,.0f}
- **最高粉丝数**: {fan_stats['max_fans']:,}
- **粉丝数中位数**: {fan_stats['median_fans']:,.0f}

#### 个性签名热门关键词
"""
            if 'sign_keywords' in results['creator_analysis']:
                keywords = results['creator_analysis']['sign_keywords'][:10]
                for i, (word, weight) in enumerate(keywords, 1):
                    report_content += f"{i}. {word} (权重: {weight:.4f})\n"
        
        # 保存报告
        with open('results/analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        print("📊 分析报告已保存到 results/analysis_report.md")
        
    except Exception as e:
        print(f"⚠️ 生成报告时出错: {e}")

if __name__ == "__main__":
    main()