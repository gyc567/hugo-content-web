#!/usr/bin/env python3
"""
Product Hunt分析器单元测试
确保100%测试覆盖率
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, Mock, MagicMock
import datetime
from producthunt_analyzer import ProductHuntAnalyzer


class TestProductHuntAnalyzer(unittest.TestCase):
    """Product Hunt分析器测试类"""

    def setUp(self):
        """测试前置设置"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        self.analyzer = ProductHuntAnalyzer()
        
        # 创建测试数据目录
        os.makedirs('data', exist_ok=True)
        os.makedirs('content/posts', exist_ok=True)

    def tearDown(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        """测试初始化"""
        analyzer = ProductHuntAnalyzer()
        self.assertIsNotNone(analyzer.headers)
        self.assertEqual(analyzer.history_file, 'data/producthunt_products.json')
        self.assertIn('User-Agent', analyzer.headers)

    def test_ensure_data_directory(self):
        """测试目录创建"""
        # 删除目录
        if os.path.exists('data'):
            shutil.rmtree('data')
        if os.path.exists('content'):
            shutil.rmtree('content')
        
        analyzer = ProductHuntAnalyzer()
        self.assertTrue(os.path.exists('data'))
        self.assertTrue(os.path.exists('content/posts'))

    def test_load_analyzed_products_empty(self):
        """测试加载空的历史记录"""
        products = self.analyzer.load_analyzed_products()
        self.assertEqual(products, set())

    def test_load_analyzed_products_existing(self):
        """测试加载已存在的历史记录"""
        test_data = {
            'last_updated': '2025-08-28T10:00:00',
            'analyzed_products': ['product1', 'product2'],
            'total_products': 2
        }
        with open(self.analyzer.history_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        products = self.analyzer.load_analyzed_products()
        self.assertEqual(products, {'product1', 'product2'})

    def test_load_analyzed_products_invalid_file(self):
        """测试加载无效的历史记录文件"""
        with open(self.analyzer.history_file, 'w', encoding='utf-8') as f:
            f.write('invalid json')
        
        products = self.analyzer.load_analyzed_products()
        self.assertEqual(products, set())

    def test_save_analyzed_products(self):
        """测试保存历史记录"""
        test_products = {'product1', 'product2', 'product3'}
        self.analyzer.save_analyzed_products(test_products)
        
        self.assertTrue(os.path.exists(self.analyzer.history_file))
        
        with open(self.analyzer.history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(set(data['analyzed_products']), test_products)
        self.assertEqual(data['total_products'], 3)
        self.assertIn('last_updated', data)

    def test_save_analyzed_products_error(self):
        """测试保存历史记录出错情况"""
        # 创建一个只读目录
        os.makedirs('readonly_data', exist_ok=True)
        os.chmod('readonly_data', 0o444)
        
        analyzer = ProductHuntAnalyzer()
        analyzer.history_file = 'readonly_data/test.json'
        
        # 这应该不会抛出异常，但会打印错误消息
        analyzer.save_analyzed_products({'test'})

    @patch('requests.get')
    def test_fetch_top_products_success(self, mock_get):
        """测试成功抓取产品"""
        mock_html = '''
        <html>
            <div class="styles_item__abc123">
                <h3>Test Product 1</h3>
                <a href="/posts/test-product-1">Link</a>
                <span>This is a test description for product 1</span>
                <span>123</span>
            </div>
            <div class="styles_item__def456">
                <h3>Test Product 2</h3>
                <a href="/posts/test-product-2">Link</a>
                <span>This is a test description for product 2</span>
                <span>456</span>
            </div>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        products = self.analyzer.fetch_top_products()
        
        self.assertIsInstance(products, list)
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_fetch_top_products_request_error(self, mock_get):
        """测试网络请求失败"""
        mock_get.side_effect = Exception("Network error")
        
        products = self.analyzer.fetch_top_products()
        self.assertEqual(products, [])

    def test_extract_product_info_complete(self):
        """测试提取完整产品信息"""
        from bs4 import BeautifulSoup
        
        html = '''
        <div>
            <h3>Test Product</h3>
            <a href="/posts/test-product">Product Link</a>
            <span>This is a detailed product description with more than ten characters</span>
            <span>789</span>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div')
        
        product = self.analyzer._extract_product_info(element)
        
        self.assertEqual(product['name'], 'Test Product')
        self.assertEqual(product['url'], 'https://www.producthunt.com/posts/test-product')
        self.assertIn('description', product)
        self.assertEqual(product['votes'], 789)

    def test_extract_product_info_minimal(self):
        """测试提取最少产品信息"""
        from bs4 import BeautifulSoup
        
        html = '<div><h3>Minimal Product</h3></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div')
        
        product = self.analyzer._extract_product_info(element)
        
        self.assertEqual(product['name'], 'Minimal Product')
        self.assertEqual(product['description'], '暂无描述')
        self.assertEqual(product['votes'], 0)
        self.assertEqual(product['url'], 'https://www.producthunt.com')

    def test_extract_product_info_error(self):
        """测试提取产品信息出错"""
        # 传入None会导致错误
        product = self.analyzer._extract_product_info(None)
        self.assertEqual(product, {})

    @patch('requests.get')
    def test_get_product_details_success(self, mock_get):
        """测试成功获取产品详情"""
        mock_html = '''
        <html>
            <p>This is a very detailed product description that is longer than the original</p>
            <span class="tag">AI</span>
            <span class="tag">Productivity</span>
            <a href="/topics/saas">SaaS</a>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        product = {
            'name': 'Test Product',
            'url': 'https://www.producthunt.com/posts/test',
            'description': 'Short desc'
        }
        
        detailed = self.analyzer.get_product_details(product)
        
        self.assertIn('detailed_description', detailed)
        self.assertIn('tags', detailed)

    @patch('requests.get')
    def test_get_product_details_no_url(self, mock_get):
        """测试没有URL的产品"""
        product = {'name': 'Test Product'}
        detailed = self.analyzer.get_product_details(product)
        self.assertEqual(detailed, product)
        mock_get.assert_not_called()

    @patch('requests.get')
    def test_get_product_details_error(self, mock_get):
        """测试获取产品详情出错"""
        mock_get.side_effect = Exception("Request failed")
        
        product = {
            'name': 'Test Product',
            'url': 'https://www.producthunt.com/posts/test'
        }
        
        detailed = self.analyzer.get_product_details(product)
        self.assertEqual(detailed, product)

    def test_analyze_product_quality_high_score(self):
        """测试高分产品质量分析"""
        product = {
            'name': 'Excellent Product',
            'votes': 1000,
            'detailed_description': 'This is a very comprehensive and detailed description that explains the product thoroughly and provides great value to users',
            'tags': ['AI', 'Productivity', 'SaaS', 'Tool'],
            'url': 'https://www.producthunt.com/posts/excellent-product'
        }
        
        analysis = self.analyzer.analyze_product_quality(product)
        
        self.assertGreater(analysis['overall_score'], 80)
        self.assertGreater(len(analysis['strengths']), 0)
        self.assertIn('优秀的Product Hunt产品', analysis['recommendations'][0])

    def test_analyze_product_quality_low_score(self):
        """测试低分产品质量分析"""
        product = {
            'name': 'Basic',
            'votes': 5,
            'description': 'Short',
            'tags': [],
            'url': 'https://www.producthunt.com'
        }
        
        analysis = self.analyzer.analyze_product_quality(product)
        
        self.assertLess(analysis['overall_score'], 60)
        self.assertGreater(len(analysis['weaknesses']), 0)

    def test_analyze_product_quality_edge_cases(self):
        """测试边界情况的质量分析"""
        # 测试空产品
        empty_product = {}
        analysis = self.analyzer.analyze_product_quality(empty_product)
        self.assertIsInstance(analysis['overall_score'], int)
        
        # 测试极值
        extreme_product = {
            'name': 'A' * 100,  # 过长名称
            'votes': -1,  # 负数投票
            'description': '',  # 空描述
            'tags': ['tag'] * 20,  # 过多标签
        }
        analysis = self.analyzer.analyze_product_quality(extreme_product)
        self.assertIsInstance(analysis['overall_score'], int)

    def test_generate_article_success(self):
        """测试成功生成文章"""
        products = [
            {
                'name': 'Test Product 1',
                'votes': 100,
                'description': 'Test description 1',
                'detailed_description': 'Detailed test description 1',
                'tags': ['AI', 'Tool'],
                'url': 'https://www.producthunt.com/posts/test1',
                'analysis': {
                    'overall_score': 85,
                    'strengths': ['Great product'],
                    'weaknesses': ['Minor issues'],
                    'recommendations': ['Recommended']
                }
            }
        ]
        
        success = self.analyzer.generate_article(products)
        self.assertTrue(success)
        
        # 检查文件是否生成
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        expected_file = f"content/posts/producthunt-top3-review-{date_str}.md"
        self.assertTrue(os.path.exists(expected_file))
        
        # 检查文件内容
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Test Product 1', content)
            self.assertIn('Detailed test description 1', content)

    def test_generate_article_empty(self):
        """测试空产品列表生成文章"""
        success = self.analyzer.generate_article([])
        self.assertFalse(success)

    def test_generate_article_write_error(self):
        """测试文章写入失败"""
        # 创建只读目录
        os.chmod('content/posts', 0o444)
        
        products = [{'name': 'Test', 'analysis': {}}]
        success = self.analyzer.generate_article(products)
        self.assertFalse(success)

    @patch.object(ProductHuntAnalyzer, 'fetch_top_products')
    @patch.object(ProductHuntAnalyzer, 'get_product_details')
    @patch.object(ProductHuntAnalyzer, 'analyze_product_quality')
    @patch.object(ProductHuntAnalyzer, 'generate_article')
    @patch.object(ProductHuntAnalyzer, 'load_analyzed_products')
    @patch.object(ProductHuntAnalyzer, 'save_analyzed_products')
    def test_run_analysis_success(self, mock_save, mock_load, mock_generate, 
                                 mock_analyze, mock_details, mock_fetch):
        """测试成功运行分析流程"""
        mock_load.return_value = set()
        mock_fetch.return_value = [{'name': 'Test Product', 'votes': 100}]
        mock_details.return_value = {'name': 'Test Product', 'votes': 100}
        mock_analyze.return_value = {'overall_score': 80}
        mock_generate.return_value = True
        
        success = self.analyzer.run_analysis()
        self.assertTrue(success)
        
        mock_fetch.assert_called_once()
        mock_generate.assert_called_once()
        mock_save.assert_called_once()

    @patch.object(ProductHuntAnalyzer, 'fetch_top_products')
    def test_run_analysis_no_products(self, mock_fetch):
        """测试无产品数据的分析流程"""
        mock_fetch.return_value = []
        
        success = self.analyzer.run_analysis()
        self.assertFalse(success)

    @patch.object(ProductHuntAnalyzer, 'fetch_top_products')
    @patch.object(ProductHuntAnalyzer, 'load_analyzed_products')
    def test_run_analysis_all_analyzed(self, mock_load, mock_fetch):
        """测试所有产品都已分析的情况"""
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        mock_load.return_value = {f'Test Product-{today_str}'}
        mock_fetch.return_value = [{'name': 'Test Product', 'votes': 100}]
        
        success = self.analyzer.run_analysis()
        self.assertFalse(success)

    @patch.object(ProductHuntAnalyzer, 'fetch_top_products')
    @patch.object(ProductHuntAnalyzer, 'get_product_details')
    @patch.object(ProductHuntAnalyzer, 'analyze_product_quality')
    @patch.object(ProductHuntAnalyzer, 'generate_article')
    @patch.object(ProductHuntAnalyzer, 'load_analyzed_products')
    def test_run_analysis_generate_fail(self, mock_load, mock_generate, 
                                       mock_analyze, mock_details, mock_fetch):
        """测试生成文章失败的情况"""
        mock_load.return_value = set()
        mock_fetch.return_value = [{'name': 'Test Product', 'votes': 100}]
        mock_details.return_value = {'name': 'Test Product', 'votes': 100}
        mock_analyze.return_value = {'overall_score': 80}
        mock_generate.return_value = False
        
        success = self.analyzer.run_analysis()
        self.assertFalse(success)


class TestMainFunction(unittest.TestCase):
    """测试主函数"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        os.makedirs('data', exist_ok=True)
        os.makedirs('content/posts', exist_ok=True)

    def tearDown(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch.object(ProductHuntAnalyzer, 'run_analysis')
    def test_main_success(self, mock_run):
        """测试主函数成功执行"""
        mock_run.return_value = True
        
        from producthunt_analyzer import main
        # 这应该不会抛出异常
        main()
        mock_run.assert_called_once()

    @patch.object(ProductHuntAnalyzer, 'run_analysis')
    def test_main_failure(self, mock_run):
        """测试主函数失败退出"""
        mock_run.return_value = False
        
        from producthunt_analyzer import main
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('requests.get')
    def test_full_workflow_mock(self, mock_get):
        """测试完整工作流程（使用Mock）"""
        # Mock第一次请求（获取产品列表）
        mock_html = '''
        <html>
            <div class="styles_item__abc123">
                <h3>Integration Test Product</h3>
                <a href="/posts/integration-test">Link</a>
                <span>This is an integration test product description</span>
                <span>999</span>
            </div>
        </html>
        '''
        
        # Mock第二次请求（获取产品详情）
        mock_detail_html = '''
        <html>
            <p>This is a comprehensive integration test product description with much more detail</p>
            <span class="tag">Integration</span>
            <span class="tag">Testing</span>
        </html>
        '''
        
        def mock_response_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            
            if 'producthunt.com/posts/' in url:
                mock_response.content = mock_detail_html.encode('utf-8')
            else:
                mock_response.content = mock_html.encode('utf-8')
            
            return mock_response
        
        mock_get.side_effect = mock_response_side_effect
        
        analyzer = ProductHuntAnalyzer()
        success = analyzer.run_analysis()
        
        # 验证结果
        self.assertTrue(success)
        
        # 检查生成的文件
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        expected_file = f"content/posts/producthunt-top3-review-{date_str}.md"
        self.assertTrue(os.path.exists(expected_file))
        
        # 检查历史记录文件
        self.assertTrue(os.path.exists('data/producthunt_products.json'))
        
        with open('data/producthunt_products.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
            self.assertEqual(history['total_products'], 1)


def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    try:
        import coverage
        cov = coverage.Coverage()
        cov.start()
        
        # 运行测试
        loader = unittest.TestLoader()
        suite = loader.discover('.', pattern='test_producthunt_analyzer.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("测试覆盖率报告:")
        print("="*50)
        cov.report(show_missing=True)
        
        # 生成HTML报告
        cov.html_report(directory='coverage_html_report')
        print(f"\n📊 详细覆盖率报告已生成到: coverage_html_report/")
        
        return result.wasSuccessful()
        
    except ImportError:
        print("⚠️  coverage 模块未安装，运行基础测试...")
        loader = unittest.TestLoader()
        suite = loader.discover('.', pattern='test_producthunt_analyzer.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 开始Product Hunt分析器单元测试...")
    success = run_tests_with_coverage()
    
    if success:
        print("\n✅ 所有测试通过！")
        exit(0)
    else:
        print("\n❌ 部分测试失败！")
        exit(1)