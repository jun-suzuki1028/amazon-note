#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product dataclass拡張のテスト

TDD原則に従い、実装前にテストを定義します。
Red-Green-Refactor サイクルで進めます。
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

# これらのクラスはまだ存在しないため、TDD RED段階
# 実装予定のインポート
# from tools.models import Product, ProductReview, SakuraScore


class TestProductDataclass:
    """拡張Product dataclassのテスト (TDD RED段階)"""
    
    def test_basic_product_fields(self):
        """基本的な商品フィールドのテスト"""
        # TDD RED: Productクラスはまだ拡張されていない
        from tools.models import Product
        
        product = Product(
            asin="B08N5WRWNW",
            name="ASUS TUF Gaming VG27AQ",
            model="VG27AQ",
            brand="ASUS"
        )
        
        assert product.asin == "B08N5WRWNW"
        assert product.name == "ASUS TUF Gaming VG27AQ"
        assert product.model == "VG27AQ"
        assert product.brand == "ASUS"
    
    def test_extended_product_fields(self):
        """拡張フィールドのテスト (TDD RED段階)"""
        from tools.models import Product
        
        product = Product(
            asin="B08N5WRWNW",
            name="ASUS TUF Gaming VG27AQ",
            model="VG27AQ",
            brand="ASUS",
            price=35000,  # 新フィールド
            rating=4.5,  # 新フィールド
            reviews_count=2500,  # 新フィールド
            merchant_id="AMAZON_JP",  # 新フィールド
            sakura_score=0.2  # 新フィールド: サクラ度スコア (0.0-1.0)
        )
        
        assert product.price == 35000
        assert product.rating == 4.5
        assert product.reviews_count == 2500
        assert product.merchant_id == "AMAZON_JP"
        assert product.sakura_score == 0.2
    
    def test_optional_fields_with_defaults(self):
        """オプションフィールドのデフォルト値テスト (TDD RED段階)"""
        from tools.models import Product
        
        # 最小限のフィールドで作成
        product = Product(
            asin="B08N5WRWNW",
            name="Test Product",
            model="TEST001",
            brand="TestBrand"
        )
        
        # オプションフィールドはNoneまたはデフォルト値
        assert product.amazon_url is None
        assert product.affiliate_url is None
        assert product.price is None
        assert product.rating is None
        assert product.reviews_count == 0
        assert product.merchant_id is None
        assert product.sakura_score is None
    
    def test_product_with_urls(self):
        """URL情報を含む商品のテスト (TDD RED段階)"""
        from tools.models import Product
        
        product = Product(
            asin="B08N5WRWNW",
            name="ASUS TUF Gaming VG27AQ",
            model="VG27AQ",
            brand="ASUS",
            amazon_url="https://www.amazon.co.jp/dp/B08N5WRWNW",
            affiliate_url="https://www.amazon.co.jp/dp/B08N5WRWNW?tag=myaffiliate-22"
        )
        
        assert product.amazon_url == "https://www.amazon.co.jp/dp/B08N5WRWNW"
        assert product.affiliate_url == "https://www.amazon.co.jp/dp/B08N5WRWNW?tag=myaffiliate-22"
    
    def test_product_quality_check_method(self):
        """品質チェックメソッドのテスト (TDD RED段階)"""
        from tools.models import Product
        
        # 高品質商品
        good_product = Product(
            asin="B08N5WRWNW",
            name="High Quality Product",
            model="HQ001",
            brand="GoodBrand",
            rating=4.5,
            reviews_count=1500,
            sakura_score=0.1  # 低いサクラ度 = 良い
        )
        
        # 品質チェックメソッド
        assert good_product.is_high_quality() is True
        assert good_product.meets_quality_criteria(min_rating=4.0, min_reviews=500) is True
        
        # 低品質商品（サクラレビューの疑い）
        bad_product = Product(
            asin="B08BADITEM",
            name="Low Quality Product",
            model="LQ001",
            brand="BadBrand",
            rating=4.8,  # 高評価だが...
            reviews_count=5000,  # レビュー多いが...
            sakura_score=0.8  # 高いサクラ度 = 悪い
        )
        
        assert bad_product.is_high_quality() is False
        assert bad_product.is_suspicious() is True
    
    def test_product_to_dict_method(self):
        """辞書変換メソッドのテスト (TDD RED段階)"""
        from tools.models import Product
        
        product = Product(
            asin="B08N5WRWNW",
            name="ASUS TUF Gaming VG27AQ",
            model="VG27AQ",
            brand="ASUS",
            price=35000,
            rating=4.5,
            reviews_count=2500,
            merchant_id="AMAZON_JP",
            sakura_score=0.2
        )
        
        product_dict = product.to_dict()
        
        assert product_dict['asin'] == "B08N5WRWNW"
        assert product_dict['name'] == "ASUS TUF Gaming VG27AQ"
        assert product_dict['price'] == 35000
        assert product_dict['rating'] == 4.5
        assert product_dict['reviews_count'] == 2500
        assert product_dict['sakura_score'] == 0.2
    
    def test_product_from_api_response(self):
        """PA-API応答からの生成テスト (TDD RED段階)"""
        from tools.models import Product
        
        # PA-APIの典型的な応答構造
        api_response = {
            'ASIN': 'B08N5WRWNW',
            'ItemInfo': {
                'Title': {'DisplayValue': 'ASUS TUF Gaming VG27AQ'},
                'ByLineInfo': {'Brand': {'DisplayValue': 'ASUS'}},
                'ManufactureInfo': {'ItemPartNumber': {'DisplayValue': 'VG27AQ'}}
            },
            'CustomerReviews': {
                'StarRating': {'DisplayValue': '4.5'},
                'Count': 2500
            },
            'Offers': {
                'Listings': [{
                    'Price': {'Amount': 35000}
                }]
            }
        }
        
        # クラスメソッドでPA-API応答から生成
        product = Product.from_api_response(api_response)
        
        assert product.asin == 'B08N5WRWNW'
        assert product.name == 'ASUS TUF Gaming VG27AQ'
        assert product.brand == 'ASUS'
        assert product.model == 'VG27AQ'
        assert product.rating == 4.5
        assert product.reviews_count == 2500
        assert product.price == 35000


