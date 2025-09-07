#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SakuraDetectorのテスト - TDD RED Phase

統計的異常値検出とレビューパターン分析による
サクラレビュー検出システムのテスト。

TDD RED Phase: 失敗するテストを先に書く
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
import pandas as pd
import numpy as np

# These imports will fail initially (RED phase)
from tools.sakura_detector import (
    SakuraDetector,
    SakuraAnalysisResult,
    ReviewPattern,
    StatisticalAnomaly
)
from tools.models import Product, ProductReview, SakuraScore


class TestSakuraDetector(unittest.TestCase):
    """SakuraDetectorの基本機能テスト"""
    
    def setUp(self):
        """テスト前の初期設定"""
        self.detector = SakuraDetector()
        
        # テスト用商品データ
        self.test_product = Product(
            asin="B08XYZ1234",
            name="テスト商品",
            model="TEST-001",
            brand="TestBrand",
            price=29800,
            rating=4.5,
            reviews_count=1500
        )
        
        # 正常な商品データ（自然な分布）
        self.normal_product = Product(
            asin="B08ABC5678",
            name="正常商品",
            model="NORMAL-001",
            brand="NormalBrand",
            price=19800,
            rating=3.8,
            reviews_count=350
        )
        
        # サクラ疑い商品データ（異常な分布）
        self.suspicious_product = Product(
            asin="B08DEF9012",
            name="疑惑商品",
            model="SUS-001",
            brand="SusBrand",
            price=9800,
            rating=4.9,  # 異常に高い評価
            reviews_count=2000  # 異常に多いレビュー数
        )
    
    def test_detector_initialization(self):
        """SakuraDetector初期化のテスト"""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector, SakuraDetector)
        
        # 閾値設定の確認
        self.assertEqual(self.detector.anomaly_threshold, 0.3)
        self.assertEqual(self.detector.min_reviews_for_analysis, 10)
    
    def test_analyze_single_product(self):
        """単一商品の分析テスト"""
        result = self.detector.analyze_product(self.test_product)
        
        self.assertIsInstance(result, SakuraAnalysisResult)
        self.assertEqual(result.product_asin, "B08XYZ1234")
        self.assertIsNotNone(result.sakura_score)
        self.assertIsInstance(result.sakura_score, float)
        self.assertTrue(0.0 <= result.sakura_score <= 1.0)
        
        # 分析詳細の確認
        self.assertIn('statistical_anomaly', result.analysis_details)
        self.assertIn('review_pattern', result.analysis_details)
        self.assertIn('confidence_level', result.analysis_details)
    
    def test_statistical_anomaly_detection(self):
        """統計的異常値検出のテスト"""
        # カテゴリ内の商品群データ
        category_products = [
            self.normal_product,
            Product(asin="B001", name="商品1", model="M1", brand="B1", rating=3.5, reviews_count=200),
            Product(asin="B002", name="商品2", model="M2", brand="B2", rating=4.0, reviews_count=450),
            Product(asin="B003", name="商品3", model="M3", brand="B3", rating=3.7, reviews_count=320),
            self.suspicious_product  # 異常値
        ]
        
        anomaly = self.detector.detect_statistical_anomaly(
            self.suspicious_product,
            category_products
        )
        
        self.assertIsInstance(anomaly, StatisticalAnomaly)
        self.assertTrue(anomaly.is_anomaly)
        self.assertGreater(anomaly.z_score_rating, 1.5)  # 1.5σ以上の異常
        self.assertGreater(anomaly.z_score_reviews, 1.5)
        
        # 正常商品は異常値として検出されない
        normal_anomaly = self.detector.detect_statistical_anomaly(
            self.normal_product,
            category_products
        )
        self.assertFalse(normal_anomaly.is_anomaly)
    
    def test_review_pattern_analysis(self):
        """レビューパターン分析のテスト"""
        # テスト用レビューデータ
        reviews = [
            ProductReview(
                review_id="R001",
                product_asin="B08XYZ1234",
                reviewer_name="レビュアー1",
                rating=5,
                title="素晴らしい",
                content="とても良い商品です。" * 10,  # 長いコンテンツ
                review_date=pd.Timestamp("2024-01-01"),
                verified_purchase=True,
                helpful_count=50,
                total_votes=60
            ),
            ProductReview(
                review_id="R002",
                product_asin="B08XYZ1234",
                reviewer_name="カスタマー",  # 汎用的な名前
                rating=5,
                title="最高",
                content="良い",  # 短いコンテンツ
                review_date=pd.Timestamp("2024-01-02"),
                verified_purchase=False,  # 未購入
                helpful_count=0,
                total_votes=10
            )
        ]
        
        pattern = self.detector.analyze_review_pattern(reviews)
        
        self.assertIsInstance(pattern, ReviewPattern)
        self.assertGreater(pattern.five_star_ratio, 0.8)  # 5つ星比率が高い
        self.assertLess(pattern.verified_purchase_ratio, 0.6)  # 購入確認率が低い
        self.assertTrue(pattern.has_suspicious_pattern)
    
    def test_review_velocity_analysis(self):
        """レビュー投稿速度分析のテスト"""
        # 短期間に大量のレビューが投稿されたケース
        rapid_reviews = []
        base_date = pd.Timestamp("2024-01-01")
        
        # 3日間で100件のレビュー（異常な速度）
        for i in range(100):
            rapid_reviews.append(ProductReview(
                review_id=f"R{i:03d}",
                product_asin="B08DEF9012",
                reviewer_name=f"User{i}",
                rating=5,
                title="Great",
                content="Good product",
                review_date=base_date + pd.Timedelta(days=i//34),
                verified_purchase=False,
                helpful_count=0,
                total_votes=0
            ))
        
        velocity = self.detector.calculate_review_velocity(rapid_reviews)
        
        self.assertGreater(velocity, 20.0)  # 日あたり20件以上は異常
        self.assertTrue(self.detector.is_velocity_suspicious(velocity))
    
    def test_batch_analysis(self):
        """複数商品の一括分析テスト"""
        products = [
            self.normal_product,
            self.test_product,
            self.suspicious_product
        ]
        
        results = self.detector.batch_analyze(products)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, SakuraAnalysisResult)
        
        # サクラ度スコアでソート確認
        sorted_results = sorted(results, key=lambda x: x.sakura_score)
        self.assertEqual(sorted_results[0].product_asin, self.normal_product.asin)
        self.assertEqual(sorted_results[-1].product_asin, self.suspicious_product.asin)
    
    def test_category_comparison(self):
        """カテゴリ内比較分析のテスト"""
        category = "Electronics/Computers"
        
        # カテゴリ内の商品群を取得（モック）
        with patch.object(self.detector, 'get_category_products') as mock_get:
            mock_get.return_value = [
                self.normal_product,
                Product(asin="B004", name="商品4", model="M4", brand="B4", rating=3.9, reviews_count=280),
                Product(asin="B005", name="商品5", model="M5", brand="B5", rating=4.1, reviews_count=420)
            ]
            
            comparison = self.detector.compare_with_category(
                self.suspicious_product,
                category
            )
            
            self.assertIsNotNone(comparison)
            self.assertIn('percentile_rating', comparison)
            self.assertIn('percentile_reviews', comparison)
            self.assertIn('deviation_score', comparison)
            
            # 異常商品は高いパーセンタイル値を持つ
            self.assertGreater(comparison['percentile_rating'], 90)
            self.assertGreater(comparison['percentile_reviews'], 90)
    
    def test_confidence_scoring(self):
        """信頼度スコアリングのテスト"""
        # データが少ない場合の信頼度
        low_data_product = Product(
            asin="B006",
            name="新商品",
            model="NEW-001",
            brand="NewBrand",
            rating=4.8,
            reviews_count=5  # レビューが少ない
        )
        
        result = self.detector.analyze_product(low_data_product)
        
        # データ不足の場合、信頼度が低い
        self.assertLess(result.confidence_level, 0.5)
        self.assertIn('insufficient_data', result.warnings)
    
    def test_sakura_detection_integration(self):
        """サクラ検出の統合テスト"""
        # 総合的なサクラ判定
        suspicious_result = self.detector.analyze_product(self.suspicious_product)
        normal_result = self.detector.analyze_product(self.normal_product)
        
        # 疑惑商品はサクラとして検出（閾値30%）
        self.assertTrue(suspicious_result.is_suspicious(threshold=0.3))
        self.assertGreater(suspicious_result.sakura_score, 0.3)
        
        # 正常商品はサクラとして検出されない
        self.assertFalse(normal_result.is_suspicious(threshold=0.3))
        self.assertLess(normal_result.sakura_score, 0.3)
    
    def test_export_analysis_report(self):
        """分析レポート出力のテスト"""
        result = self.detector.analyze_product(self.test_product)
        report = result.to_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn('product_asin', report)
        self.assertIn('sakura_score', report)
        self.assertIn('risk_level', report)
        self.assertIn('analysis_timestamp', report)
        self.assertIn('recommendations', report)
        
        # リスクレベルの確認
        self.assertIn(report['risk_level'], ['LOW', 'MEDIUM', 'HIGH'])
    
    def test_is_suspicious_method(self):
        """is_suspiciousメソッドの単体テスト（閾値30%）"""
        # 低いスコア（非疑惑）
        self.assertFalse(self.detector.is_suspicious(0.2))
        self.assertFalse(self.detector.is_suspicious(0.29))
        
        # 閾値を超えるスコア（疑惑）
        self.assertTrue(self.detector.is_suspicious(0.31))
        self.assertTrue(self.detector.is_suspicious(0.5))
        self.assertTrue(self.detector.is_suspicious(1.0))
        
        # カスタム閾値のテスト
        self.assertFalse(self.detector.is_suspicious(0.4, threshold=0.5))
        self.assertTrue(self.detector.is_suspicious(0.6, threshold=0.5))
    
    def test_temporal_analysis_rating_surge(self):
        """時系列分析：評価急上昇検出のテスト（TDD RED Phase）"""
        # 評価履歴データ（時間とともに急上昇）
        rating_history = [
            {'date': pd.Timestamp('2024-01-01'), 'rating': 3.2, 'review_count': 100},
            {'date': pd.Timestamp('2024-01-02'), 'rating': 3.3, 'review_count': 105},
            {'date': pd.Timestamp('2024-01-03'), 'rating': 4.8, 'review_count': 200},  # 急上昇
            {'date': pd.Timestamp('2024-01-04'), 'rating': 4.9, 'review_count': 300}   # さらに上昇
        ]
        
        # 異常な評価上昇を検出
        surge_score = self.detector.detect_rating_surge(rating_history)
        
        self.assertIsInstance(surge_score, float)
        self.assertGreater(surge_score, 0.5)  # 異常な上昇として検出
        self.assertTrue(self.detector.is_rating_surge_suspicious(surge_score))
    
    def test_temporal_analysis_review_burst(self):
        """時系列分析：レビューバースト検出のテスト（TDD RED Phase）"""
        # 通常の投稿パターン
        normal_reviews = []
        for i in range(30):  # 30日間
            normal_reviews.append(ProductReview(
                review_id=f"N{i:03d}",
                product_asin="B08ABC5678",
                reviewer_name=f"NormalUser{i}",
                rating=4,
                title="Good product",
                content="This is a decent product with good quality.",
                review_date=pd.Timestamp('2024-01-01') + pd.Timedelta(days=i),
                verified_purchase=True,
                helpful_count=5,
                total_votes=10
            ))
        
        # バーストパターン（3日間で100件）
        burst_reviews = []
        for i in range(100):
            burst_reviews.append(ProductReview(
                review_id=f"B{i:03d}",
                product_asin="B08DEF9012",
                reviewer_name=f"BurstUser{i}",
                rating=5,
                title="Amazing!",
                content="Great!",
                review_date=pd.Timestamp('2024-01-01') + pd.Timedelta(days=i//34),
                verified_purchase=False,
                helpful_count=0,
                total_votes=0
            ))
        
        # 時系列バースト分析
        normal_burst_score = self.detector.analyze_temporal_burst(normal_reviews)
        burst_score = self.detector.analyze_temporal_burst(burst_reviews)
        
        self.assertLess(normal_burst_score, 0.3)  # 通常パターンは低スコア
        self.assertGreater(burst_score, 0.7)     # バーストパターンは高スコア
    
    def test_temporal_analysis_periodic_patterns(self):
        """時系列分析：周期的パターン検出のテスト（TDD RED Phase）"""
        # 人工的な周期パターン（毎週同じ曜日に大量投稿）
        periodic_reviews = []
        base_date = pd.Timestamp('2024-01-01')  # 月曜日
        
        for week in range(8):  # 8週間
            # 毎週月曜日に20件の高評価レビュー
            monday = base_date + pd.Timedelta(weeks=week)
            for i in range(20):
                periodic_reviews.append(ProductReview(
                    review_id=f"P{week}_{i:02d}",
                    product_asin="B08GHI3456",
                    reviewer_name=f"PeriodicUser{week}_{i}",
                    rating=5,
                    title="Perfect",
                    content="Excellent product",
                    review_date=monday + pd.Timedelta(hours=i),
                    verified_purchase=False,
                    helpful_count=0,
                    total_votes=0
                ))
        
        # 周期性分析
        periodicity_score = self.detector.detect_periodic_patterns(periodic_reviews)
        
        self.assertIsInstance(periodicity_score, float)
        self.assertGreater(periodicity_score, 0.6)  # 高い周期性を検出
        self.assertTrue(self.detector.is_periodic_pattern_suspicious(periodicity_score))
    
    def test_temporal_analysis_comprehensive_score(self):
        """時系列分析：総合スコア計算のテスト（TDD RED Phase）"""
        # テスト商品の評価履歴
        rating_history = [
            {'date': pd.Timestamp('2024-01-01'), 'rating': 3.0, 'review_count': 50},
            {'date': pd.Timestamp('2024-01-05'), 'rating': 4.9, 'review_count': 500}  # 急激な変化
        ]
        
        # レビュー履歴（バーストパターン）
        reviews = []
        for i in range(50):
            reviews.append(ProductReview(
                review_id=f"T{i:03d}",
                product_asin="B08JKL7890",
                reviewer_name=f"TestUser{i}",
                rating=5,
                title="Great",
                content="Good",
                review_date=pd.Timestamp('2024-01-05') + pd.Timedelta(hours=i//10),
                verified_purchase=False,
                helpful_count=0,
                total_votes=0
            ))
        
        # 総合的な時系列分析
        temporal_score = self.detector.calculate_temporal_analysis_score(
            rating_history=rating_history,
            reviews=reviews
        )
        
        self.assertIsInstance(temporal_score, float)
        self.assertTrue(0.0 <= temporal_score <= 1.0)
        self.assertGreater(temporal_score, 0.5)  # 疑わしいパターンとして高スコア


if __name__ == "__main__":
    unittest.main()