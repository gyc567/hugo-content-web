#!/usr/bin/env python3
"""
Product Hunt今日TOP3产品自动分析和文章生成器
每日抓取Product Hunt的Top Products Launching Today榜单前三名，生成专业评测文章
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


class ProductHuntAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        # 产品历史记录文件路径
        self.history_file = 'data/producthunt_products.json'
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """确保data目录存在"""
        os.makedirs('data', exist_ok=True)
        os.makedirs('content/posts', exist_ok=True)
    
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
        """抓取Product Hunt今日TOP3产品"""
        url = "https://www.producthunt.com"
        
        try:
            print("🔍 正在抓取Product Hunt今日热门产品...")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # 查找产品列表元素
            product_elements = soup.find_all('div', class_=re.compile(r'styles_item__.*'))
            
            if not product_elements:
                # 备用选择器
                product_elements = soup.find_all(['div', 'article'], attrs={'data-test': re.compile(r'post.*')})
            
            count = 0
            for element in product_elements:
                if count >= 3:  # 只取前3个
                    break
                
                product = self._extract_product_info(element)
                if product and product.get('name'):
                    products.append(product)
                    count += 1
            
            print(f"✅ 成功抓取到 {len(products)} 个产品")
            return products
            
        except Exception as e:
            print(f"❌ 抓取Product Hunt失败: {e}")
            return []
    
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
            
            # 提取标签
            tag_elements = soup.find_all('span', class_=re.compile(r'tag'))
            if not tag_elements:
                tag_elements = soup.find_all('a', href=re.compile(r'/topics/'))
            
            tags = []
            for tag in tag_elements[:5]:  # 最多5个标签
                tag_text = tag.get_text(strip=True)
                if tag_text and len(tag_text) < 20:
                    tags.append(tag_text)
            
            product['tags'] = tags
            
            return product
            
        except Exception as e:
            print(f"⚠️  获取产品详情失败 {product.get('name', 'Unknown')}: {e}")
            return product
    
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
        content = f"""---
title: "{title}"
date: {datetime.datetime.now().isoformat()}
draft: false
description: "每日精选Product Hunt热门产品TOP3，深度分析产品特色、市场定位和用户价值"
keywords: ["Product Hunt", "热门产品", "产品推荐", "创业项目", "科技产品"]
categories: ["Product Hunt热门"]
tags: ["Product Hunt", "产品评测", "创业项目", "科技创新", "热门应用"]
image: "/images/producthunt-top3.jpg"
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
        
        # 加载历史记录
        analyzed_products = self.load_analyzed_products()
        print(f"📚 已分析产品数量: {len(analyzed_products)}")
        
        # 获取今日TOP产品
        products = self.fetch_top_products()
        
        if not products:
            print("📝 今日无法获取Product Hunt产品数据")
            return False
        
        new_products = []
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        
        for product in products:
            product_id = f"{product['name']}-{today_str}"
            if product_id not in analyzed_products:
                # 获取详细信息
                detailed_product = self.get_product_details(product)
                # 进行质量分析
                detailed_product['analysis'] = self.analyze_product_quality(detailed_product)
                new_products.append(detailed_product)
                analyzed_products.add(product_id)
                
                # 添加延迟避免过于频繁的请求
                time.sleep(1)
        
        if new_products:
            # 按投票数排序
            new_products.sort(key=lambda x: x.get('votes', 0), reverse=True)
            
            # 生成文章
            success = self.generate_article(new_products)
            
            if success:
                # 保存历史记录
                self.save_analyzed_products(analyzed_products)
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