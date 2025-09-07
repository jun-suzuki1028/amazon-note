#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon PA-API 5.0クライアント実装

Product Advertising API 5.0との統合を提供するクライアントライブラリ。
設定管理、認証、エラーハンドリング、およびサクラレビュー検出のための
商品品質フィルタリング機能を含む。

TDD Refactor段階: 品質向上とコードの可読性改善
"""

import os
import yaml
import time
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from amazon_paapi import AmazonApi
from amazon_paapi.errors import AsinNotFound, TooManyRequests, AmazonError

# ロガー設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# 定数定義
DEFAULT_CONFIG_PATH = "config/settings.yaml"
DEFAULT_REGION = "us-east-1"
DEFAULT_REQUESTS_PER_DAY = 8640
DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 1.0

# PA-API制限
MAX_ITEMS_PER_REQUEST = 10
DEFAULT_MIN_REVIEWS = 500
DEFAULT_MIN_RATING = 4.0

# デフォルトリソース定義
DEFAULT_SEARCH_RESOURCES = [
    "Images.Primary.Medium",
    "ItemInfo.Title",
    "ItemInfo.Features", 
    "ItemInfo.ProductInfo",
    "Offers.Listings.Price",
    "CustomerReviews.StarRating",
    "CustomerReviews.Count"
]

DEFAULT_GET_ITEMS_RESOURCES = [
    "Images.Primary.Medium",
    "ItemInfo.Title",
    "ItemInfo.Features",
    "ItemInfo.ProductInfo", 
    "Offers.Listings.Price",
    "CustomerReviews.StarRating",
    "CustomerReviews.Count",
    "BrowseNodeInfo.BrowseNodes"
]


class PAAPIAuthenticationError(Exception):
    """PA-API認証関連のエラー。

    アクセスキー、シークレットキー、またはアソシエイトタグが
    適切に設定されていない場合に発生。
    """
    pass


class PAAPIConfigError(Exception):
    """PA-API設定関連のエラー。

    設定ファイルの読み込みエラー、必須フィールドの欠落、
    または設定値の形式エラー時に発生。
    """
    pass


class PAAPIRateLimitError(Exception):
    """PA-APIレート制限エラー。

    1日のAPIリクエスト制限に達した場合に発生。
    """
    pass


class PAAPINetworkError(Exception):
    """PA-APIネットワークエラー。

    API通信時のネットワーク問題や接続タイムアウト時に発生。
    """
    pass


@dataclass
class PAAPIConfig:
    """PA-API設定情報を格納するデータクラス。

    Amazon Product Advertising API 5.0の接続に必要な認証情報と
    設定パラメータを管理。
    
    Attributes:
        access_key: AWSアクセスキー
        secret_key: AWSシークレットアクセスキー  
        associate_tag: Amazonアソシエイトタグ
        region: APIエンドポイントのリージョン
        requests_per_day: 1日あたりのAPI呼び出し制限
        timeout_seconds: リクエストタイムアウト時間（秒）
        retry_attempts: リトライ回数
        retry_delay: リトライ間隔（秒）
    """
    access_key: str
    secret_key: str
    associate_tag: str
    region: str = DEFAULT_REGION
    requests_per_day: int = DEFAULT_REQUESTS_PER_DAY
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS
    retry_delay: float = DEFAULT_RETRY_DELAY


class PAAPIClient:
    """Amazon Product Advertising API 5.0との通信を管理するクライアント。

    設定ファイルの読み込み、環境変数の処理、認証情報の管理を行い、
    PA-APIへのリクエスト送信に必要な基盤を提供。

    Attributes:
        config: PA-API設定情報
    """
    
    def __init__(self, config_path: Optional[Path] = None) -> None:
        """PA-APIクライアントを初期化。
        
        Args:
            config_path: 設定ファイルのパス。Noneの場合は自動検索。
            
        Raises:
            PAAPIConfigError: 設定ファイルが見つからないかpa_api設定がない場合
            PAAPIAuthenticationError: 認証情報が不正または不足している場合
        """
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[Path] = None) -> PAAPIConfig:
        """設定情報を読み込んでPAAPIConfigインスタンスを作成。
        
        Args:
            config_path: 設定ファイルパス。Noneの場合は自動検索。
            
        Returns:
            設定情報を含むPAAPIConfigインスタンス
            
        Raises:
            PAAPIConfigError: 設定ファイルの問題または必須設定の欠落
            PAAPIAuthenticationError: 認証情報が不足または不正
        """
        resolved_path = self._resolve_config_path(config_path)
        settings = self._load_settings_file(resolved_path)
        pa_api_config = self._extract_pa_api_config(settings)
        
        return self._create_config_from_settings(pa_api_config)
    
    def _resolve_config_path(self, config_path: Optional[Path]) -> Path:
        """設定ファイルのパスを解決。"""
        if config_path is not None:
            if not config_path.exists():
                raise PAAPIConfigError(f"設定ファイル {DEFAULT_CONFIG_PATH} が見つかりません")
            return config_path
        
        # プロジェクトルートを探索
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            config_file = current_dir / DEFAULT_CONFIG_PATH
            if config_file.exists():
                return config_file
            current_dir = current_dir.parent
        
        raise PAAPIConfigError(f"設定ファイル {DEFAULT_CONFIG_PATH} が見つかりません")
    
    def _load_settings_file(self, config_path: Path) -> Dict[str, Any]:
        """YAML設定ファイルを読み込み。"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise PAAPIConfigError(f"設定ファイル読み込みエラー: {e}")
    
    def _extract_pa_api_config(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """設定からPA-API関連の設定を抽出。"""
        pa_api_config = settings.get('pa_api', {})
        if not pa_api_config:
            raise PAAPIConfigError("設定ファイルにpa_api設定が見つかりません")
        return pa_api_config
    
    def _create_config_from_settings(self, pa_api_config: Dict[str, Any]) -> PAAPIConfig:
        """PA-API設定辞書からPAAPIConfigインスタンスを作成。"""
        # 認証情報の取得（環境変数優先）
        access_key = os.environ.get('AWS_ACCESS_KEY_ID', 
                                  pa_api_config.get('access_key', ''))
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', 
                                  pa_api_config.get('secret_key', ''))
        
        # 認証情報の検証
        self._validate_auth_credentials(access_key, secret_key)
        
        # associate_tagの検証
        associate_tag = pa_api_config.get('associate_tag')
        if not associate_tag:
            raise PAAPIConfigError("associate_tagが設定されていません")
        
        return PAAPIConfig(
            access_key=access_key,
            secret_key=secret_key,
            associate_tag=associate_tag,
            region=pa_api_config.get('region', DEFAULT_REGION),
            requests_per_day=pa_api_config.get('requests_per_day', DEFAULT_REQUESTS_PER_DAY),
            timeout_seconds=pa_api_config.get('timeout_seconds', DEFAULT_TIMEOUT_SECONDS),
            retry_attempts=pa_api_config.get('retry_attempts', DEFAULT_RETRY_ATTEMPTS),
            retry_delay=pa_api_config.get('retry_delay', DEFAULT_RETRY_DELAY)
        )
    
    def _validate_auth_credentials(self, access_key: str, secret_key: str) -> None:
        """認証情報の妥当性を検証。"""
        if not access_key:
            raise PAAPIAuthenticationError(
                "access_keyが設定されていません"
            )
        if not secret_key:
            raise PAAPIAuthenticationError(
                "secret_keyが設定されていません"
            )
    
    def _create_paapi_client(self) -> AmazonApi:
        """PA-API AmazonApiクライアントを作成。
        
        Returns:
            設定済みのAmazonApi PA-APIクライアント
            
        Raises:
            PAAPINetworkError: クライアント作成に失敗した場合
        """
        try:
            # 国別設定を地域から決定
            country_mapping = {
                'us-east-1': 'US',
                'eu-west-1': 'UK', 
                'ap-northeast-1': 'JP'
            }
            country = country_mapping.get(self.config.region, 'US')
            
            return AmazonApi(
                key=self.config.access_key,
                secret=self.config.secret_key,
                tag=self.config.associate_tag,
                country=country
            )
        except Exception as e:
            raise PAAPINetworkError(f"PA-APIクライアント作成エラー: {e}")
    
    def _handle_rate_limit(self, attempt: int) -> None:
        """レート制限処理。"""
        if attempt > 0:
            delay = self.config.retry_delay * (2 ** (attempt - 1))  # 指数バックオフ
            time.sleep(delay)
    
    def _parse_api_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """API応答を解析して結果を返す。
        
        部分的な失敗（一部のASINが見つからない等）の場合は、
        成功した部分だけを返し、完全な失敗の場合のみ例外を発生させる。
        """
        # エラーがある場合の処理
        if 'Errors' in response:
            errors = response['Errors']
            
            # 部分的失敗の場合（成功したアイテムもある）
            if 'ItemsResult' in response and response.get('ItemsResult', {}).get('Items'):
                # ItemNotFoundのようなエラーは警告としてログに記録するが、例外は発生させない
                # 成功したアイテムを含むレスポンスを返す
                return response
            
            # 完全な失敗の場合（成功したアイテムがない）
            error_msg = ", ".join([f"{err.get('Code', 'Unknown')}: {err.get('Message', 'Unknown error')}" for err in errors])
            if any(err.get('Code') == 'RequestThrottled' for err in errors):
                raise PAAPIRateLimitError(f"レート制限エラー: {error_msg}")
            else:
                raise PAAPINetworkError(f"API エラー: {error_msg}")
        
        return response
    
    def _execute_with_retry(self, operation_name: str, **kwargs) -> Dict[str, Any]:
        """リトライ機能付きでPA-API操作を実行。
        
        Args:
            operation_name: 操作名（'search'、'get_items'）
            **kwargs: API操作に渡すパラメータ
            
        Returns:
            API応答辞書
            
        Raises:
            PAAPIRateLimitError: レート制限に達した場合
            PAAPINetworkError: 通信エラーまたはAPIエラー
        """
        client = self._create_paapi_client()
        operation_method = getattr(client, operation_name)
        
        last_error = None
        for attempt in range(self.config.retry_attempts):
            try:
                self._handle_rate_limit(attempt)
                
                response = operation_method(**kwargs)
                return response  # 新しいSDKは直接辞書を返す
                
            except AsinNotFound as e:
                # ASIN見つからない場合は空の結果を返す
                return {"data": {"ItemsResult": {"Items": []}}}
            except TooManyRequests as e:
                # レート制限の場合
                logger.warning(f"PA-APIレート制限: {e}")
                last_error = PAAPIRateLimitError(f"レート制限エラー: {e}")
                if attempt == self.config.retry_attempts - 1:
                    raise last_error
                continue
            except AmazonError as e:
                # Amazon関連エラー
                logger.error(f"PA-APIエラー: {e}")
                last_error = PAAPINetworkError(f"API エラー: {e}")
                if attempt == self.config.retry_attempts - 1:
                    raise last_error
                continue
            except Exception as e:
                # その他の例外処理
                last_error = PAAPINetworkError(f"予期しないエラー: {e}")
                if attempt == self.config.retry_attempts - 1:
                    raise last_error
                continue
        
        # ここに到達することはないはずだが、安全のため
        if last_error:
            raise last_error
        raise PAAPINetworkError("未知のエラーが発生しました")
    
    def search_items(self, keywords: str, search_index: str = "All", 
                    item_count: int = MAX_ITEMS_PER_REQUEST, item_page: int = 1, 
                    resources: Optional[List[str]] = None) -> Dict[str, Any]:
        """製品検索を実行。
        
        Args:
            keywords: 検索キーワード
            search_index: 検索カテゴリ（All, Electronics, Books等）
            item_count: 取得件数（最大10件）
            item_page: ページ番号（1から開始）
            resources: 取得するリソース項目
            
        Returns:
            検索結果の辞書
            
        Raises:
            PAAPIRateLimitError: レート制限に達した場合
            PAAPINetworkError: 通信エラーまたはAPIエラー
        """
        if resources is None:
            resources = DEFAULT_SEARCH_RESOURCES
        
        # 新しいSDKに合わせたパラメータ
        search_params = {
            "keywords": keywords,
            "search_index": search_index,
            "item_count": min(item_count, MAX_ITEMS_PER_REQUEST),
            "item_page": item_page
        }
        
        return self._execute_with_retry("search_items", **search_params)
    
    def get_items(self, asins: List[str], 
                 resources: Optional[List[str]] = None) -> Dict[str, Any]:
        """ASIN指定で製品詳細を取得。
        
        Args:
            asins: ASINのリスト（最大10件）
            resources: 取得するリソース項目
            
        Returns:
            製品詳細の辞書
            
        Raises:
            ValueError: ASINが不正または範囲外の場合
            PAAPIRateLimitError: レート制限に達した場合
            PAAPINetworkError: 通信エラーまたはAPIエラー
        """
        if not asins:
            raise ValueError("ASINが指定されていません")
        
        if len(asins) > MAX_ITEMS_PER_REQUEST:
            raise ValueError(f"ASINは最大{MAX_ITEMS_PER_REQUEST}件まで指定可能です")
        
        if resources is None:
            resources = DEFAULT_GET_ITEMS_RESOURCES
        
        # 新しいSDKに合わせたパラメータ
        get_items_params = {
            "items": asins
        }
        
        return self._execute_with_retry("get_items", **get_items_params)
    
    def _extract_product_data(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """PA-API商品アイテムから標準化されたデータを抽出。
        
        Args:
            item: PA-APIから返される商品アイテム辞書
            
        Returns:
            標準化された商品データ、またはデータが不正な場合はNone
        """
        try:
            # 必須データの取得
            asin = item.get('ASIN')
            if not asin:
                return None
            
            # タイトル
            title_info = item.get('ItemInfo', {}).get('Title', {})
            title = title_info.get('DisplayValue', 'Unknown')
            
            # レビュー情報
            customer_reviews = item.get('CustomerReviews', {})
            
            # 評価値の取得と変換
            star_rating = customer_reviews.get('StarRating', {})
            rating_str = star_rating.get('DisplayValue', '0')
            try:
                rating = float(rating_str)
            except (ValueError, TypeError):
                rating = 0.0
            
            # レビュー数の取得
            review_count = customer_reviews.get('Count', 0)
            if isinstance(review_count, dict):
                review_count = review_count.get('DisplayValue', 0)
            try:
                review_count = int(review_count)
            except (ValueError, TypeError):
                review_count = 0
            
            # 価格情報（オプション）
            price = None
            price_display = None
            offers = item.get('Offers', {}).get('Listings', [])
            if offers and len(offers) > 0:
                price_info = offers[0].get('Price', {})
                if 'Amount' in price_info:
                    price = price_info['Amount']
                if 'DisplayAmount' in price_info:
                    price_display = price_info['DisplayAmount']
            
            return {
                'asin': asin,
                'title': title,
                'rating': rating,
                'review_count': review_count,
                'price': price,
                'price_display': price_display,
                'raw_data': item
            }
            
        except Exception:
            # データ処理エラーの場合はNoneを返す
            return None
    
    def _extract_detailed_product_data(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """PA-API商品アイテムから詳細なデータを抽出（記事作成用）。
        
        Args:
            item: PA-APIから返される商品アイテム辞書
            
        Returns:
            詳細な商品データ、またはデータが不正な場合はNone
        """
        try:
            # 必須データの取得
            asin = item.get('ASIN')
            if not asin:
                return None
            
            item_info = item.get('ItemInfo', {})
            
            # タイトル
            title_info = item_info.get('Title', {})
            title = title_info.get('DisplayValue', 'Unknown')
            
            # ブランド情報
            brand_info = item_info.get('ByLineInfo', {}).get('Brand', {})
            brand = brand_info.get('DisplayValue', 'Unknown')
            
            # 型番・製品番号
            manufacture_info = item_info.get('ManufactureInfo', {})
            part_number_info = manufacture_info.get('ItemPartNumber', {})
            part_number = part_number_info.get('DisplayValue', 'Unknown')
            
            # レビュー情報
            customer_reviews = item.get('CustomerReviews', {})
            
            # 評価値の取得と変換
            star_rating = customer_reviews.get('StarRating', {})
            rating_str = star_rating.get('DisplayValue', '0')
            try:
                rating = float(rating_str)
            except (ValueError, TypeError):
                rating = 0.0
            
            # レビュー数の取得
            review_count = customer_reviews.get('Count', 0)
            if isinstance(review_count, dict):
                review_count = review_count.get('DisplayValue', 0)
            try:
                review_count = int(review_count)
            except (ValueError, TypeError):
                review_count = 0
            
            # 価格情報
            price = None
            price_display = None
            offers = item.get('Offers', {}).get('Listings', [])
            if offers and len(offers) > 0:
                price_info = offers[0].get('Price', {})
                if 'Amount' in price_info:
                    price = price_info['Amount']
                if 'DisplayAmount' in price_info:
                    price_display = price_info['DisplayAmount']
            
            # 画像URL
            image_url = None
            images = item.get('Images', {}).get('Primary', {}).get('Medium', {})
            if 'URL' in images:
                image_url = images['URL']
            
            return {
                'asin': asin,
                'title': title,
                'brand': brand,
                'part_number': part_number,
                'rating': rating,
                'review_count': review_count,
                'price': price,
                'price_display': price_display,
                'image_url': image_url,
                'raw_data': item
            }
            
        except Exception:
            # データ処理エラーの場合はNoneを返す
            return None
    
    def search_products(self, keywords: str, min_reviews: int = DEFAULT_MIN_REVIEWS, 
                       min_rating: float = DEFAULT_MIN_RATING, search_index: str = "All",
                       max_results: int = MAX_ITEMS_PER_REQUEST) -> List[Dict[str, Any]]:
        """品質基準を満たす商品を検索（サクラレビュー対策用フィルタリング付き）。
        
        Args:
            keywords: 検索キーワード
            min_reviews: 最小レビュー数（サクラ対策）
            min_rating: 最小評価値（品質保証）
            search_index: 検索カテゴリ
            max_results: 最大結果数
            
        Returns:
            品質基準を満たす商品のリスト
            
        Raises:
            PAAPIRateLimitError: レート制限に達した場合
            PAAPINetworkError: 通信エラーまたはAPIエラー
        """
        logger.info(f"商品検索開始: keywords='{keywords}', min_reviews={min_reviews}, min_rating={min_rating}")
        
        # PA-API SearchItemsを呼び出し
        response = self.search_items(
            keywords=keywords,
            search_index=search_index,
            item_count=max_results,
            resources=[
                "Images.Primary.Medium",
                "ItemInfo.Title",
                "ItemInfo.Features", 
                "ItemInfo.ProductInfo",
                "Offers.Listings.Price",
                "CustomerReviews.StarRating",
                "CustomerReviews.Count"
            ]
        )
        
        # 応答から商品リストを抽出（新しいSDK形式）
        items = response.get('data', {}).get('SearchResult', {}).get('Items', [])
        
        # 品質基準でフィルタリング
        filtered_products = []
        
        for item in items:
            try:
                # 必須データの取得
                asin = item.get('ASIN')
                if not asin:
                    continue
                
                # タイトル
                title_info = item.get('ItemInfo', {}).get('Title', {})
                title = title_info.get('DisplayValue', 'Unknown')
                
                # レビュー情報
                customer_reviews = item.get('CustomerReviews', {})
                
                # 評価値の取得と変換
                star_rating = customer_reviews.get('StarRating', {})
                rating_str = star_rating.get('DisplayValue', '0')
                try:
                    rating = float(rating_str)
                except (ValueError, TypeError):
                    rating = 0.0
                
                # レビュー数の取得
                review_count = customer_reviews.get('Count', 0)
                if isinstance(review_count, dict):
                    review_count = review_count.get('DisplayValue', 0)
                try:
                    review_count = int(review_count)
                except (ValueError, TypeError):
                    review_count = 0
                
                # 品質基準チェック（サクラレビュー対策）
                if review_count >= min_reviews and rating >= min_rating:
                    logger.debug(f"品質基準通過: ASIN={asin}, reviews={review_count}, rating={rating}")
                    # 価格情報（オプション）
                    price = None
                    offers = item.get('Offers', {}).get('Listings', [])
                    if offers and len(offers) > 0:
                        price_info = offers[0].get('Price', {})
                        if 'Amount' in price_info:
                            price = price_info['Amount']
                    
                    # フィルタリング通過した商品を追加
                    product = {
                        'asin': asin,
                        'title': title,
                        'rating': rating,
                        'review_count': review_count,
                        'price': price,
                        'raw_data': item  # 生データも保持
                    }
                    filtered_products.append(product)
                    
            except Exception as e:
                # 個別の商品データ処理エラーはログに記録してスキップ
                logger.warning(f"商品データ処理エラー (ASIN={item.get('ASIN', 'Unknown')}): {e}")
                continue
        
        logger.info(f"検索完了: {len(filtered_products)}件の商品が品質基準を満たしました")
        return filtered_products    
    def get_product_details(self, asin: str) -> Optional[Dict[str, Any]]:
        """単一ASINの商品詳細情報を取得。
        
        Args:
            asin: 取得したい商品のASIN
            
        Returns:
            商品詳細情報の辞書、または商品が見つからない場合はNone
            
        Raises:
            PAAPIRateLimitError: レート制限に達した場合
            PAAPINetworkError: 通信エラーまたはAPIエラー
        """
        response = self.get_items(
            asins=[asin],
            resources=DEFAULT_GET_ITEMS_RESOURCES
        )
        
        # 応答から商品データを抽出（新しいSDK形式）
        items = response.get('data', {}).get('ItemsResult', {}).get('Items', [])
        
        if not items:
            return None
        
        return self._extract_detailed_product_data(items[0])
    
    def batch_lookup(self, asins: List[str]) -> List[Dict[str, Any]]:
        """複数ASINの商品詳細を一括取得。
        
        Args:
            asins: 取得したい商品のASINリスト（最大10件）
            
        Returns:
            商品詳細情報のリスト
            
        Raises:
            ValueError: ASINが不正または範囲外の場合
            PAAPIRateLimitError: レート制限に達した場合
            PAAPINetworkError: 通信エラーまたはAPIエラー
        """
        if not asins:
            return []
        
        if len(asins) > MAX_ITEMS_PER_REQUEST:
            raise ValueError(f"ASINは最大{MAX_ITEMS_PER_REQUEST}件まで指定可能です")
        
        response = self.get_items(
            asins=asins,
            resources=DEFAULT_GET_ITEMS_RESOURCES
        )
        
        # 応答から商品リストを抽出（新しいSDK形式）
        items = response.get('data', {}).get('ItemsResult', {}).get('Items', [])
        
        # 詳細データに変換
        detailed_products = []
        for item in items:
            product = self._extract_detailed_product_data(item)
            if product:
                detailed_products.append(product)
        
        return detailed_products
