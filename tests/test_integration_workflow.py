#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
システム統合テスト - TDD RED Phase

PA-APIサクラチェッカー検出システムの統合テスト。
PAAPIClient, SakuraDetector, PlaywrightAutomationの全体統合を検証。

TDD RED Phase: 失敗する統合テストを先に書く
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from typing import List, Dict, Any
import pandas as pd

# これらのインポートは最初は失敗する（RED phase）
from tools.pa_api_client import PAAPIClient
from tools.sakura_detector import SakuraDetector, SakuraAnalysisResult  
from tools.playwright_automation import PlaywrightAutomation, SakuraCheckerResult
from tools.models import Product, IntegratedAffiliateLinkGenerator


class TestSystemIntegration(unittest.TestCase):
    """システム全体の統合テスト"""
    
    def setUp(self):
        """テスト前の初期設定"""
        # テスト用設定
        self.test_asins = [
            "B08XYZ1234",
            "B08ABC5678", 
            "B08DEF9012",
            "B08GHI3456",
            "B08JKL7890"
        ]
        
        # 統合システムの初期化（最初は失敗する）
        self.integrated_generator = IntegratedAffiliateLinkGenerator()
        
        # 期待される統合結果
        self.expected_integrated_result = {
            'products': [
                {
                    'asin': 'B08XYZ1234',
                    'title': 'Test Product 1',
                    'price': '¥1,299',
                    'rating': 4.5,
                    'review_count': 500,
                    'sakura_score': 25.0,
                    'confidence': 0.85,
                    'is_recommended': True,
                    'affiliate_link': 'https://amazon.co.jp/dp/B08XYZ1234/?tag=test-affiliate',
                    'quality_rank': 1
                }
            ],
            'total_processed': 5,
            'recommended_count': 3,
            'processing_time': 45.2,
            'quality_score': 92.5
        }
    
    def test_integrated_system_initialization(self):
        """統合システム初期化のテスト"""
        # 統合システムが正しく初期化されることを確認
        self.assertIsNotNone(self.integrated_generator)
        self.assertIsInstance(self.integrated_generator, IntegratedAffiliateLinkGenerator)
        
        # 必要なコンポーネントがセットアップされていることを確認
        self.assertIsNotNone(self.integrated_generator.paapi_client)
        self.assertIsNotNone(self.integrated_generator.sakura_detector)
        self.assertIsNotNone(self.integrated_generator.playwright_automation)
        
        # 設定が正しく初期化されていることを確認
        self.assertEqual(self.integrated_generator.batch_size, 15)
        self.assertEqual(self.integrated_generator.quality_threshold, 70.0)
        self.assertTrue(self.integrated_generator.enable_playwright)
    
    @patch('tools.pa_api_client.PAAPIClient.search_products')
    @patch('tools.sakura_detector.SakuraDetector.batch_analyze')
    @patch('tools.playwright_automation.PlaywrightAutomation.batch_check')
    def test_full_workflow_integration(self, mock_playwright, mock_sakura, mock_paapi):
        """フルワークフローの統合テスト"""
        # PA-API モック設定
        mock_paapi.return_value = [
            Product(
                asin="B08XYZ1234",
                name="Gaming Monitor 1",
                model="GM-001",
                brand="TestBrand",
                price=29999,
                rating=4.5,
                reviews_count=500
            ),
            Product(
                asin="B08ABC5678",
                name="Gaming Monitor 2", 
                model="GM-002",
                brand="TestBrand",
                price=39999,
                rating=4.2,
                reviews_count=300
            )
        ]
        
        # Sakura Detector モック設定  
        mock_sakura.return_value = [
            SakuraAnalysisResult(
                product_asin="B08XYZ1234",
                sakura_score=25.0,
                confidence_level=0.85,
                analysis_details={'suspicious_reviews': 50, 'total_reviews': 500}
            ),
            SakuraAnalysisResult(
                product_asin="B08ABC5678", 
                sakura_score=75.0,
                confidence_level=0.90,
                analysis_details={'suspicious_reviews': 200, 'total_reviews': 300}
            )
        ]
        
        # Playwright Automation モック設定
        mock_playwright.return_value = [
            SakuraCheckerResult(
                asin="B08XYZ1234",
                sakura_score=22.0,
                confidence_level=0.88,
                review_analysis={'suspicious_reviews': 50, 'total_reviews': 500, 'ratio': 0.1}
            ),
            SakuraCheckerResult(
                asin="B08ABC5678", 
                sakura_score=73.0,
                confidence_level=0.92,
                review_analysis={'suspicious_reviews': 200, 'total_reviews': 300, 'ratio': 0.67}
            )
        ]
        
        # フルワークフロー実行
        result = self.integrated_generator.process_affiliate_workflow(
            keyword="gaming monitor",
            max_products=2
        )
        
        # 統合結果の検証
        self.assertIsNotNone(result)
        self.assertIn('products', result)
        self.assertIn('total_processed', result)
        self.assertIn('recommended_count', result)
        self.assertIn('processing_time', result)
        self.assertIn('quality_score', result)
        
        # 品質フィルタリングの確認（サクラスコア高い商品は除外）
        recommended_products = [p for p in result['products'] if p['is_recommended']]
        self.assertEqual(len(recommended_products), 1)
        self.assertEqual(recommended_products[0]['asin'], "B08XYZ1234")
        
        # API呼び出し確認
        mock_paapi.assert_called_once_with("gaming monitor", max_results=2)
        mock_sakura.assert_called_once()
        mock_playwright.assert_called_once()
    
    def test_quality_assessment_integration(self):
        """品質評価統合のテスト"""
        # 品質評価システムの統合テスト
        test_products = [
            {
                'asin': 'B08XYZ1234',
                'rating': 4.5,
                'review_count': 500,
                'sakura_score': 25.0,
                'confidence': 0.85
            },
            {
                'asin': 'B08ABC5678',
                'rating': 4.0,
                'review_count': 100,
                'sakura_score': 80.0,
                'confidence': 0.90
            }
        ]
        
        # 品質評価実行
        quality_results = self.integrated_generator.assess_product_quality(test_products)
        
        # 品質スコアの検証
        self.assertIsInstance(quality_results, list)
        self.assertEqual(len(quality_results), 2)
        
        # 高品質商品の確認
        high_quality = [r for r in quality_results if r['quality_rank'] <= 3]
        self.assertEqual(len(high_quality), 1)
        self.assertEqual(high_quality[0]['asin'], 'B08XYZ1234')
    
    def test_error_handling_integration(self):
        """エラーハンドリング統合のテスト"""
        # API エラー時の統合テスト
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.side_effect = ConnectionError("PA-API Connection Failed")
            
            # エラーが適切に処理されることを確認
            result = self.integrated_generator.process_affiliate_workflow(
                keyword="test",
                max_products=5
            )
            
            # エラー時のレスポンス確認
            self.assertIsNotNone(result)
            self.assertIn('error', result)
            self.assertIn('PA-API Connection Failed', result['error'])
            self.assertEqual(result['total_processed'], 0)
    
    def test_performance_optimization_integration(self):
        """パフォーマンス最適化統合のテスト"""
        import time
        
        # 15商品処理の時間測定（目標：20分以内）
        start_time = time.time()
        
        # モック設定で高速化をシミュレート
        with patch.multiple(
            self.integrated_generator,
            paapi_client=Mock(),
            sakura_detector=Mock(),
            playwright_automation=Mock()
        ):
            self.integrated_generator.paapi_client.search_products.return_value = [
                Mock(asin=f"B08{i:07d}", title=f"Product {i}") for i in range(15)
            ]
            self.integrated_generator.sakura_detector.detect_sakura_products.return_value = [
                Mock(asin=f"B08{i:07d}", sakura_score=30.0) for i in range(15)
            ]
            self.integrated_generator.playwright_automation.batch_check.return_value = [
                Mock(asin=f"B08{i:07d}", sakura_score=25.0) for i in range(15)
            ]
            
            # 15商品の処理実行
            result = self.integrated_generator.process_affiliate_workflow(
                keyword="test products",
                max_products=15
            )
            
            elapsed_time = time.time() - start_time
            
            # パフォーマンス要件確認
            self.assertLess(elapsed_time, 1200)  # 20分以内（モックなので実際はもっと高速）
            self.assertEqual(result['total_processed'], 15)
            self.assertGreater(result['quality_score'], 80.0)
    
    def test_batch_processing_optimization(self):
        """バッチ処理最適化のテスト"""
        # バッチサイズによる処理効率の確認
        large_asin_list = [f"B08{i:07d}" for i in range(30)]
        
        # バッチ処理設定の確認
        self.assertEqual(self.integrated_generator.batch_size, 15)
        
        # バッチ処理実行のテスト（モック）
        with patch.object(self.integrated_generator, '_process_batch') as mock_process:
            mock_process.return_value = {'processed': 15, 'quality_score': 85.0}
            
            # 30商品を2バッチで処理
            result = self.integrated_generator.process_large_product_set(large_asin_list)
            
            # バッチ処理回数の確認
            self.assertEqual(mock_process.call_count, 2)
            self.assertIn('total_batches', result)
            self.assertEqual(result['total_batches'], 2)
    
    def test_data_consistency_validation(self):
        """データ一貫性検証のテスト"""
        # 異なるソースからのデータ一貫性チェック
        paapi_data = Product(
            asin="B08XYZ1234",
            name="Test Product",
            model="TEST-001",
            brand="TestBrand",
            rating=4.5,
            reviews_count=500
        )
        
        sakura_result = SakuraAnalysisResult(
            product_asin="B08XYZ1234",
            sakura_score=25.0,
            confidence_level=0.85,
            analysis_details={'suspicious_reviews': 50, 'total_reviews': 500}
        )
        
        playwright_result = SakuraCheckerResult(
            asin="B08XYZ1234",
            sakura_score=22.0,
            confidence_level=0.88
        )
        
        # データ一貫性の検証
        consistency_check = self.integrated_generator.validate_data_consistency(
            paapi_data, sakura_result, playwright_result
        )
        
        # 一貫性チェック結果の確認
        self.assertIsNotNone(consistency_check)
        self.assertTrue(consistency_check['is_consistent'])
        self.assertEqual(consistency_check['asin'], "B08XYZ1234")
        self.assertLess(abs(consistency_check['sakura_score_variance']), 10.0)
    
    def test_concurrent_processing_integration(self):
        """並行処理統合のテスト"""
        # 並行処理による処理時間短縮の確認
        import concurrent.futures
        
        # 並行処理設定
        self.integrated_generator.enable_concurrent_processing = True
        self.integrated_generator.max_workers = 3
        
        # 並行処理モック
        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
            mock_executor.return_value.__enter__.return_value.submit.return_value.result.return_value = {
                'processed': True, 'processing_time': 15.0
            }
            
            # 並行処理実行
            result = self.integrated_generator.process_concurrent_workflow(
                keywords=["gaming monitor", "mechanical keyboard", "wireless mouse"],
                max_products_per_keyword=5
            )
            
            # 並行処理結果の確認
            self.assertIsNotNone(result)
            self.assertIn('concurrent_results', result)
            self.assertEqual(len(result['concurrent_results']), 3)
    
    def test_affiliate_link_optimization(self):
        """アフィリエイトリンク最適化のテスト"""
        # アフィリエイトリンクの最適化機能テスト
        test_products = [
            {
                'asin': 'B08XYZ1234',
                'title': 'Gaming Monitor',
                'price': '¥29,999',
                'rating': 4.5,
                'sakura_score': 25.0,
                'quality_rank': 1
            }
        ]
        
        # アフィリエイトリンク最適化実行
        optimized_links = self.integrated_generator.optimize_affiliate_links(
            test_products,
            tracking_params={'utm_source': 'test', 'utm_medium': 'affiliate'}
        )
        
        # 最適化結果の確認
        self.assertIsInstance(optimized_links, list)
        self.assertEqual(len(optimized_links), 1)
        self.assertIn('utm_source=test', optimized_links[0]['affiliate_link'])
        self.assertIn('tag=', optimized_links[0]['affiliate_link'])


if __name__ == "__main__":
    unittest.main()