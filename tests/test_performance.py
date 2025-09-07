#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パフォーマンステスト - TDD RED Phase

PA-APIサクラ検出システムのパフォーマンス要件テスト。
15商品を20分以内で処理する要件の検証。

TDD RED Phase: 厳しいパフォーマンス要件の失敗テストを先に書く
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
import time
import psutil
import os
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
import threading

# System components
from tools.models import IntegratedAffiliateLinkGenerator, Product
from tools.pa_api_client import PAAPIClient
from tools.sakura_detector import SakuraDetector, SakuraAnalysisResult
from tools.playwright_automation import PlaywrightAutomation, SakuraCheckerResult


class PerformanceMonitor:
    """パフォーマンス監視クラス"""
    
    def __init__(self):
        """初期化"""
        self.start_time = None
        self.end_time = None
        self.peak_memory = 0
        self.initial_memory = 0
        self.api_call_times = []
        self.process = psutil.Process(os.getpid())
    
    def start_monitoring(self):
        """監視開始"""
        self.start_time = time.time()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.initial_memory
        
        # メモリ監視スレッド開始
        self.monitoring_active = True
        self.memory_thread = threading.Thread(target=self._monitor_memory)
        self.memory_thread.daemon = True
        self.memory_thread.start()
    
    def stop_monitoring(self):
        """監視停止"""
        self.end_time = time.time()
        self.monitoring_active = False
        if hasattr(self, 'memory_thread'):
            self.memory_thread.join(timeout=1.0)
    
    def _monitor_memory(self):
        """メモリ使用量監視"""
        while self.monitoring_active:
            try:
                current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                self.peak_memory = max(self.peak_memory, current_memory)
                time.sleep(0.1)  # 100ms間隔で監視
            except psutil.NoSuchProcess:
                break
    
    def get_results(self) -> Dict[str, Any]:
        """監視結果を取得"""
        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time
            return {
                'total_time_minutes': total_time / 60,
                'total_time_seconds': total_time,
                'peak_memory_mb': self.peak_memory,
                'memory_increase_mb': self.peak_memory - self.initial_memory,
                'api_call_count': len(self.api_call_times),
                'avg_api_time': sum(self.api_call_times) / len(self.api_call_times) if self.api_call_times else 0
            }
        return {}
    
    def record_api_call_time(self, duration: float):
        """API呼び出し時間を記録"""
        self.api_call_times.append(duration)


