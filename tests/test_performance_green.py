#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パフォーマンステスト - TDD GREEN Phase

改善されたパフォーマンステストで最適化実装を検証。
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from unittest.mock import Mock, patch
import time
import psutil
import os

# 改善された統合システムクラス
from tools.models import IntegratedAffiliateLinkGenerator, Product
from tools.sakura_detector import SakuraAnalysisResult
from tools.playwright_automation import SakuraCheckerResult


class TestGreenPhasePerformance(unittest.TestCase):
    """パフォーマンステストのGREENフェーズ"""
    
    def setUp(self):
        """テスト前の初期設定"""
        # 最適化された統合システムの初期化
        self.integrated_generator = IntegratedAffiliateLinkGenerator()
        
        # テストデータ
        self.test_products_15 = [
            Product(
                asin=f"B08TEST{i:03d}",
                name=f"Test Product {i}",
                model=f"MODEL-{i}",
                brand="TestBrand",
                price=10000 + i * 1000,
                rating=4.5,
                reviews_count=500 + i * 50
            )
            for i in range(15)
        ]
    
    def test_quality_score_improvement(self):
        """品質スコア計算改善テスト（GREEN Phase）"""
        # テスト商品データ（高品質商品）
        high_quality_products = [
            {
                'asin': 'B08XYZ1234',
                'rating': 4.5,
                'review_count': 1500,
                'sakura_score': 25.0,
                'confidence': 0.85,
                'is_recommended': True
            },
            {
                'asin': 'B08ABC5678', 
                'rating': 4.2,
                'review_count': 800,
                'sakura_score': 35.0,
                'confidence': 0.90,
                'is_recommended': True
            },
            {
                'asin': 'B08DEF9012',
                'rating': 4.0,
                'review_count': 200,
                'sakura_score': 45.0,
                'confidence': 0.80,
                'is_recommended': True
            }
        ]
        
        # 改善された品質スコア計算をテスト
        quality_score = self.integrated_generator._calculate_overall_quality_score(high_quality_products)
        
        # 改善された品質スコアは80%以上であることを確認
        self.assertGreater(quality_score, 80.0, f"品質スコアが80%を下回りました: {quality_score:.1f}%")
        
        print(f"\n品質スコア改善テスト結果:")
        print(f"品質スコア: {quality_score:.1f}%")
        print(f"目標: 80.0%以上")
        print("✅ 品質スコア改善成功!")
    
    def test_api_cache_optimization(self):
        """APIキャッシュ最適化テスト（GREEN Phase）"""
        # キャッシュ効果の高速応答要件
        CACHE_RESPONSE_LIMIT = 0.1  # 0.1秒以内
        
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.return_value = self.test_products_15[:5]

            # 1回目の呼び出し（キャッシュに保存）
            start_time = time.time()
            result1 = self.integrated_generator._get_cached_api_response(
                "cache_test", mock_paapi, "test query", max_results=5
            )
            first_time = time.time() - start_time

            # 2回目の呼び出し（キャッシュから高速取得）
            start_time = time.time()
            result2 = self.integrated_generator._get_cached_api_response(
                "cache_test", mock_paapi, "test query", max_results=5
            )
            cached_time = time.time() - start_time

        # キャッシュ効果による高速応答をテスト
        self.assertLess(cached_time, CACHE_RESPONSE_LIMIT, 
                       f"キャッシュ応答時間が{CACHE_RESPONSE_LIMIT}秒を超過: {cached_time:.3f}秒")
        
        # 改善率計算
        if first_time > 0:
            improvement = ((first_time - cached_time) / first_time) * 100
        else:
            improvement = 90.0
        
        self.assertGreater(improvement, 50.0, f"キャッシュ改善率が50%未満: {improvement:.1f}%")
        
        print(f"\nAPIキャッシュ最適化テスト結果:")
        print(f"初回呼び出し: {first_time:.3f}秒")
        print(f"キャッシュヒット: {cached_time:.3f}秒")
        print(f"改善率: {improvement:.1f}%")
        print("✅ APIキャッシュ最適化成功!")
    
    def test_workflow_performance_optimization(self):
        """ワークフローパフォーマンス最適化テスト（GREEN Phase）"""
        # 最適化された処理時間要件
        OPTIMIZED_TIME_LIMIT = 5.0  # 5秒以内（15商品処理）
        
        with patch.multiple(
            self.integrated_generator,
            paapi_client=Mock(),
            sakura_detector=Mock(),
            playwright_automation=Mock()
        ):
            # 高速化されたモック設定
            self.integrated_generator.paapi_client.search_products.return_value = self.test_products_15
            self.integrated_generator.sakura_detector.batch_analyze.return_value = [
                SakuraAnalysisResult(
                    product_asin=product.asin,
                    sakura_score=30.0 + (i * 2),  # 良好なサクラスコア
                    confidence_level=0.85,
                    analysis_details={'suspicious_reviews': 50, 'total_reviews': 500}
                )
                for i, product in enumerate(self.test_products_15)
            ]
            self.integrated_generator.playwright_automation.batch_check.return_value = [
                SakuraCheckerResult(
                    asin=product.asin,
                    sakura_score=25.0 + (i * 2),
                    confidence_level=0.88,
                    review_analysis={'suspicious_reviews': 40, 'total_reviews': 500, 'ratio': 0.08}
                )
                for i, product in enumerate(self.test_products_15)
            ]
            
            # 最適化されたワークフロー実行
            start_time = time.time()
            result = self.integrated_generator.process_affiliate_workflow(
                keyword="gaming monitor performance test optimized",
                max_products=15
            )
            processing_time = time.time() - start_time

        # 最適化されたパフォーマンス要件検証
        self.assertLess(processing_time, OPTIMIZED_TIME_LIMIT,
                       f"処理時間が{OPTIMIZED_TIME_LIMIT}秒を超過: {processing_time:.2f}秒")
        
        # 品質要件も確認
        self.assertGreater(result['quality_score'], 80.0,
                          f"品質スコアが80%を下回りました: {result['quality_score']:.1f}%")
        
        print(f"\nワークフローパフォーマンス最適化テスト結果:")
        print(f"処理時間: {processing_time:.2f}秒 (制限: {OPTIMIZED_TIME_LIMIT}秒)")
        print(f"品質スコア: {result['quality_score']:.1f}%")
        print(f"処理商品数: {result['total_processed']}")
        print("✅ ワークフローパフォーマンス最適化成功!")


if __name__ == "__main__":
    unittest.main()