class TestProductReviewDataclass:
    """ProductReview dataclassのテスト (TDD RED段階)"""
    
    def test_review_basic_fields(self):
        """レビューの基本フィールドテスト"""
        from tools.models import ProductReview
        
        review = ProductReview(
            review_id="R1234567890",
            product_asin="B08N5WRWNW",
            reviewer_name="山田太郎",
            rating=5,
            title="素晴らしい製品です",
            content="このモニターは最高です。画質も良く、応答速度も速いです。",
            review_date=datetime(2024, 1, 15),
            verified_purchase=True
        )
        
        assert review.review_id == "R1234567890"
        assert review.product_asin == "B08N5WRWNW"
        assert review.reviewer_name == "山田太郎"
        assert review.rating == 5
        assert review.verified_purchase is True
    
    def test_review_suspicious_indicators(self):
        """サクラレビュー疑惑指標のテスト"""
        from tools.models import ProductReview
        
        # 疑わしいレビュー
        suspicious_review = ProductReview(
            review_id="R9999999999",
            product_asin="B08BADITEM",
            reviewer_name="レビュアー",  # 汎用的な名前
            rating=5,
            title="最高！！！",  # 短く感情的
            content="すごくいい！買って正解！みんな買うべき！",  # 具体性なし
            review_date=datetime(2024, 1, 1),
            verified_purchase=False,  # 未購入
            helpful_count=0,
            total_votes=100  # 投票多いのに役立つ票なし
        )
        
        # サクラ度チェック
        assert suspicious_review.calculate_sakura_probability() > 0.7
        assert suspicious_review.is_suspicious() is True
        
        # 信頼できるレビュー
        genuine_review = ProductReview(
            review_id="R1111111111",
            product_asin="B08N5WRWNW",
            reviewer_name="田中一郎",
            rating=4,
            title="概ね満足ですが、一部改善の余地あり",
            content="画質は期待通りで満足していますが、スタンドの調整範囲がもう少し広いと良かったです。",
            review_date=datetime(2024, 1, 10),
            verified_purchase=True,
            helpful_count=45,
            total_votes=50
        )
        
        assert genuine_review.calculate_sakura_probability() < 0.3
        assert genuine_review.is_suspicious() is False


class TestSakuraScoreDataclass:
    """SakuraScore dataclassのテスト (TDD RED段階)"""
    
    def test_sakura_score_calculation(self):
        """サクラ度スコア計算のテスト"""
        from tools.models import SakuraScore
        
        score = SakuraScore(
            product_asin="B08N5WRWNW",
            total_reviews=1000,
            suspicious_reviews=150,
            verified_purchase_ratio=0.7,
            rating_distribution=[50, 30, 100, 320, 500],  # 1-5星の分布
            review_velocity=10.5,  # 日あたりのレビュー数
            merchant_reliability=0.85
        )
        
        # 総合スコア計算
        overall_score = score.calculate_overall_score()
        assert 0.0 <= overall_score <= 1.0
        
        # 個別指標チェック
        assert score.get_suspicious_ratio() == 0.15
        assert score.is_rating_distribution_natural() is True
        assert score.is_review_velocity_suspicious() is False
    
    def test_sakura_score_thresholds(self):
        """サクラ度の閾値判定テスト"""
        from tools.models import SakuraScore
        
        # 高サクラ度商品
        high_sakura = SakuraScore(
            product_asin="B08BADITEM",
            total_reviews=5000,
            suspicious_reviews=3500,
            verified_purchase_ratio=0.2,
            rating_distribution=[10, 10, 20, 60, 4900],  # 不自然な5星集中
            review_velocity=100.0,  # 異常に高い投稿速度
            merchant_reliability=0.3
        )
        
        assert high_sakura.calculate_overall_score() > 0.7
        assert high_sakura.get_risk_level() == "HIGH"
        assert high_sakura.should_exclude() is True
        
        # 低サクラ度商品（信頼できる）
        low_sakura = SakuraScore(
            product_asin="B08GOODITEM",
            total_reviews=1500,
            suspicious_reviews=50,
            verified_purchase_ratio=0.85,
            rating_distribution=[100, 150, 300, 550, 400],  # 自然な分布
            review_velocity=2.5,  # 通常の投稿速度
            merchant_reliability=0.95
        )
        
        assert low_sakura.calculate_overall_score() < 0.3
        assert low_sakura.get_risk_level() == "LOW"
        assert low_sakura.should_exclude() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])