class TestPerformanceRequirements(unittest.TestCase):
    """パフォーマンス要件テスト"""
    
    def setUp(self):
        """テスト前の初期設定"""
        self.integrated_generator = IntegratedAffiliateLinkGenerator()
        self.monitor = PerformanceMonitor()
        
        # パフォーマンス要件定義
        self.MAX_PROCESSING_TIME_MINUTES = 20.0  # 20分以内
        self.MAX_MEMORY_USAGE_MB = 500.0  # 最大500MB
        self.MAX_API_RESPONSE_TIME_SECONDS = 5.0  # API応答時間5秒以内
        self.TARGET_PRODUCT_COUNT = 15  # 15商品処理
        
        # テスト用商品データ
        self.test_products_15 = self._generate_test_products(15)
    
    def _generate_test_products(self, count: int) -> List[Product]:
        """テスト用商品データ生成"""
        products = []
        for i in range(count):
            product = Product(
                asin=f"B08TEST{i:03d}",
                name=f"Test Gaming Monitor {i+1}",
                model=f"TGM-{i+1:03d}",
                brand="TestBrand",
                price=25000 + (i * 5000),
                rating=4.0 + (i * 0.1) % 1.0,
                reviews_count=100 + (i * 50)
            )
            products.append(product)
        return products
    
    def test_15_products_20_minutes_requirement_RED(self):
        """15商品20分処理要件テスト（RED Phase - 厳しい要件で失敗させる）"""
        # 厳しいパフォーマンス要件でテスト
        STRICT_TIME_LIMIT = 10.0  # 10分以内（実際は20分だが、REDフェーズでは厳しく設定）
        
        # パフォーマンス監視開始
        self.monitor.start_monitoring()
        
        try:
            # 15商品の実際処理（モック使用で時間短縮）
            with patch.multiple(
                self.integrated_generator,
                paapi_client=Mock(),
                sakura_detector=Mock(),
                playwright_automation=Mock()
            ):
                # モック設定
                self.integrated_generator.paapi_client.search_products.return_value = self.test_products_15
                self.integrated_generator.sakura_detector.batch_analyze.return_value = [
                    SakuraAnalysisResult(
                        product_asin=product.asin,
                        sakura_score=30.0 + (i * 5),
                        confidence_level=0.85,
                        analysis_details={'suspicious_reviews': 50, 'total_reviews': 500}
                    )
                    for i, product in enumerate(self.test_products_15)
                ]
                self.integrated_generator.playwright_automation.batch_check.return_value = [
                    SakuraCheckerResult(
                        asin=product.asin,
                        sakura_score=25.0 + (i * 3),
                        confidence_level=0.88,
                        review_analysis={'suspicious_reviews': 40, 'total_reviews': 500, 'ratio': 0.08}
                    )
                    for i, product in enumerate(self.test_products_15)
                ]
                
                # 15商品処理実行
                result = self.integrated_generator.process_affiliate_workflow(
                    keyword="gaming monitor performance test",
                    max_products=15
                )
                
        finally:
            # パフォーマンス監視停止
            self.monitor.stop_monitoring()
        
        # 結果取得
        perf_results = self.monitor.get_results()
        
        # パフォーマンス要件検証（厳しい要件でREDフェーズ）
        self.assertIsNotNone(result, "処理結果が取得できませんでした")
        self.assertEqual(result['total_processed'], 15, "15商品が処理されませんでした")
        
        # 時間要件（厳しく設定してREDフェーズで失敗させる）
        processing_time_minutes = perf_results['total_time_minutes']
        self.assertLess(
            processing_time_minutes, 
            STRICT_TIME_LIMIT, 
            f"処理時間が{STRICT_TIME_LIMIT}分を超過: {processing_time_minutes:.2f}分"
        )
        
        # メモリ要件
        peak_memory = perf_results['peak_memory_mb']
        self.assertLess(
            peak_memory,
            self.MAX_MEMORY_USAGE_MB,
            f"メモリ使用量が制限を超過: {peak_memory:.2f}MB"
        )
        
        # 品質要件
        self.assertGreater(result['quality_score'], 80.0, "品質スコアが80%を下回りました")
        
        print(f"\nパフォーマンステスト結果:")
        print(f"処理時間: {processing_time_minutes:.2f}分")
        print(f"ピークメモリ: {peak_memory:.2f}MB")
        print(f"品質スコア: {result['quality_score']:.1f}%")
    
    def test_api_response_time_requirements_RED(self):
        """API応答時間要件テスト（GREEN Phase - キャッシュ最適化版）"""
        # 改善されたAPI応答時間要件
        OPTIMIZED_API_TIME_LIMIT = 0.5  # キャッシュ使用時の高速応答
        
        # 各APIコンポーネントの応答時間テスト
        test_asins = [f"B08API{i:03d}" for i in range(5)]
        
        # 1回目：キャッシュなしでの呼び出し
        start_time = time.time()
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.return_value = self.test_products_15[:5]
            
            # 最初の呼び出し（キャッシュに保存される）
            result1 = self.integrated_generator._get_cached_api_response(
                "paapi_search",
                mock_paapi,
                "test", max_results=5
            )

        first_call_time = time.time() - start_time

        # 2回目：キャッシュありでの呼び出し
        start_time = time.time()
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.return_value = self.test_products_15[:5]
            
            # 2回目の呼び出し（キャッシュから高速取得）
            result2 = self.integrated_generator._get_cached_api_response(
                "paapi_search", 
                mock_paapi,
                "test", max_results=5
            )

        cached_call_time = time.time() - start_time
        self.monitor.record_api_call_time(cached_call_time)

        # キャッシュ効果による高速応答をテスト
        self.assertLess(
            cached_call_time,
            OPTIMIZED_API_TIME_LIMIT,
            f"キャッシュAPI応答時間が{OPTIMIZED_API_TIME_LIMIT}秒を超過: {cached_call_time:.3f}秒"
        )
        
        print(f"\nAPI応答時間最適化テスト結果:")
        print(f"初回呼び出し: {first_call_time:.3f}秒")
        print(f"キャッシュ使用: {cached_call_time:.3f}秒")
        
        # SakuraDetector応答時間テスト
        start_time = time.time()
        with patch('tools.sakura_detector.SakuraDetector.batch_analyze') as mock_sakura:
            mock_sakura.return_value = [
                SakuraAnalysisResult(
                    product_asin=asin,
                    sakura_score=40.0,
                    confidence_level=0.85,
                    analysis_details={}
                ) for asin in test_asins
            ]
            
            # キャッシュ最適化でSakuraDetectorも高速化
            result = self.integrated_generator._get_cached_api_response(
                "sakura_batch",
                mock_sakura,
                self.test_products_15[:5]
            )
        
        sakura_time = time.time() - start_time
        self.monitor.record_api_call_time(sakura_time)
        
        # 厳しい応答時間要件でテスト
        self.assertLess(
            sakura_time,
            OPTIMIZED_API_TIME_LIMIT,
            f"SakuraDetector応答時間が{OPTIMIZED_API_TIME_LIMIT}秒を超過: {sakura_time:.2f}秒"
        )
    
    def test_memory_usage_requirements_RED(self):
        """メモリ使用量要件テスト（RED Phase）"""
        # 厳しいメモリ使用量要件
        STRICT_MEMORY_LIMIT = 200.0  # 200MB以内（実際は500MBだが、REDフェーズでは厳しく設定）
        
        # パフォーマンス監視開始
        self.monitor.start_monitoring()
        
        try:
            # 大量データ処理シミュレート（メモリ使用量を意図的に増加）
            large_products = self._generate_test_products(100)  # 100商品で負荷テスト
            
            # 意図的にメモリを多く使用する処理
            memory_intensive_data = []
            for i in range(1000):  # メモリ集約的な処理をシミュレート
                memory_intensive_data.append([j for j in range(1000)])
            
            # システム統合処理実行
            with patch.multiple(
                self.integrated_generator,
                paapi_client=Mock(),
                sakura_detector=Mock(),
                playwright_automation=Mock()
            ):
                # モック設定
                self.integrated_generator.paapi_client.search_products.return_value = large_products
                
                result = self.integrated_generator.process_affiliate_workflow(
                    keyword="memory intensive test",
                    max_products=100
                )
                
        finally:
            # パフォーマンス監視停止
            self.monitor.stop_monitoring()
        
        # メモリ使用量検証
        perf_results = self.monitor.get_results()
        peak_memory = perf_results['peak_memory_mb']
        
        # 厳しいメモリ要件でテスト（REDフェーズで失敗）
        self.assertLess(
            peak_memory,
            STRICT_MEMORY_LIMIT,
            f"メモリ使用量が{STRICT_MEMORY_LIMIT}MBを超過: {peak_memory:.2f}MB"
        )
    
    def test_concurrent_processing_performance_RED(self):
        """並行処理パフォーマンステスト（RED Phase）"""
        # 厳しい並行処理時間要件
        STRICT_CONCURRENT_TIME_LIMIT = 5.0  # 5分以内（REDフェーズ用の厳しい要件）
        
        # パフォーマンス監視開始
        self.monitor.start_monitoring()
        
        try:
            # 複数キーワードでの並行処理テスト
            keywords = [
                "gaming monitor",
                "mechanical keyboard", 
                "wireless mouse",
                "gaming headset",
                "ultrawide monitor"
            ]
            
            with patch.multiple(
                self.integrated_generator,
                paapi_client=Mock(),
                sakura_detector=Mock(),
                playwright_automation=Mock()
            ):
                # モック設定（処理時間をシミュレート）
                def slow_mock_process(*args, **kwargs):
                    time.sleep(2.0)  # 意図的に遅い処理をシミュレート
                    return self.test_products_15[:3]  # 3商品ずつ返却
                
                self.integrated_generator.paapi_client.search_products.side_effect = slow_mock_process
                self.integrated_generator.sakura_detector.batch_analyze.return_value = []
                self.integrated_generator.playwright_automation.batch_check.return_value = []
                
                # 並行処理実行
                result = self.integrated_generator.process_concurrent_workflow(
                    keywords=keywords,
                    max_products_per_keyword=3
                )
                
        finally:
            # パフォーマンス監視停止
            self.monitor.stop_monitoring()
        
        # 並行処理時間検証
        perf_results = self.monitor.get_results()
        concurrent_time_minutes = perf_results['total_time_minutes']
        
        # 結果検証
        self.assertIsNotNone(result, "並行処理結果が取得できませんでした")
        self.assertEqual(len(result['concurrent_results']), 5, "5キーワードの処理が完了していません")
        
        # 厳しい時間要件でテスト（REDフェーズで失敗）
        self.assertLess(
            concurrent_time_minutes,
            STRICT_CONCURRENT_TIME_LIMIT,
            f"並行処理時間が{STRICT_CONCURRENT_TIME_LIMIT}分を超過: {concurrent_time_minutes:.2f}分"
        )
    
    def test_cache_performance_improvement_RED(self):
        """キャッシュパフォーマンス改善テスト（RED Phase）"""
        # 厳しいキャッシュ効果要件
        MINIMUM_CACHE_IMPROVEMENT = 50.0  # 50%以上の改善を要求（REDフェーズ用の厳しい要件）
        
        # キャッシュなし処理時間測定
        start_time = time.time()
        with patch.multiple(
            self.integrated_generator,
            paapi_client=Mock(),
            sakura_detector=Mock(),
            playwright_automation=Mock()
        ):
            # モック設定（処理時間をシミュレート）
            def slow_processing(*args, **kwargs):
                time.sleep(1.0)  # 1秒の処理時間をシミュレート
                return self.test_products_15[:5]
            
            self.integrated_generator.paapi_client.search_products.side_effect = slow_processing
            
            # 1回目の処理（キャッシュなし）
            result1 = self.integrated_generator.process_affiliate_workflow("cache test 1", max_products=5)
        
        no_cache_time = time.time() - start_time
        
        # キャッシュあり処理時間測定
        start_time = time.time()
        
        # 2回目の処理（キャッシュありをシミュレート）
        # ただし、REDフェーズでは意図的にキャッシュ効果を低く設定
        def cached_processing(*args, **kwargs):
            time.sleep(0.8)  # わずかな改善のみ（REDフェーズ用）
            return self.test_products_15[:5]
        
        with patch.object(self.integrated_generator.paapi_client, 'search_products', side_effect=cached_processing):
            result2 = self.integrated_generator.process_affiliate_workflow("cache test 2", max_products=5)
        
        cache_time = time.time() - start_time
        
        # キャッシュ効果計算
        improvement_percentage = ((no_cache_time - cache_time) / no_cache_time) * 100
        
        # 厳しいキャッシュ改善要件でテスト（REDフェーズで失敗）
        self.assertGreater(
            improvement_percentage,
            MINIMUM_CACHE_IMPROVEMENT,
            f"キャッシュによる改善が{MINIMUM_CACHE_IMPROVEMENT}%未満: {improvement_percentage:.1f}%改善"
        )
        
        print(f"\nキャッシュパフォーマンステスト結果:")
        print(f"キャッシュなし: {no_cache_time:.2f}秒")
        print(f"キャッシュあり: {cache_time:.2f}秒")
        print(f"改善率: {improvement_percentage:.1f}%")


if __name__ == "__main__":
    unittest.main()