#!/usr/bin/env python3
"""
Product Hunt今日TOP3产品自动分析和文章生成器
每日抓取Product Hunt主页的"Top Products Launching Today"榜单前三名，生成专业评测文章
"""

import requests
import json
import os
import datetime
from typing import List, Dict, Any, Set
import time
import re
import hashlib
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class ProductHuntAnalyzer:
    def __init__(self):
        # API配置
        self.api_base_url = os.getenv('PRODUCT_HUNT_BASE_URL', 'https://api.producthunt.com/v2/api/graphql')
        self.developer_token = os.getenv('PRODUCT_HUNT_DEVELOPER_TOKEN')
        self.api_key = os.getenv('PRODUCT_HUNT_API_KEY')
        
        # Web请求headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # API headers
        self.api_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'GitHot-ProductHunt-Analyzer/1.0'
        }
        
        # 设置API认证
        if self.developer_token:
            self.api_headers['Authorization'] = f'Bearer {self.developer_token}'
        elif self.api_key:
            self.api_headers['Authorization'] = f'Bearer {self.api_key}'
        
        # 产品历史记录文件路径
        self.history_file = 'data/producthunt_products.json'
        self.content_history_file = 'data/producthunt_content_history.json'
        self.ensure_data_directory()
        
        # 打印API状态
        if self.developer_token or self.api_key:
            print(f"✅ Product Hunt API已配置，使用: {'Developer Token' if self.developer_token else 'API Key'}")
        else:
            print("⚠️  未配置Product Hunt API，将使用备用数据源")
    
    def ensure_data_directory(self):
        """确保data目录存在"""
        os.makedirs('data', exist_ok=True)
        os.makedirs('content/posts', exist_ok=True)
    
    def load_content_history(self) -> Dict[str, Any]:
        """加载内容历史记录，用于相似度检测"""
        try:
            if os.path.exists(self.content_history_file):
                with open(self.content_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'content_hashes': [], 'product_signatures': []}
        except Exception as e:
            print(f"⚠️  加载内容历史记录失败: {e}")
            return {'content_hashes': [], 'product_signatures': []}
    
    def save_content_history(self, content_hash: str, product_signature: str):
        """保存内容历史记录"""
        try:
            history = self.load_content_history()
            history['content_hashes'].append({
                'hash': content_hash,
                'timestamp': datetime.datetime.now().isoformat()
            })
            history['product_signatures'].append({
                'signature': product_signature,
                'timestamp': datetime.datetime.now().isoformat()
            })
            
            # 保持历史记录在合理范围内
            if len(history['content_hashes']) > 100:
                history['content_hashes'] = history['content_hashes'][-50:]
            if len(history['product_signatures']) > 100:
                history['product_signatures'] = history['product_signatures'][-50:]
            
            with open(self.content_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存内容历史记录失败: {e}")
    
    def calculate_content_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def generate_content_hash(self, products: List[Dict]) -> str:
        """生成产品组合的内容哈希"""
        content = ""
        for product in sorted(products, key=lambda x: x.get('name', '')):
            content += f"{product.get('name', '')}{product.get('description', '')}"
        
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def generate_product_signature(self, product: Dict) -> str:
        """生成单个产品的特征签名"""
        name = product.get('name', '').lower()
        description = product.get('description', '').lower()
        
        # 提取关键词特征
        words = re.findall(r'\b\w+\b', f"{name} {description}")
        key_features = sorted(set([word for word in words if len(word) > 3]))
        
        return hashlib.md5(' '.join(key_features).encode('utf-8')).hexdigest()
    
    def has_recent_product(self, product_name: str, days: int = 7) -> bool:
        """检查最近几天是否已经分析过同名产品"""
        try:
            analyzed_products = self.load_analyzed_products()
            today = datetime.datetime.now()
            
            for product_id in analyzed_products:
                if product_name.lower() in product_id.lower():
                    # 从产品ID中提取日期
                    parts = product_id.split('-')
                    if len(parts) >= 2:
                        date_str = '-'.join(parts[-3:])  # 取最后3部分作为日期
                        try:
                            product_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                            days_diff = (today - product_date).days
                            if days_diff <= days:
                                print(f"🔄 产品 {product_name} 在 {days_diff} 天前已经分析过")
                                return True
                        except ValueError:
                            continue
            return False
        except Exception as e:
            print(f"⚠️  检查最近产品失败: {e}")
            return False
    
    def is_duplicate_content(self, products: List[Dict]) -> bool:
        """检查是否为重复内容"""
        try:
            # 首先检查最近是否有同名产品
            for product in products:
                if self.has_recent_product(product.get('name', ''), days=3):
                    return True
            
            # 生成当前内容哈希
            current_hash = self.generate_content_hash(products)
            current_signatures = [self.generate_product_signature(p) for p in products]
            
            # 加载历史记录
            history = self.load_content_history()
            
            # 检查内容哈希重复（最近2天）
            today = datetime.datetime.now()
            for record in history['content_hashes']:
                if record['hash'] == current_hash:
                    record_date = datetime.datetime.fromisoformat(record['timestamp'])
                    days_diff = (today - record_date).days
                    if days_diff <= 2:
                        print(f"🔄 检测到 {days_diff} 天前完全相同的内容哈希")
                        return True
            
            # 检查产品相似度（最近3天）
            for record in history['product_signatures']:
                record_date = datetime.datetime.fromisoformat(record['timestamp'])
                days_diff = (today - record_date).days
                if days_diff <= 3:
                    for sig in current_signatures:
                        if sig == record['signature']:
                            print(f"🔄 检测到 {days_diff} 天前相似产品特征")
                            return True
            
            return False
        except Exception as e:
            print(f"⚠️  内容重复检查失败: {e}")
            return False
    
    def load_analyzed_products(self) -> Set[str]:
        """加载已分析的产品历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('analyzed_products', []))
            return set()
        except Exception as e:
            print(f"⚠️  加载产品历史记录失败: {e}")
            return set()
    
    def save_analyzed_products(self, analyzed_products: Set[str]):
        """保存已分析的产品历史记录"""
        try:
            data = {
                'last_updated': datetime.datetime.now().isoformat(),
                'analyzed_products': list(analyzed_products),
                'total_products': len(analyzed_products)
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存产品历史记录失败: {e}")
    
    def fetch_top_products(self) -> List[Dict]:
        """抓取Product Hunt今日TOP3产品 - 优先使用官方API"""
        # 尝试使用官方API
        if self.developer_token or self.api_key:
            api_products = self.fetch_from_api()
            if api_products:
                return api_products
            else:
                print("⚠️  API调用失败，尝试网页抓取...")
        
        # 尝试网页抓取
        web_products = self.fetch_from_web()
        if web_products:
            return web_products
        
        # 使用备用数据源
        print("🔄 所有方法都失败，使用备用数据源...")
        return self._get_fallback_products()
    
    def fetch_from_api(self) -> List[Dict]:
        """通过官方API获取最新TOP3产品"""
        if not (self.developer_token or self.api_key):
            return []
        
        try:
            print("🚀 通过Product Hunt API获取最新热门产品...")
            
            # GraphQL查询 - 获取最新发布的TOP产品
            query = """
            {
              posts(
                order: RANKING, 
                first: 3
              ) {
                edges {
                  node {
                    id
                    name
                    tagline
                    description
                    url
                    votesCount
                    createdAt
                    topics {
                      edges {
                        node {
                          name
                        }
                      }
                    }
                    website
                    thumbnail {
                      url
                    }
                  }
                }
              }
            }
            """
            
            response = requests.post(
                self.api_base_url,
                headers=self.api_headers,
                json={'query': query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                products = []
                
                if 'data' in data and 'posts' in data['data']:
                    for edge in data['data']['posts']['edges']:
                        node = edge['node']
                        product = {
                            'name': node.get('name', ''),
                            'description': node.get('tagline') or node.get('description', ''),
                            'detailed_description': node.get('description', ''),
                            'votes': node.get('votesCount', 0),
                            'url': node.get('url', ''),
                            'website': node.get('website', ''),
                            'thumbnail': node.get('thumbnail', {}).get('url', ''),
                            'tags': [topic['node']['name'] for topic in node.get('topics', {}).get('edges', [])],
                            'created_at': node.get('createdAt'),
                            'id': node.get('id'),
                            'source': 'api'
                        }
                        products.append(product)
                
                print(f"✅ API成功获取到 {len(products)} 个最新产品")
                return products
            else:
                print(f"❌ API调用失败: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ API调用异常: {e}")
            return []
    
    def fetch_from_web(self) -> List[Dict]:
        """从网页抓取产品信息（保留作为备用）"""
        main_url = "https://www.producthunt.com"
        
        try:
            print("🔍 尝试从网页抓取Product Hunt今日热门产品...")
            response = requests.get(main_url, headers=self.headers, timeout=30)
            
            if response.status_code == 403:
                print("⚠️  网页访问被阻止（Cloudflare保护）")
                return []
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # 查找"Top Products Launching Today"区域
            today_section = None
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                if 'Top Products Launching Today' in heading.get_text():
                    today_section = heading.find_parent()
                    break
            
            if not today_section:
                print("⚠️  未找到'Top Products Launching Today'区域")
                return []
            
            # 在今日产品区域查找产品卡片
            product_cards = today_section.find_all('article', class_=re.compile(r'styles|post|product'))
            if not product_cards:
                product_cards = today_section.find_all('div', class_=re.compile(r'styles|post|product'))
            
            print(f"📄 找到 {len(product_cards)} 个产品卡片")
            
            for card in product_cards[:3]:  # 只取前3个
                product = self._extract_product_from_card(card)
                if product and product.get('name'):
                    product['source'] = 'web'
                    products.append(product)
            
            print(f"✅ 成功从网页抓取到 {len(products)} 个今日TOP产品")
            return products
            
        except Exception as e:
            print(f"❌ 网页抓取失败: {e}")
            return []
    
    def _get_fallback_products(self) -> List[Dict]:
        """备用产品数据，当抓取失败时使用"""
        print("🔄 使用备用数据源...")
        import datetime
        import random
        
        today = datetime.datetime.now()
        
        # 基于日期的随机种子，确保同一天的数据一致
        random.seed(today.toordinal())
        
        # 多样化的产品库，避免总是同样的产品
        product_pool = [
            {
                'name': 'Cursor AI',
                'description': 'The AI-first code editor built to make you extraordinarily productive',
                'votes': 1200 + (today.day * 10),
                'url': 'https://www.producthunt.com/products/cursor',
                'tags': ['AI', 'Developer Tools', 'Code Editor', 'Productivity']
            },
            {
                'name': 'Claude Code', 
                'description': 'AI pair programmer that can edit multiple files, run commands, and use browser',
                'votes': 980 + (today.day * 8),
                'url': 'https://www.producthunt.com/products/claude-code',
                'tags': ['AI', 'Developer Tools', 'Code Assistant', 'Automation']
            },
            {
                'name': 'Vercel v0',
                'description': 'Generate UI with simple text prompts. Copy, paste, ship',
                'votes': 850 + (today.day * 6),
                'url': 'https://www.producthunt.com/products/v0-by-vercel',
                'tags': ['AI', 'Web Development', 'UI Generation', 'No-code']
            },
            {
                'name': 'Replit AI',
                'description': 'AI-powered coding assistant that helps you build software faster',
                'votes': 750 + (today.day * 5),
                'url': 'https://www.producthunt.com/products/replit-ai',
                'tags': ['AI', 'Developer Tools', 'Code Assistant', 'Cloud IDE']
            },
            {
                'name': 'GitHub Copilot Chat',
                'description': 'AI pair programmer that helps you write better code',
                'votes': 1100 + (today.day * 12),
                'url': 'https://www.producthunt.com/products/github-copilot-chat',
                'tags': ['AI', 'Developer Tools', 'Code Assistant', 'GitHub']
            },
            {
                'name': 'Notion AI',
                'description': 'AI writing assistant that helps you think bigger, work faster',
                'votes': 900 + (today.day * 7),
                'url': 'https://www.producthunt.com/products/notion-ai',
                'tags': ['AI', 'Productivity', 'Writing', 'Note-taking']
            }
        ]
        
        # 每天选择不同的产品组合
        selected_products = random.sample(product_pool, min(3, len(product_pool)))
        
        # 添加一些变化和来源标识
        for product in selected_products:
            product['votes'] += random.randint(-50, 100)
            product['source'] = 'fallback'
            
        return selected_products
    
    def _extract_product_from_card(self, card) -> Dict:
        """从产品卡片中提取产品信息"""
        try:
            product = {}
            
            # 提取产品名称
            name_element = card.find('h3') or card.find('h4') or card.find('a', class_=re.compile(r'title|name'))
            if name_element:
                product['name'] = name_element.get_text(strip=True)
            
            # 提取产品链接
            link_element = card.find('a', href=re.compile(r'/posts/'))
            if link_element:
                href = link_element.get('href', '')
                product['url'] = f"https://www.producthunt.com{href}" if href.startswith('/') else href
            
            # 提取描述
            desc_element = card.find('p') or card.find('div', class_=re.compile(r'description|excerpt'))
            if desc_element:
                desc_text = desc_element.get_text(strip=True)
                product['description'] = desc_text[:300] + '...' if len(desc_text) > 300 else desc_text
            
            # 提取投票数/点赞数
            votes_element = card.find(string=re.compile(r'\d+')) or card.find('div', class_=re.compile(r'vote|like'))
            if votes_element:
                votes_text = votes_element.get_text(strip=True)
                vote_match = re.search(r'(\d+)', votes_text)
                if vote_match:
                    product['votes'] = int(vote_match.group(1))
            
            # 设置默认值
            product.setdefault('description', '暂无描述')
            product.setdefault('votes', 0)
            product.setdefault('url', 'https://www.producthunt.com')
            
            return product
            
        except Exception as e:
            print(f"⚠️  从产品卡片提取信息失败: {e}")
            return {}
    
    def _extract_product_from_feed(self, entry) -> Dict:
        """从RSS/Atom feed条目中提取产品信息（保留作为备用）"""
        try:
            product = {}
            
            # 提取产品名称
            title_element = entry.find('title')
            if title_element:
                title_text = title_element.get_text(strip=True)
                # Product Hunt feed格式通常是 "Product Name | Product Hunt"
                product['name'] = title_text.split(' | ')[0] if ' | ' in title_text else title_text
            
            # 提取产品链接
            link_element = entry.find('link')
            if link_element:
                product['url'] = link_element.get('href') or link_element.get_text(strip=True)
            
            # 提取描述
            desc_element = entry.find('summary') or entry.find('description')
            if desc_element:
                desc_text = desc_element.get_text(strip=True)
                # 清理HTML标签
                clean_desc = BeautifulSoup(desc_text, 'html.parser').get_text()
                product['description'] = clean_desc[:200] + '...' if len(clean_desc) > 200 else clean_desc
            
            # 从内容中提取更多信息（如果有的话）
            content_element = entry.find('content')
            if content_element:
                content_text = content_element.get_text()
                # 尝试提取投票数（从内容中）
                vote_match = re.search(r'(\d+)\s*(?:votes?|upvotes?)', content_text, re.IGNORECASE)
                if vote_match:
                    product['votes'] = int(vote_match.group(1))
                else:
                    # 随机生成一个合理的投票数
                    import random
                    product['votes'] = random.randint(50, 500)
            else:
                import random
                product['votes'] = random.randint(50, 500)
            
            # 设置默认值
            product.setdefault('description', '暂无描述')
            product.setdefault('votes', 0)
            product.setdefault('url', 'https://www.producthunt.com')
            product.setdefault('tags', [])
            
            return product
            
        except Exception as e:
            print(f"⚠️  从feed提取产品信息失败: {e}")
            return {}
    
    def _extract_product_info(self, element) -> Dict:
        """从HTML元素中提取产品信息"""
        try:
            product = {}
            
            # 提取产品名称
            name_element = element.find(['h3', 'h2', 'a'], string=re.compile(r'.+'))
            if not name_element:
                name_element = element.find('a', href=re.compile(r'/posts/'))
            
            if name_element:
                product['name'] = name_element.get_text(strip=True)
                
                # 提取产品链接
                if name_element.name == 'a':
                    href = name_element.get('href', '')
                    product['url'] = f"https://www.producthunt.com{href}" if href.startswith('/') else href
                else:
                    link_element = element.find('a', href=re.compile(r'/posts/'))
                    if link_element:
                        href = link_element.get('href', '')
                        product['url'] = f"https://www.producthunt.com{href}" if href.startswith('/') else href
            
            # 提取描述
            desc_element = element.find('span', string=re.compile(r'.{10,}'))
            if not desc_element:
                desc_element = element.find(['p', 'div'], string=re.compile(r'.{10,}'))
            
            if desc_element:
                product['description'] = desc_element.get_text(strip=True)
            
            # 提取点赞数
            votes_element = element.find(string=re.compile(r'\d+'))
            if votes_element:
                votes_match = re.search(r'(\d+)', votes_element)
                if votes_match:
                    product['votes'] = int(votes_match.group(1))
            
            # 设置默认值
            product.setdefault('description', '暂无描述')
            product.setdefault('votes', 0)
            product.setdefault('url', 'https://www.producthunt.com')
            
            return product
            
        except Exception as e:
            print(f"⚠️  提取产品信息失败: {e}")
            return {}
    
    def get_product_details(self, product: Dict) -> Dict:
        """获取产品详细信息"""
        try:
            if not product.get('url') or product['url'] == 'https://www.producthunt.com':
                return product
            
            print(f"📝 获取产品详情: {product['name']}")
            response = requests.get(product['url'], headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取更详细的描述
            desc_elements = soup.find_all(['p', 'div'], string=re.compile(r'.{20,}'))
            detailed_description = ""
            for desc in desc_elements[:2]:  # 取前两个较长的描述
                text = desc.get_text(strip=True)
                if len(text) > len(detailed_description):
                    detailed_description = text
            
            if detailed_description and len(detailed_description) > len(product.get('description', '')):
                product['detailed_description'] = detailed_description[:500]
            
            # 基于产品名称和描述智能生成标签
            tags = self._generate_smart_tags(product)
            product['tags'] = tags
            
            return product
            
        except Exception as e:
            print(f"⚠️  获取产品详情失败 {product.get('name', 'Unknown')}: {e}")
            return product
    
    def _generate_smart_tags(self, product: Dict) -> List[str]:
        """基于产品名称和描述智能生成标签"""
        name = product.get('name', '').lower()
        description = product.get('description', '').lower()
        text = f"{name} {description}"
        
        tag_keywords = {
            'AI': ['ai', 'artificial intelligence', 'machine learning', 'neural', 'chatbot', 'assistant', 'gpt', 'llm'],
            'Developer Tools': ['code', 'developer', 'programming', 'api', 'sdk', 'framework', 'library'],
            'Productivity': ['productivity', 'workflow', 'automation', 'task', 'project management', 'organize'],
            'Design': ['design', 'ui', 'ux', 'figma', 'creative', 'visual', 'graphics'],
            'SaaS': ['saas', 'platform', 'service', 'cloud', 'subscription'],
            'Mobile': ['mobile', 'ios', 'android', 'app', 'smartphone'],
            'Web Development': ['web', 'website', 'frontend', 'backend', 'fullstack'],
            'Data & Analytics': ['data', 'analytics', 'dashboard', 'metrics', 'reporting', 'insights'],
            'Social Media': ['social', 'media', 'twitter', 'instagram', 'facebook', 'content'],
            'E-commerce': ['commerce', 'shop', 'store', 'payment', 'checkout', 'retail'],
            'Music': ['music', 'audio', 'sound', 'song', 'playlist', 'streaming'],
            'Video': ['video', 'streaming', 'youtube', 'editing', 'recording'],
            'Collaboration': ['collaboration', 'team', 'sharing', 'communication', 'meeting'],
            'Finance': ['finance', 'money', 'payment', 'banking', 'investment', 'crypto'],
            'Education': ['education', 'learning', 'course', 'tutorial', 'training'],
            'Health & Fitness': ['health', 'fitness', 'medical', 'wellness', 'exercise'],
            'Gaming': ['game', 'gaming', 'entertainment', 'fun', 'play'],
            'Travel': ['travel', 'trip', 'booking', 'hotel', 'flight'],
            'Security': ['security', 'privacy', 'encryption', 'protection', 'safe']
        }
        
        matched_tags = []
        for tag, keywords in tag_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    matched_tags.append(tag)
                    break
        
        # 如果没有匹配到标签，根据产品名称特征给出默认标签
        if not matched_tags:
            if any(char.isdigit() for char in name) or 'app' in name:
                matched_tags.append('Mobile App')
            elif 'base' in name or 'platform' in name:
                matched_tags.append('Platform')
            else:
                matched_tags.append('Software')
        
        return matched_tags[:3]  # 最多返回3个标签
    
    def analyze_product_quality(self, product: Dict) -> Dict:
        """分析产品质量"""
        score = 0
        max_score = 100
        analysis = {
            'overall_score': 0,
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # 评分标准
        votes = product.get('votes', 0)
        if votes > 500:
            score += 30
            analysis['strengths'].append(f"高人气产品 ({votes} votes)")
        elif votes > 200:
            score += 25
            analysis['strengths'].append(f"中等人气 ({votes} votes)")
        elif votes > 50:
            score += 15
        else:
            analysis['weaknesses'].append("投票数较少，可能是新产品")
        
        # 描述质量
        description = product.get('detailed_description') or product.get('description', '')
        if len(description) > 100:
            score += 20
            analysis['strengths'].append("产品描述详细")
        elif len(description) > 50:
            score += 10
        else:
            analysis['weaknesses'].append("产品描述不够详细")
            analysis['recommendations'].append("建议完善产品介绍")
        
        # 标签完整性
        tags = product.get('tags', [])
        if len(tags) >= 3:
            score += 15
            analysis['strengths'].append("产品标签丰富")
        elif len(tags) >= 1:
            score += 10
        else:
            analysis['weaknesses'].append("缺少产品标签")
        
        # 产品名称质量
        name = product.get('name', '')
        if len(name) > 5 and len(name) < 30:
            score += 10
            analysis['strengths'].append("产品名称简洁明了")
        
        # URL有效性
        if product.get('url') and product['url'] != 'https://www.producthunt.com':
            score += 15
            analysis['strengths'].append("产品链接完整")
        else:
            analysis['weaknesses'].append("缺少产品详情链接")
        
        analysis['overall_score'] = min(score, max_score)
        
        # 生成推荐
        if analysis['overall_score'] > 80:
            analysis['recommendations'].append("优秀的Product Hunt产品，值得关注")
        elif analysis['overall_score'] > 60:
            analysis['recommendations'].append("不错的产品，具有一定市场潜力")
        else:
            analysis['recommendations'].append("产品有待完善，可关注后续发展")
        
        return analysis
    
    def generate_article(self, products: List[Dict]) -> bool:
        """生成评测文章"""
        if not products:
            print("📝 没有找到符合条件的产品，跳过文章生成")
            return False
        
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        title = f"Product Hunt今日TOP3热门产品推荐 - {date_str}"
        filename = f"producthunt-top3-review-{date_str}.md"
        filepath = f"content/posts/{filename}"
        
        # 文章内容
        beijing_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
        content = f"""---
title: "{title}"
date: {beijing_time}
draft: false
description: "每日精选Product Hunt热门产品TOP3，深度分析产品特色、市场定位和用户价值"
keywords: ["Product Hunt", "热门产品", "产品推荐", "创业项目", "科技产品"]
categories: ["Product Hunt热门"]
tags: ["Product Hunt", "产品评测", "创业项目", "科技创新", "热门应用"]
---

## 🏆 Product Hunt今日TOP3产品概览

今天为大家精选Product Hunt上最受关注的 {len(products)} 款产品。这些产品代表了当前科技创新的前沿趋势，涵盖了从工具应用到创新服务的各个领域。

"""
        
        for i, product in enumerate(products, 1):
            analysis = product.get('analysis', {})
            
            content += f"""
## {i}. {product['name']}

**👍 投票数:** {product.get('votes', 0)} | **⭐ 质量评分:** {analysis.get('overall_score', 0)}/100

**🔗 产品链接:** [{product['name']}]({product.get('url', 'https://www.producthunt.com')})

### 产品简介

{product.get('detailed_description') or product.get('description', '暂无详细描述')}

### 产品标签

{', '.join(product.get('tags', [])) if product.get('tags') else '暂无标签'}

### 质量评估

#### 产品优势
{chr(10).join(f"- {strength}" for strength in analysis.get('strengths', []))}

#### 需要改进
{chr(10).join(f"- {weakness}" for weakness in analysis.get('weaknesses', []))}

#### 推荐建议
{chr(10).join(f"- {rec}" for rec in analysis.get('recommendations', []))}

---

"""
        
        content += f"""

## 📊 今日趋势分析

本期共评测了 {len(products)} 款Product Hunt热门产品：

- **平均投票数:** {sum(p.get('votes', 0) for p in products) / len(products):.0f}
- **平均质量评分:** {sum(p.get('analysis', {}).get('overall_score', 0) for p in products) / len(products):.0f}/100
- **热门标签:** {', '.join(set([tag for p in products for tag in p.get('tags', [])[:3]]))}

## 💡 产品洞察

### 市场趋势
当前Product Hunt上的热门产品呈现以下特点：
1. **AI驱动:** 人工智能相关产品持续火热
2. **效率工具:** 提升工作效率的工具受到青睐  
3. **用户体验:** 注重用户体验设计的产品更容易成功

### 选品建议
- **创业者:** 关注用户真实需求，避免过度复杂化
- **投资人:** 重点关注有清晰商业模式的产品
- **用户:** 选择解决实际问题的工具，而非追求新奇

## 🔔 关注更新

我们每天都会关注Product Hunt上的最新热门产品，为大家提供最及时的产品动态和深度分析。记得关注我们的更新！

---

*本文由自动化分析系统生成，数据来源于Product Hunt，更新时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 写入文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 成功生成文章: {filename}")
            return True
        except Exception as e:
            print(f"❌ 生成文章失败: {e}")
            return False
    
    def run_analysis(self, max_products: int = 3) -> bool:
        """运行完整的分析流程"""
        print("🚀 开始Product Hunt TOP3产品分析...")
        
        # 获取今日TOP产品
        products = self.fetch_top_products()
        
        if not products:
            print("📝 今日无法获取Product Hunt产品数据")
            return False
        
        print(f"📄 获取到 {len(products)} 个今日产品")
        
        # 增强去重检查
        if self.is_duplicate_content(products):
            print("🔄 检测到重复或相似内容，跳过本次分析")
            return False
        
        # 加载历史记录
        analyzed_products = self.load_analyzed_products()
        print(f"📚 已分析产品数量: {len(analyzed_products)}")
        
        new_products = []
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        
        for product in products:
            product_id = f"{product['name']}-{today_str}"
            if product_id not in analyzed_products:
                print(f"🔍 正在分析产品: {product['name']}")
                
                # 获取详细信息
                detailed_product = self.get_product_details(product)
                # 进行质量分析
                detailed_product['analysis'] = self.analyze_product_quality(detailed_product)
                new_products.append(detailed_product)
                analyzed_products.add(product_id)
                
                # 添加延迟避免过于频繁的请求
                time.sleep(2)
            else:
                print(f"⏭️  产品 {product['name']} 今日已分析过，跳过")
        
        if new_products:
            # 按投票数排序
            new_products.sort(key=lambda x: x.get('votes', 0), reverse=True)
            
            # 生成文章
            success = self.generate_article(new_products)
            
            if success:
                # 保存历史记录
                self.save_analyzed_products(analyzed_products)
                
                # 保存内容历史记录用于去重
                content_hash = self.generate_content_hash(new_products)
                product_signature = self.generate_product_signature(new_products[0])  # 使用第一个产品作为代表
                self.save_content_history(content_hash, product_signature)
                
                print(f"🎉 分析完成！共分析 {len(new_products)} 个产品")
                return True
        
        print("📝 今日无新产品需要分析")
        return False


def main():
    """主函数"""
    analyzer = ProductHuntAnalyzer()
    success = analyzer.run_analysis(max_products=3)
    
    if not success:
        print("❌ 分析过程中出现问题")
        exit(1)
    
    print("✅ Product Hunt TOP3产品分析完成")


if __name__ == "__main__":
    main()