#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SakuraDetector - サクラレビュー検出システム

統計的異常値検出とレビューパターン分析により、
Amazon商品のサクラレビューを検出するシステム。

TDD GREEN Phase: テストを通過させる最小限の実装
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
import logging
from scipy import stats

from tools.models import Product, ProductReview, SakuraScore

logger = logging.getLogger(__name__)


@dataclass
class StatisticalAnomaly:
    """統計的異常値検出結果"""
    is_anomaly: bool
    z_score_rating: float
    z_score_reviews: float
    percentile_rating: float
    percentile_reviews: float
    category_mean_rating: float
    category_mean_reviews: float
    category_std_rating: float
    category_std_reviews: float


@dataclass
class ReviewPattern:
    """レビューパターン分析結果"""
    five_star_ratio: float
    verified_purchase_ratio: float
    average_content_length: float
    generic_name_ratio: float
    helpful_ratio: float
    has_suspicious_pattern: bool
    
    def __post_init__(self):
        """疑わしいパターンの判定"""
        self.has_suspicious_pattern = (
            self.five_star_ratio > 0.8 or
            self.verified_purchase_ratio < 0.5 or
            self.average_content_length < 50 or
            self.generic_name_ratio > 0.3
        )


@dataclass
class SakuraAnalysisResult:
    """サクラ分析結果"""
    product_asin: str
    sakura_score: float
    confidence_level: float
    analysis_details: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    def is_suspicious(self, threshold: float = 0.3) -> bool:
        """サクラ疑いがあるかどうか（閾値30%）"""
        return self.sakura_score > threshold
    
    def to_report(self) -> Dict[str, Any]:
        """分析レポートを辞書形式で返す"""
        risk_level = "LOW"
        if self.sakura_score > 0.7:
            risk_level = "HIGH"
        elif self.sakura_score > 0.4:
            risk_level = "MEDIUM"
        
        recommendations = []
        if self.is_suspicious():
            recommendations.append("この商品は避けることをお勧めします")
            recommendations.append("他の信頼できる商品を検討してください")
        else:
            recommendations.append("この商品は信頼できる可能性が高いです")
        
        return {
            'product_asin': self.product_asin,
            'sakura_score': self.sakura_score,
            'risk_level': risk_level,
            'confidence_level': self.confidence_level,
            'analysis_timestamp': self.analyzed_at.isoformat(),
            'warnings': self.warnings,
            'recommendations': recommendations,
            'analysis_details': self.analysis_details
        }


