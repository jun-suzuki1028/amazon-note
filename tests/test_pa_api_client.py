#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PA-APIクライアントのテスト

TDD原則に従い、実装前にテストを定義します。
Red-Green-Refactor サイクルで進めます。
"""

import os
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError, BotoCoreError

# 実装済みのクラスをインポート（TDD Green段階）
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.pa_api_client import (
    PAAPIClient, 
    PAAPIConfig,
    PAAPIAuthenticationError,
    PAAPIConfigError,
    PAAPIRateLimitError,
    PAAPINetworkError
)


class TestPAAPIConfig:
    """PAAPIConfig データクラスのテスト"""
    
    def test_config_creation_with_required_fields(self):
        """必須フィールドでの設定作成テスト"""
        # TDD Red: まだPAAPIConfigが存在しない
        config = PAAPIConfig(
            access_key="test_access_key",
            secret_key="test_secret_key", 
            associate_tag="test_tag"
        )
        assert config.access_key == "test_access_key"
        assert config.secret_key == "test_secret_key"
        assert config.associate_tag == "test_tag"
        assert config.region == "us-east-1"  # デフォルト値
        assert config.requests_per_day == 8640  # デフォルト値
    
    def test_config_creation_with_custom_values(self):
        """カスタム値での設定作成テスト"""
        config = PAAPIConfig(
            access_key="custom_access",
            secret_key="custom_secret",
            associate_tag="custom_tag",
            region="eu-west-1",
            requests_per_day=1000,
            timeout_seconds=20
        )
        assert config.region == "eu-west-1"
        assert config.requests_per_day == 1000
        assert config.timeout_seconds == 20


class TestPAAPIClient:
    """PAAPIClient クラスのテスト"""
    
    def setup_method(self):
        """テスト前の準備"""
        # テスト用の一時設定ファイルを作成
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir()
        self.settings_file = self.config_dir / "settings.yaml"
        
        # テスト用設定データ
        self.test_settings = {
            'pa_api': {
                'access_key': 'test_file_access_key',
                'secret_key': 'test_file_secret_key',
                'associate_tag': 'test_associate_tag',
                'region': 'us-east-1',
                'requests_per_day': 8640,
                'timeout_seconds': 10,
                'retry_attempts': 3,
                'retry_delay': 1.0
            }
        }
        
        with open(self.settings_file, 'w') as f:
            yaml.dump(self.test_settings, f)
    
    def test_config_loading_from_file(self):
        """設定ファイルからの設定読み込みテスト"""
        # TDD Red: PAAPIClientがまだ存在しない
        client = PAAPIClient(config_path=self.settings_file)
        
        assert client.config.access_key == 'test_file_access_key'
        assert client.config.secret_key == 'test_file_secret_key'
        assert client.config.associate_tag == 'test_associate_tag'
        assert client.config.region == 'us-east-1'
    
    @patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'env_access_key',
        'AWS_SECRET_ACCESS_KEY': 'env_secret_key'
    })
    def test_config_loading_env_vars_override(self):
        """環境変数が設定ファイルをオーバーライドするテスト"""
        client = PAAPIClient(config_path=self.settings_file)
        
        # 環境変数が優先される
        assert client.config.access_key == 'env_access_key'
        assert client.config.secret_key == 'env_secret_key'
        # その他は設定ファイルから
        assert client.config.associate_tag == 'test_associate_tag'
    
    def test_config_error_missing_file(self):
        """設定ファイル不在時のエラー"""
        non_existent_path = Path("/non/existent/path/settings.yaml")
        
        with pytest.raises(PAAPIConfigError, match="設定ファイル.*が見つかりません"):
            PAAPIClient(config_path=non_existent_path)
    
    def test_config_error_missing_pa_api_section(self):
        """pa_api設定セクション不在時のエラー"""
        # pa_api セクションなしの設定ファイル
        bad_settings = {'other_section': {}}
        bad_settings_file = self.config_dir / "bad_settings.yaml"
        
        with open(bad_settings_file, 'w') as f:
            yaml.dump(bad_settings, f)
        
        with pytest.raises(PAAPIConfigError, match="pa_api設定が見つかりません"):
            PAAPIClient(config_path=bad_settings_file)
    
    def test_authentication_error_missing_access_key(self):
        """access_key不在時の認証エラー"""
        bad_settings = {
            'pa_api': {
                # access_keyがない
                'secret_key': 'test_secret',
                'associate_tag': 'test_tag'
            }
        }
        bad_settings_file = self.config_dir / "no_access_key.yaml"
        
        with open(bad_settings_file, 'w') as f:
            yaml.dump(bad_settings, f)
        
        with pytest.raises(PAAPIAuthenticationError, match="access_keyが設定されていません"):
            PAAPIClient(config_path=bad_settings_file)
    
    def test_authentication_error_missing_secret_key(self):
        """secret_key不在時の認証エラー"""
        bad_settings = {
            'pa_api': {
                'access_key': 'test_access',
                # secret_keyがない
                'associate_tag': 'test_tag'
            }
        }
        bad_settings_file = self.config_dir / "no_secret_key.yaml" 
        
        with open(bad_settings_file, 'w') as f:
            yaml.dump(bad_settings, f)
        
        with pytest.raises(PAAPIAuthenticationError, match="secret_keyが設定されていません"):
            PAAPIClient(config_path=bad_settings_file)
    
    def test_config_error_missing_associate_tag(self):
        """associate_tag不在時の設定エラー"""
        bad_settings = {
            'pa_api': {
                'access_key': 'test_access',
                'secret_key': 'test_secret'
                # associate_tagがない
            }
        }
        bad_settings_file = self.config_dir / "no_associate_tag.yaml"
        
        with open(bad_settings_file, 'w') as f:
            yaml.dump(bad_settings, f)
        
        with pytest.raises(PAAPIConfigError, match="associate_tagが設定されていません"):
            PAAPIClient(config_path=bad_settings_file)


class TestProductSearch:
    """商品検索機能のテスト（TDD Red段階）"""
    
    def setup_method(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir()
        self.settings_file = self.config_dir / "settings.yaml"
        
        # テスト用設定データ（品質基準を含む）
        self.test_settings = {
            'pa_api': {
                'access_key': 'test_access_key',
                'secret_key': 'test_secret_key',
                'associate_tag': 'test_tag',
                'region': 'us-east-1'
            },
            'product_criteria': {
                'min_reviews': 500,
                'min_rating': 4.0,
                'sakura_check': True,
                'exclude_chinese': True
            }
        }
        
        with open(self.settings_file, 'w') as f:
            yaml.dump(self.test_settings, f)
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_search_products_basic_functionality(self, mock_client):
        """基本的な商品検索機能テスト（TDD Red段階）"""
        # モックした検索応答データ
        mock_response = {
            'SearchResult': {
                'Items': [
                    {
                        'ASIN': 'B08N5WRWNW',
                        'ItemInfo': {
                            'Title': {'DisplayValue': 'Test Gaming Monitor'},
                        },
                        'CustomerReviews': {
                            'StarRating': {'DisplayValue': '4.5'},
                            'Count': 1500
                        },
                        'Offers': {
                            'Listings': [{'Price': {'Amount': 25000}}]
                        }
                    }
                ]
            }
        }
        
        # boto3クライアントのモック設定
        mock_client_instance = MagicMock()
        mock_client_instance.search_items.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        # TDD Red: この時点でsearch_products()メソッドは存在しない
        client = PAAPIClient(config_path=self.settings_file)
        
        # 品質基準を満たす商品の検索
        results = client.search_products(
            keywords="gaming monitor",
            min_reviews=500,
            min_rating=4.0
        )
        
        # 期待される結果の検証
        assert len(results) == 1
        assert results[0]['asin'] == 'B08N5WRWNW'
        assert results[0]['title'] == 'Test Gaming Monitor'
        assert results[0]['rating'] == 4.5
        assert results[0]['review_count'] == 1500
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_search_products_quality_filtering(self, mock_client):
        """品質基準でのフィルタリングテスト（TDD Red段階）"""
        # 品質基準を満たさない商品を含むモック応答
        mock_response = {
            'SearchResult': {
                'Items': [
                    # 品質基準を満たす商品
                    {
                        'ASIN': 'B08N5WRWNW',
                        'ItemInfo': {'Title': {'DisplayValue': 'High Quality Monitor'}},
                        'CustomerReviews': {
                            'StarRating': {'DisplayValue': '4.5'},
                            'Count': 1500
                        }
                    },
                    # レビュー数不足
                    {
                        'ASIN': 'B08BADITEM1',
                        'ItemInfo': {'Title': {'DisplayValue': 'Low Review Monitor'}},
                        'CustomerReviews': {
                            'StarRating': {'DisplayValue': '4.5'},
                            'Count': 100
                        }
                    },
                    # 評価不足
                    {
                        'ASIN': 'B08BADITEM2',
                        'ItemInfo': {'Title': {'DisplayValue': 'Low Rating Monitor'}},
                        'CustomerReviews': {
                            'StarRating': {'DisplayValue': '3.5'},
                            'Count': 1500
                        }
                    }
                ]
            }
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.search_items.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        client = PAAPIClient(config_path=self.settings_file)
        
        # 品質基準でフィルタリングされて、1件のみが返される
        results = client.search_products(
            keywords="monitor",
            min_reviews=500,
            min_rating=4.0
        )
        
        assert len(results) == 1
        assert results[0]['asin'] == 'B08N5WRWNW'
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_search_products_empty_results(self, mock_client):
        """検索結果なしのテスト（TDD Red段階）"""
        mock_response = {
            'SearchResult': {
                'Items': []
            }
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.search_items.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        client = PAAPIClient(config_path=self.settings_file)
        
        results = client.search_products(
            keywords="nonexistent product",
            min_reviews=500,
            min_rating=4.0
        )
        
        assert results == []


class TestProductDetails:
    """商品詳細取得機能のテスト（TDD Red段階）"""
    
    def setup_method(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir()
        self.settings_file = self.config_dir / "settings.yaml"
        
        # テスト用設定データ
        self.test_settings = {
            'pa_api': {
                'access_key': 'test_access_key',
                'secret_key': 'test_secret_key',
                'associate_tag': 'test_tag',
                'region': 'us-east-1'
            }
        }
        
        with open(self.settings_file, 'w') as f:
            yaml.dump(self.test_settings, f)
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_get_product_details_single_asin(self, mock_client):
        """単一ASINの商品詳細取得テスト（TDD Red段階）"""
        # モックした商品詳細データ
        mock_response = {
            'ItemsResult': {
                'Items': [
                    {
                        'ASIN': 'B08N5WRWNW',
                        'ItemInfo': {
                            'Title': {'DisplayValue': 'ASUS TUF Gaming Monitor'},
                            'ByLineInfo': {
                                'Brand': {'DisplayValue': 'ASUS'}
                            },
                            'ManufactureInfo': {
                                'ItemPartNumber': {'DisplayValue': 'VG27AQ'}
                            }
                        },
                        'CustomerReviews': {
                            'StarRating': {'DisplayValue': '4.5'},
                            'Count': 2500
                        },
                        'Offers': {
                            'Listings': [{
                                'Price': {'Amount': 35000, 'DisplayAmount': '￥35,000'}
                            }]
                        },
                        'Images': {
                            'Primary': {
                                'Medium': {'URL': 'https://example.com/image.jpg'}
                            }
                        }
                    }
                ]
            }
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.get_items.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        # TDD Red: この時点でget_product_details()メソッドは存在しない
        client = PAAPIClient(config_path=self.settings_file)
        
        # 商品詳細取得
        details = client.get_product_details('B08N5WRWNW')
        
        # 期待される結果の検証
        assert details is not None
        assert details['asin'] == 'B08N5WRWNW'
        assert details['title'] == 'ASUS TUF Gaming Monitor'
        assert details['brand'] == 'ASUS'
        assert details['part_number'] == 'VG27AQ'
        assert details['rating'] == 4.5
        assert details['review_count'] == 2500
        assert details['price'] == 35000
        assert details['price_display'] == '￥35,000'
        assert details['image_url'] == 'https://example.com/image.jpg'
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_batch_lookup_multiple_asins(self, mock_client):
        """複数ASINの一括取得テスト（TDD Red段階）"""
        # 複数商品のモックデータ
        mock_response = {
            'ItemsResult': {
                'Items': [
                    {
                        'ASIN': 'B08N5WRWNW',
                        'ItemInfo': {
                            'Title': {'DisplayValue': 'Monitor 1'},
                            'ByLineInfo': {'Brand': {'DisplayValue': 'Brand1'}}
                        },
                        'CustomerReviews': {
                            'StarRating': {'DisplayValue': '4.5'},
                            'Count': 1500
                        }
                    },
                    {
                        'ASIN': 'B08EXAMPLE',
                        'ItemInfo': {
                            'Title': {'DisplayValue': 'Monitor 2'},
                            'ByLineInfo': {'Brand': {'DisplayValue': 'Brand2'}}
                        },
                        'CustomerReviews': {
                            'StarRating': {'DisplayValue': '4.2'},
                            'Count': 800
                        }
                    }
                ]
            }
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.get_items.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        # TDD Red: この時点でbatch_lookup()メソッドは存在しない
        client = PAAPIClient(config_path=self.settings_file)
        
        asins = ['B08N5WRWNW', 'B08EXAMPLE']
        results = client.batch_lookup(asins)
        
        # 期待される結果の検証
        assert len(results) == 2
        assert results[0]['asin'] == 'B08N5WRWNW'
        assert results[0]['title'] == 'Monitor 1'
        assert results[1]['asin'] == 'B08EXAMPLE'
        assert results[1]['title'] == 'Monitor 2'
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_get_product_details_not_found(self, mock_client):
        """存在しないASINのテスト（TDD Red段階）"""
        mock_response = {
            'ItemsResult': {
                'Items': []
            }
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.get_items.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        client = PAAPIClient(config_path=self.settings_file)
        
        # 存在しないASINの場合はNoneが返される
        details = client.get_product_details('NONEXISTENT')
        
        assert details is None


class TestErrorHandling:
    """エラーハンドリングのテスト（TDD Red段階）"""
    
    def setup_method(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir()
        self.settings_file = self.config_dir / "settings.yaml"
        
        # テスト用設定データ
        self.test_settings = {
            'pa_api': {
                'access_key': 'test_access_key',
                'secret_key': 'test_secret_key',
                'associate_tag': 'test_tag',
                'region': 'us-east-1',
                'retry_attempts': 3,
                'retry_delay': 0.1
            }
        }
        
        with open(self.settings_file, 'w') as f:
            yaml.dump(self.test_settings, f)
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_authentication_error_during_search(self, mock_client):
        """検索時の認証エラーテスト（TDD Red段階）"""
        # 認証エラーのモック
        mock_client_instance = MagicMock()
        mock_client_instance.search_items.side_effect = ClientError(
            error_response={
                'Error': {
                    'Code': 'UnauthorizedException',
                    'Message': 'The request signature we calculated does not match'
                }
            },
            operation_name='SearchItems'
        )
        mock_client.return_value = mock_client_instance
        
        client = PAAPIClient(config_path=self.settings_file)
        
        # 認証エラーが適切に発生することを確認
        with pytest.raises(PAAPIAuthenticationError, match="認証エラー"):
            client.search_products(keywords="test product")
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_rate_limit_error_during_search(self, mock_client):
        """検索時のレート制限エラーテスト（TDD Red段階）"""
        # レート制限エラーのモック
        mock_client_instance = MagicMock()
        mock_client_instance.search_items.side_effect = ClientError(
            error_response={
                'Error': {
                    'Code': 'TooManyRequestsException',
                    'Message': 'You have exceeded your maximum request quota'
                }
            },
            operation_name='SearchItems'
        )
        mock_client.return_value = mock_client_instance
        
        client = PAAPIClient(config_path=self.settings_file)
        
        # レート制限エラーが適切に発生することを確認
        with pytest.raises(PAAPIRateLimitError, match="レート制限"):
            client.search_products(keywords="test product")
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_network_error_during_search(self, mock_client):
        """検索時のネットワークエラーテスト（TDD Red段階）"""
        # ネットワークエラーのモック
        mock_client_instance = MagicMock()
        mock_client_instance.search_items.side_effect = BotoCoreError()
        mock_client.return_value = mock_client_instance
        
        client = PAAPIClient(config_path=self.settings_file)
        
        # ネットワークエラーが適切に発生することを確認
        with pytest.raises(PAAPINetworkError, match="ネットワークエラー"):
            client.search_products(keywords="test product")
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_retry_on_network_error(self, mock_client):
        """ネットワークエラー時のリトライテスト（TDD Red段階）"""
        # 2回失敗後、3回目で成功するモック
        mock_client_instance = MagicMock()
        mock_response = {
            'SearchResult': {
                'Items': [{
                    'ASIN': 'B08N5WRWNW',
                    'ItemInfo': {'Title': {'DisplayValue': 'Test Product'}},
                    'CustomerReviews': {
                        'StarRating': {'DisplayValue': '4.5'},
                        'Count': 1000
                    }
                }]
            }
        }
        
        # side_effectに呼び出し順で異なる結果を設定
        mock_client_instance.search_items.side_effect = [
            BotoCoreError(),  # 1回目: ネットワークエラー
            BotoCoreError(),  # 2回目: ネットワークエラー
            mock_response     # 3回目: 成功
        ]
        mock_client.return_value = mock_client_instance
        
        client = PAAPIClient(config_path=self.settings_file)
        
        # リトライ後に成功することを確認
        results = client.search_products(keywords="test product")
        assert len(results) == 1
        assert results[0]['asin'] == 'B08N5WRWNW'
        
        # search_itemsが3回呼ばれたことを確認
        assert mock_client_instance.search_items.call_count == 3
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_authentication_error_during_get_details(self, mock_client):
        """商品詳細取得時の認証エラーテスト（TDD Red段階）"""
        # 認証エラーのモック
        mock_client_instance = MagicMock()
        mock_client_instance.get_items.side_effect = ClientError(
            error_response={
                'Error': {
                    'Code': 'UnauthorizedException',
                    'Message': 'Invalid associate tag'
                }
            },
            operation_name='GetItems'
        )
        mock_client.return_value = mock_client_instance
        
        client = PAAPIClient(config_path=self.settings_file)
        
        # 認証エラーが適切に発生することを確認
        with pytest.raises(PAAPIAuthenticationError, match="認証エラー"):
            client.get_product_details('B08N5WRWNW')
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_rate_limit_error_during_batch_lookup(self, mock_client):
        """バッチ取得時のレート制限エラーテスト（TDD Red段階）"""
        # レート制限エラーのモック
        mock_client_instance = MagicMock()
        mock_client_instance.get_items.side_effect = ClientError(
            error_response={
                'Error': {
                    'Code': 'TooManyRequestsException',
                    'Message': 'Request rate exceeded'
                }
            },
            operation_name='GetItems'
        )
        mock_client.return_value = mock_client_instance
        
        client = PAAPIClient(config_path=self.settings_file)
        
        # レート制限エラーが適切に発生することを確認
        with pytest.raises(PAAPIRateLimitError, match="レート制限"):
            client.batch_lookup(['B08N5WRWNW', 'B08EXAMPLE'])
    
    @patch('tools.pa_api_client.PAAPIClient._create_paapi_client')
    def test_partial_failure_in_batch_lookup(self, mock_client):
        """バッチ取得時の部分的失敗テスト（TDD Red段階）"""
        # 一部のASINが見つからない場合のモック
        mock_response = {
            'ItemsResult': {
                'Items': [
                    {
                        'ASIN': 'B08N5WRWNW',
                        'ItemInfo': {'Title': {'DisplayValue': 'Found Product'}},
                        'CustomerReviews': {
                            'StarRating': {'DisplayValue': '4.5'},
                            'Count': 1000
                        }
                    }
                ]
            },
            'Errors': [
                {
                    'Code': 'ItemNotFound',
                    'Message': 'The ItemId B08NOTFOUND was not found',
                    'ASIN': 'B08NOTFOUND'
                }
            ]
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.get_items.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        client = PAAPIClient(config_path=self.settings_file)
        
        # 部分的な結果が返されることを確認
        results = client.batch_lookup(['B08N5WRWNW', 'B08NOTFOUND'])
        
        # 見つかった商品のみが返される
        assert len(results) == 1
        assert results[0]['asin'] == 'B08N5WRWNW'
        assert results[0]['title'] == 'Found Product'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])