#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SakuraDetectorの高度な統計分析テスト - TDD GREEN継続

評価分布の偏り検出やレビュー数vs評価の相関分析など、
より高度な統計分析機能のテスト。

TDD GREEN Phase継続: 追加機能のテストと実装
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

from tools.sakura_detector import SakuraDetector
from tools.models import Product, ProductReview


class TestAdvancedSakuraDetector(unittest.TestCase):
    """SakuraDetectorの高度な統計分析機能テスト"""
    
    def setUp(self):
        """テスト前の初期設定"""
        self.detector = SakuraDetector()
    
    def test_rating_distribution_analysis(self):
        """評価分布の偏り検出テスト"""
        # 自然な評価分布（正規分布に近い）
        natural_distribution = [10, 25, 45, 65, 55]  # 1星〜5星の件数
        
        # 不自然な評価分布（5星に偏っている）
        unnatural_distribution = [5, 3, 7, 15, 170]  # 5星が85%
        
        natural_score = self.detector.calculate_distribution_bias(natural_distribution)
        unnatural_score = self.detector.calculate_distribution_bias(unnatural_distribution)
        
        self.assertLess(natural_score, 0.3)  # 自然な分布はスコアが低い
        self.assertGreater(unnatural_score, 0.7)  # 不自然な分布はスコアが高い
    
    def test_review_rating_correlation(self):
        """レビュー数と評価の相関分析テスト"""
        # 同カテゴリの商品群（自然な相関）
        normal_products = [
            Product(asin="B001", name="商品1", model="M1", brand="B1", rating=3.2, reviews_count=50),
            Product(asin="B002", name="商品2", model="M2", brand="B2", rating=3.8, reviews_count=150),
            Product(asin="B003", name="商品3", model="M3", brand="B3", rating=4.1, reviews_count=300),
            Product(asin="B004", name="商品4", model="M4", brand="B4", rating=4.3, reviews_count=450),
            Product(asin="B005", name="商品5", model="M5", brand="B5", rating=4.5, reviews_count=600),
        ]
        
        # 異常な商品（高評価なのにレビュー数が異常に多い）
        suspicious = Product(asin="B006", name="疑惑", model="S1", brand="SB", rating=4.9, reviews_count=3000)
        
        correlation_score = self.detector.analyze_correlation_anomaly(suspicious, normal_products)
        
        self.assertGreater(correlation_score, 0.7)  # 異常な相関として検出
    
    def test_review_burst_detection(self):
        """レビューバースト（短期間の大量投稿）検出テスト"""
        base_date = pd.Timestamp("2024-01-01")
        
        # バーストパターンのレビュー（3日間で50件）
        burst_reviews = []
        for i in range(50):
            burst_reviews.append(ProductReview(
                review_id=f"R{i:03d}",
                product_asin="B007",
                reviewer_name=f"User{i}",
                rating=5,
                title="Great",
                content="Amazing product",
                review_date=base_date + pd.Timedelta(days=i//17),  # 3日間に集中
                verified_purchase=True,
                helpful_count=0,
                total_votes=0
            ))
        
        burst_score = self.detector.detect_review_burst(burst_reviews)
        
        self.assertGreater(burst_score, 0.8)  # 強いバーストとして検出
    
    def test_sentiment_consistency_analysis(self):
        """レビュー感情の一貫性分析テスト"""
        # 感情が一貫していない不自然なレビュー
        inconsistent_reviews = [
            ProductReview(
                review_id="R001",
                product_asin="B008",
                reviewer_name="User1",
                rating=5,
                title="最悪",  # タイトルと評価が矛盾
                content="品質が悪い。二度と買わない。",  # 内容と評価が矛盾
                review_date=pd.Timestamp("2024-01-01"),
                verified_purchase=True,
                helpful_count=0,
                total_votes=10
            ),
            ProductReview(
                review_id="R002",
                product_asin="B008",
                reviewer_name="User2",
                rating=1,
                title="素晴らしい",  # タイトルと評価が矛盾
                content="完璧な商品です！",  # 内容と評価が矛盾
                review_date=pd.Timestamp("2024-01-02"),
                verified_purchase=False,
                helpful_count=0,
                total_votes=5
            )
        ]
        
        consistency_score = self.detector.analyze_sentiment_consistency(inconsistent_reviews)
        
        self.assertLess(consistency_score, 0.3)  # 一貫性が低いと判定
    
    def test_merchant_reliability_score(self):
        """販売者信頼度スコアのテスト"""
        # 信頼できる販売者の商品群
        reliable_products = [
            Product(asin="B101", name="商品A", model="MA", brand="Brand1", rating=4.2, reviews_count=300),
            Product(asin="B102", name="商品B", model="MB", brand="Brand1", rating=4.0, reviews_count=250),
            Product(asin="B103", name="商品C", model="MC", brand="Brand1", rating=3.9, reviews_count=200),
        ]
        
        # 疑わしい販売者の商品群（全て高評価）
        suspicious_products = [
            Product(asin="B201", name="商品X", model="MX", brand="Brand2", rating=4.9, reviews_count=1000),
            Product(asin="B202", name="商品Y", model="MY", brand="Brand2", rating=4.8, reviews_count=1200),
            Product(asin="B203", name="商品Z", model="MZ", brand="Brand2", rating=4.9, reviews_count=1500),
        ]
        
        reliable_score = self.detector.calculate_merchant_reliability("merchant1", reliable_products)
        suspicious_score = self.detector.calculate_merchant_reliability("merchant2", suspicious_products)
        
        self.assertGreater(reliable_score, 0.7)  # 信頼度が高い
        self.assertLess(suspicious_score, 0.3)  # 信頼度が低い
    
    def test_comprehensive_sakura_scoring(self):
        """総合的なサクラ度スコアリングテスト"""
        product = Product(
            asin="B300",
            name="テスト商品",
            model="TEST",
            brand="TestBrand",
            rating=4.7,
            reviews_count=800
        )
        
        # 詳細な分析データを提供
        analysis_data = {
            'distribution_bias': 0.6,
            'correlation_anomaly': 0.4,
            'review_burst': 0.3,
            'sentiment_consistency': 0.8,
            'merchant_reliability': 0.5
        }
        
        comprehensive_score = self.detector.calculate_comprehensive_score(product, analysis_data)
        
        self.assertIsInstance(comprehensive_score, float)
        self.assertTrue(0.0 <= comprehensive_score <= 1.0)
        # 複数の要因を考慮した総合スコア
        self.assertAlmostEqual(comprehensive_score, 0.40, delta=0.1)


if __name__ == "__main__":
    unittest.main()