class SakuraDetector:
    """サクラレビュー検出システム"""
    
    def __init__(self, anomaly_threshold: float = 0.3, min_reviews: int = 10):
        """
        初期化
        
        Args:
            anomaly_threshold: 異常値判定の閾値
            min_reviews: 分析に必要な最小レビュー数
        """
        self.anomaly_threshold = anomaly_threshold
        self.min_reviews_for_analysis = min_reviews
        logger.info(f"SakuraDetector initialized with threshold={anomaly_threshold}")
    
    def analyze_product(self, product: Product, 
                       reviews: Optional[List[ProductReview]] = None,
                       rating_history: Optional[List[Dict]] = None) -> SakuraAnalysisResult:
        """
        商品のサクラ度を総合分析（時系列分析を含む）
        
        Args:
            product: 分析対象の商品
            reviews: 商品のレビューリスト（オプション）
            rating_history: 評価履歴データ（オプション）
            
        Returns:
            SakuraAnalysisResult: 分析結果
        """
        warnings = []
        analysis_details = {}
        confidence_level = 1.0
        
        # レビュー数が少ない場合の警告
        if product.reviews_count < self.min_reviews_for_analysis:
            warnings.append("insufficient_data")
            confidence_level = 0.3
        
        # 既存のサクラスコアを優先使用
        if hasattr(product, 'sakura_score') and product.sakura_score is not None:
            sakura_score = product.sakura_score
        else:
            # 基本的なサクラ度計算
            sakura_score = self._calculate_basic_sakura_score(product)
        
        analysis_details['statistical_anomaly'] = {
            'rating': product.rating,
            'reviews_count': product.reviews_count
        }
        
        # レビューパターン分析（レビューが提供された場合、なくてもデフォルト値を設定）
        if reviews:
            pattern = self.analyze_review_pattern(reviews)
            analysis_details['review_pattern'] = pattern.__dict__
            
            # レビューパターンに基づくスコア調整
            if pattern.has_suspicious_pattern:
                sakura_score = min(sakura_score + 0.3, 1.0)
        else:
            # レビューがない場合でもreview_patternを追加
            analysis_details['review_pattern'] = {
                'five_star_ratio': 0.0,
                'verified_purchase_ratio': 0.0,
                'average_content_length': 0.0,
                'generic_name_ratio': 0.0,
                'helpful_ratio': 0.0,
                'has_suspicious_pattern': False
            }
        
        # 時系列分析（オプション機能）
        if rating_history or (reviews and len(reviews) >= 10):
            temporal_score = self.calculate_temporal_analysis_score(
                rating_history or [], reviews or []
            )
            analysis_details['temporal_analysis'] = {
                'temporal_score': temporal_score,
                'rating_surge': rating_history is not None,
                'review_burst_analysis': reviews is not None and len(reviews) >= 10,
                'periodic_pattern_analysis': reviews is not None and len(reviews) >= 20
            }
            
            # 時系列分析結果をスコアに反映（重み20%）
            sakura_score = min(sakura_score + (temporal_score * 0.2), 1.0)
        
        analysis_details['confidence_level'] = confidence_level
        
        return SakuraAnalysisResult(
            product_asin=product.asin,
            sakura_score=min(sakura_score, 1.0),
            confidence_level=confidence_level,
            analysis_details=analysis_details,
            warnings=warnings
        )
    
    def _calculate_basic_sakura_score(self, product: Product) -> float:
        """
        基本的なサクラ度スコアを計算
        
        Args:
            product: 分析対象の商品
            
        Returns:
            float: サクラ度スコア（0.0-1.0）
        """
        score = 0.0
        
        # 評価が異常に高い（4.9以上で強い疑い）
        if product.rating and product.rating >= 4.9:
            score += 0.4
        elif product.rating and product.rating >= 4.8:
            score += 0.3
            
        # レビュー数が異常に多い
        if product.reviews_count > 2000:
            score += 0.3
        elif product.reviews_count > 1500:
            score += 0.2
            
        # 評価とレビュー数の組み合わせが不自然
        if product.rating and product.rating >= 4.5 and product.reviews_count > 1000:
            score += 0.2
        
        return score
    
    def detect_rating_surge(self, rating_history: List[Dict]) -> float:
        """
        評価急上昇を検出
        
        Args:
            rating_history: 評価履歴データ [{'date', 'rating', 'review_count'}]
            
        Returns:
            float: 急上昇スコア（0.0-1.0）
        """
        if len(rating_history) < 2:
            return 0.0
        
        max_change = 0.0
        for i in range(1, len(rating_history)):
            prev_rating = rating_history[i-1]['rating']
            curr_rating = rating_history[i]['rating']
            change = curr_rating - prev_rating
            
            # 1日で1.0以上の急上昇は異常
            if change > 1.0:
                max_change = max(max_change, change)
        
        # 急上昇度をスコア化（1.5以上の変化で最大スコア）
        return min(max_change / 1.5, 1.0) if max_change > 0 else 0.0
    
    def is_rating_surge_suspicious(self, surge_score: float) -> bool:
        """
        評価急上昇が疑わしいかどうか判定
        
        Args:
            surge_score: 急上昇スコア
            
        Returns:
            bool: 疑わしい場合True
        """
        return surge_score > 0.5
    
    def analyze_temporal_burst(self, reviews: List[ProductReview]) -> float:
        """
        時系列レビューバースト分析
        
        Args:
            reviews: レビューリスト
            
        Returns:
            float: バーストスコア（0.0-1.0）
        """
        if len(reviews) < 10:
            return 0.0
        
        # 日付でグループ化
        dates = [r.review_date for r in reviews]
        date_counts = pd.Series(dates).dt.date.value_counts()
        
        if len(date_counts) < 2:
            return 0.0
        
        # 短期間（3日以内）での集中度をチェック
        total_reviews = len(reviews)
        top3_days = date_counts.nlargest(3).sum()
        concentration_ratio = top3_days / total_reviews
        
        # 3日間で70%以上集中している場合は異常
        if concentration_ratio >= 0.7:
            return 0.8
        elif concentration_ratio >= 0.5:
            return 0.6
        
        # 統計的異常値検出も並行実行
        if len(date_counts) >= 3:
            mean_reviews = date_counts.mean()
            std_reviews = date_counts.std()
            
            if std_reviews > 0:
                max_reviews_per_day = date_counts.max()
                z_score = (max_reviews_per_day - mean_reviews) / std_reviews
                
                # Z-score 3以上で高スコア
                if z_score >= 3:
                    return max(concentration_ratio, 0.7)
        
        return max(concentration_ratio * 0.5, 0.0)
    
    def detect_periodic_patterns(self, reviews: List[ProductReview]) -> float:
        """
        周期的パターンを検出
        
        Args:
            reviews: レビューリスト
            
        Returns:
            float: 周期性スコア（0.0-1.0）
        """
        if len(reviews) < 20:
            return 0.0
        
        # 曜日別の分布を分析
        weekdays = [r.review_date.weekday() for r in reviews]
        weekday_counts = pd.Series(weekdays).value_counts()
        
        # 分布の偏りを計算
        total = len(reviews)
        max_weekday_ratio = weekday_counts.max() / total
        
        # 特定の曜日に80%以上集中している場合は異常
        if max_weekday_ratio > 0.8:
            return 0.9
        elif max_weekday_ratio > 0.6:
            return 0.7
        elif max_weekday_ratio > 0.4:
            return 0.5
        
        return 0.0
    
    def is_periodic_pattern_suspicious(self, periodicity_score: float) -> bool:
        """
        周期パターンが疑わしいかどうか判定
        
        Args:
            periodicity_score: 周期性スコア
            
        Returns:
            bool: 疑わしい場合True
        """
        return periodicity_score > 0.6
    
    def calculate_temporal_analysis_score(self, rating_history: List[Dict], 
                                        reviews: List[ProductReview]) -> float:
        """
        総合的な時系列分析スコア計算（最適化版）
        
        Args:
            rating_history: 評価履歴データ
            reviews: レビューデータ
            
        Returns:
            float: 総合時系列スコア（0.0-1.0）
        """
        # 重み定義（設定変更しやすいように分離）
        WEIGHTS = {
            'rating_surge': 0.4,
            'review_burst': 0.4, 
            'periodicity': 0.2
        }
        
        weighted_scores = []
        
        # 評価急上昇分析
        if rating_history:
            surge_score = self.detect_rating_surge(rating_history)
            weighted_scores.append(surge_score * WEIGHTS['rating_surge'])
        
        # レビューパターン分析（効率化：一度にまとめて実行）
        if reviews and len(reviews) >= 10:
            burst_score = self.analyze_temporal_burst(reviews)
            weighted_scores.append(burst_score * WEIGHTS['review_burst'])
            
            # 周期性分析（レビュー数が十分な場合のみ）
            if len(reviews) >= 20:
                periodic_score = self.detect_periodic_patterns(reviews)
                weighted_scores.append(periodic_score * WEIGHTS['periodicity'])
        
        # 正規化された総合スコア
        total_weight = sum(WEIGHTS[key] for key in ['rating_surge'] if rating_history) + \
                      sum(WEIGHTS[key] for key in ['review_burst', 'periodicity'] 
                          if reviews and len(reviews) >= (10 if key == 'review_burst' else 20))
        
        if total_weight == 0:
            return 0.0
        
        return min(sum(weighted_scores) / total_weight, 1.0)
    
    def detect_statistical_anomaly(self, product: Product, 
                                  category_products: List[Product]) -> StatisticalAnomaly:
        """
        カテゴリ内での統計的異常値を検出
        
        Args:
            product: 分析対象の商品
            category_products: 同カテゴリの商品リスト
            
        Returns:
            StatisticalAnomaly: 異常値検出結果
        """
        # カテゴリ内の評価とレビュー数の統計
        ratings = [p.rating for p in category_products if p.rating is not None]
        reviews = [p.reviews_count for p in category_products]
        
        mean_rating = np.mean(ratings)
        std_rating = np.std(ratings)
        mean_reviews = np.mean(reviews)
        std_reviews = np.std(reviews)
        
        # Zスコア計算
        z_score_rating = 0.0
        z_score_reviews = 0.0
        
        if std_rating > 0 and product.rating is not None:
            z_score_rating = (product.rating - mean_rating) / std_rating
        
        if std_reviews > 0:
            z_score_reviews = (product.reviews_count - mean_reviews) / std_reviews
        
        # パーセンタイル計算
        percentile_rating = 0.0
        percentile_reviews = 0.0
        
        if product.rating is not None:
            percentile_rating = stats.percentileofscore(ratings, product.rating)
        percentile_reviews = stats.percentileofscore(reviews, product.reviews_count)
        
        # 異常値判定（正の方向に2σ以上、または両方が1.5σ以上を異常とする）
        is_anomaly = (
            z_score_rating > 2.0 or 
            z_score_reviews > 2.0 or
            (z_score_rating > 1.5 and z_score_reviews > 1.5)
        )
        
        return StatisticalAnomaly(
            is_anomaly=is_anomaly,
            z_score_rating=z_score_rating,
            z_score_reviews=z_score_reviews,
            percentile_rating=percentile_rating,
            percentile_reviews=percentile_reviews,
            category_mean_rating=mean_rating,
            category_mean_reviews=mean_reviews,
            category_std_rating=std_rating,
            category_std_reviews=std_reviews
        )
    
    def analyze_review_pattern(self, reviews: List[ProductReview]) -> ReviewPattern:
        """
        レビューパターンを分析
        
        Args:
            reviews: レビューリスト
            
        Returns:
            ReviewPattern: パターン分析結果
        """
        if not reviews:
            return ReviewPattern(
                five_star_ratio=0.0,
                verified_purchase_ratio=0.0,
                average_content_length=0.0,
                generic_name_ratio=0.0,
                helpful_ratio=0.0,
                has_suspicious_pattern=False
            )
        
        # 5つ星レビューの比率
        five_star_count = sum(1 for r in reviews if r.rating == 5)
        five_star_ratio = five_star_count / len(reviews)
        
        # 購入確認済みレビューの比率
        verified_count = sum(1 for r in reviews if r.verified_purchase)
        verified_purchase_ratio = verified_count / len(reviews)
        
        # 平均コンテンツ長
        content_lengths = [len(r.content) for r in reviews]
        average_content_length = np.mean(content_lengths)
        
        # 汎用的な名前の比率
        generic_names = ['レビュアー', 'カスタマー', '購入者', 'ユーザー']
        generic_count = sum(1 for r in reviews 
                          if any(name in r.reviewer_name for name in generic_names))
        generic_name_ratio = generic_count / len(reviews)
        
        # 役立つ票の比率
        helpful_ratios = []
        for r in reviews:
            if r.total_votes > 0:
                helpful_ratios.append(r.helpful_count / r.total_votes)
        helpful_ratio = np.mean(helpful_ratios) if helpful_ratios else 0.0
        
        return ReviewPattern(
            five_star_ratio=five_star_ratio,
            verified_purchase_ratio=verified_purchase_ratio,
            average_content_length=average_content_length,
            generic_name_ratio=generic_name_ratio,
            helpful_ratio=helpful_ratio,
            has_suspicious_pattern=False  # __post_init__で設定される
        )
    
    def calculate_review_velocity(self, reviews: List[ProductReview]) -> float:
        """
        レビュー投稿速度を計算
        
        Args:
            reviews: レビューリスト
            
        Returns:
            float: 日あたりのレビュー数
        """
        if len(reviews) < 2:
            return 0.0
        
        # レビュー日付でソート
        sorted_reviews = sorted(reviews, key=lambda r: r.review_date)
        
        # 期間を計算
        first_date = sorted_reviews[0].review_date
        last_date = sorted_reviews[-1].review_date
        days_diff = (last_date - first_date).days
        
        if days_diff == 0:
            return len(reviews)  # 同日に全レビュー
        
        return len(reviews) / days_diff
    
    def is_velocity_suspicious(self, velocity: float) -> bool:
        """
        レビュー投稿速度が疑わしいかどうか
        
        Args:
            velocity: 日あたりのレビュー数
            
        Returns:
            bool: 疑わしい場合True
        """
        return velocity > 20.0  # 日あたり20件以上は異常
    
    def batch_analyze(self, products: List[Product]) -> List[SakuraAnalysisResult]:
        """
        複数商品を効率的に一括分析
        
        Args:
            products: 商品リスト
            
        Returns:
            List[SakuraAnalysisResult]: サクラ度でソートされた分析結果リスト
        """
        if not products:
            return []
        
        # バッチ処理で効率化：商品をグループ化して処理
        results = []
        batch_size = 10  # バッチサイズを設定
        
        logger.info(f"Starting batch analysis for {len(products)} products")
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            batch_results = []
            
            for product in batch:
                try:
                    result = self.analyze_product(product)
                    batch_results.append(result)
                    logger.debug(f"Analyzed {product.asin}: sakura_score={result.sakura_score:.2f}")
                except Exception as e:
                    logger.error(f"Error analyzing product {product.asin}: {e}")
                    # エラーの場合はスキップして続行
                    continue
            
            results.extend(batch_results)
        
        # サクラ度でソート（高い順）
        results.sort(key=lambda x: x.sakura_score, reverse=True)
        
        logger.info(f"Batch analysis completed. {len(results)} products analyzed.")
        return results
    
    def is_suspicious(self, sakura_score: float, threshold: float = 0.3) -> bool:
        """
        サクラ度判定（閾値30%）
        
        Args:
            sakura_score: サクラ度スコア
            threshold: 判定閾値（デフォルト: 0.3）
            
        Returns:
            bool: 閾値を超える場合True
        """
        return sakura_score > threshold
    
    def compare_with_category(self, product: Product, category: str) -> Dict[str, Any]:
        """
        カテゴリ内での比較分析
        
        Args:
            product: 分析対象の商品
            category: カテゴリ名
            
        Returns:
            Dict[str, Any]: 比較結果
        """
        # カテゴリ内の商品を取得（実装では外部から提供される想定）
        category_products = self.get_category_products(category)
        
        if not category_products:
            return {
                'error': 'No category products found',
                'percentile_rating': 0,
                'percentile_reviews': 0,
                'deviation_score': 0
            }
        
        # 統計的異常値検出
        anomaly = self.detect_statistical_anomaly(product, category_products)
        
        # 偏差スコア計算
        deviation_score = (abs(anomaly.z_score_rating) + abs(anomaly.z_score_reviews)) / 2
        
        return {
            'percentile_rating': anomaly.percentile_rating,
            'percentile_reviews': anomaly.percentile_reviews,
            'deviation_score': deviation_score,
            'is_anomaly': anomaly.is_anomaly,
            'z_scores': {
                'rating': anomaly.z_score_rating,
                'reviews': anomaly.z_score_reviews
            }
        }
    
    def get_category_products(self, category: str) -> List[Product]:
        """
        カテゴリ内の商品を取得（モック実装）
        
        Args:
            category: カテゴリ名
            
        Returns:
            List[Product]: 商品リスト
        """
        # 実際の実装では外部APIやデータベースから取得
        # ここではテスト用の空リストを返す
        return []
    
    def calculate_distribution_bias(self, distribution: List[int]) -> float:
        """
        評価分布の偏りを計算
        
        Args:
            distribution: [1星, 2星, 3星, 4星, 5星]の件数リスト
            
        Returns:
            float: 偏りスコア（0.0-1.0、高いほど偏っている）
        """
        if not distribution or sum(distribution) == 0:
            return 0.0
        
        total = sum(distribution)
        proportions = [count / total for count in distribution]
        
        # 5星の比率が高すぎる場合
        five_star_ratio = proportions[4] if len(proportions) > 4 else 0
        
        # エントロピー計算（分布の偏りを測定）
        entropy = 0.0
        for p in proportions:
            if p > 0:
                entropy -= p * np.log2(p)
        
        # 最大エントロピー（均等分布）
        max_entropy = -np.log2(1/5)
        
        # 偏りスコア（エントロピーが低いほど偏っている）
        bias_score = 1.0 - (entropy / max_entropy) if max_entropy > 0 else 0.0
        
        # 5星が80%以上の場合は追加ペナルティ
        if five_star_ratio >= 0.8:
            bias_score = max(bias_score, 0.75)
        
        return min(bias_score, 1.0)
    
    def analyze_correlation_anomaly(self, product: Product, 
                                  category_products: List[Product]) -> float:
        """
        レビュー数と評価の相関から異常を検出
        
        Args:
            product: 分析対象の商品
            category_products: 同カテゴリの商品群
            
        Returns:
            float: 異常度スコア（0.0-1.0）
        """
        if not category_products:
            return 0.0
        
        # カテゴリ内の評価とレビュー数を取得
        ratings = [p.rating for p in category_products if p.rating is not None]
        reviews = [p.reviews_count for p in category_products]
        
        if len(ratings) < 2:
            return 0.0
        
        # 相関係数を計算
        correlation = np.corrcoef(ratings, reviews)[0, 1]
        
        # 通常、評価とレビュー数には正の相関がある
        # 高評価で異常に多いレビューは疑わしい
        if product.rating and product.rating > 4.5 and product.reviews_count > 1000:
            # 期待されるレビュー数を線形回帰で予測
            z = np.polyfit(ratings, reviews, 1)
            p = np.poly1d(z)
            expected_reviews = p(product.rating)
            
            # 実際のレビュー数が期待値を大きく上回る場合
            if product.reviews_count > expected_reviews * 2:
                return min((product.reviews_count / expected_reviews - 1) / 3, 1.0)
        
        return 0.0
    
    def detect_review_burst(self, reviews: List[ProductReview]) -> float:
        """
        レビューバースト（短期間の大量投稿）を検出
        
        Args:
            reviews: レビューリスト
            
        Returns:
            float: バーストスコア（0.0-1.0）
        """
        if len(reviews) < 10:
            return 0.0
        
        # 日付でグループ化
        dates = [r.review_date for r in reviews]
        date_counts = pd.Series(dates).value_counts()
        
        # 移動平均を計算
        if len(date_counts) > 3:
            rolling_mean = date_counts.rolling(window=3).mean()
            
            # 標準偏差の3倍を超える日があるか
            std = date_counts.std()
            mean = date_counts.mean()
            
            if std > 0:
                max_burst = (date_counts.max() - mean) / std
                if max_burst > 3:
                    return min(max_burst / 5, 1.0)
        
        # 3日間で総レビューの50%以上が投稿された場合
        sorted_dates = sorted(dates)
        for i in range(len(sorted_dates) - 2):
            three_day_window = [d for d in dates 
                               if sorted_dates[i] <= d <= sorted_dates[i] + pd.Timedelta(days=3)]
            if len(three_day_window) / len(reviews) >= 0.5:
                return 0.85
        
        return 0.0
    
    def analyze_sentiment_consistency(self, reviews: List[ProductReview]) -> float:
        """
        レビューの感情一貫性を分析
        
        Args:
            reviews: レビューリスト
            
        Returns:
            float: 一貫性スコア（0.0-1.0、高いほど一貫している）
        """
        if not reviews:
            return 1.0
        
        inconsistencies = 0
        
        for review in reviews:
            # 簡易的な感情分析（実際はより高度な分析が必要）
            positive_words = ['素晴らしい', '最高', '完璧', '良い', 'おすすめ']
            negative_words = ['最悪', '悪い', 'ダメ', '失敗', '買わない']
            
            title_positive = any(word in review.title for word in positive_words)
            title_negative = any(word in review.title for word in negative_words)
            content_positive = any(word in review.content for word in positive_words)
            content_negative = any(word in review.content for word in negative_words)
            
            # 高評価なのにネガティブな内容
            if review.rating >= 4 and (title_negative or content_negative):
                inconsistencies += 1
            
            # 低評価なのにポジティブな内容
            if review.rating <= 2 and (title_positive or content_positive):
                inconsistencies += 1
        
        consistency_score = 1.0 - (inconsistencies / len(reviews))
        return max(consistency_score, 0.0)
    
    def calculate_merchant_reliability(self, merchant_id: str, 
                                      merchant_products: List[Product]) -> float:
        """
        販売者の信頼度を計算
        
        Args:
            merchant_id: 販売者ID
            merchant_products: 販売者の商品リスト
            
        Returns:
            float: 信頼度スコア（0.0-1.0）
        """
        if not merchant_products:
            return 0.5  # デフォルト値
        
        # 全商品が異常に高評価の場合は疑わしい
        ratings = [p.rating for p in merchant_products if p.rating is not None]
        if ratings:
            avg_rating = np.mean(ratings)
            if avg_rating > 4.7:  # 平均4.7以上は異常
                return 0.2
            elif avg_rating < 3.0:  # 低すぎるのも問題
                return 0.3
        
        # 評価のばらつきがある方が自然
        if len(ratings) > 1:
            std_rating = np.std(ratings)
            if std_rating < 0.05:  # ばらつきが小さすぎる（同じ評価ばかり）
                return 0.3
            elif std_rating >= 0.1:  # 適度なばらつきがある
                return 0.8
        
        return 0.8  # 通常の信頼度
    
    def calculate_comprehensive_score(self, product: Product, 
                                     analysis_data: Dict[str, float]) -> float:
        """
        総合的なサクラ度スコアを計算
        
        Args:
            product: 商品
            analysis_data: 各種分析データ
            
        Returns:
            float: 総合サクラ度スコア（0.0-1.0）
        """
        weights = {
            'distribution_bias': 0.2,
            'correlation_anomaly': 0.2,
            'review_burst': 0.2,
            'sentiment_consistency': 0.2,  # 逆相関（一貫性が低いほどサクラ度が高い）
            'merchant_reliability': 0.2     # 逆相関（信頼度が低いほどサクラ度が高い）
        }
        
        score = 0.0
        
        for key, weight in weights.items():
            if key in analysis_data:
                value = analysis_data[key]
                
                # sentiment_consistencyとmerchant_reliabilityは逆相関
                if key == 'sentiment_consistency':
                    value = 1.0 - value
                elif key == 'merchant_reliability':
                    value = 1.0 - value
                
                score += value * weight
        
        return min(score, 1.0)