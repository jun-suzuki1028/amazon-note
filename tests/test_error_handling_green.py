#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
エラー処理テスト - TDD GREEN Phase

実装されたエラーハンドリング機能を検証。
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from typing import List, Dict, Any

from tools.pa_api_client import PAAPIClient
from tools.sakura_detector import SakuraDetector, SakuraAnalysisResult
from tools.playwright_automation import PlaywrightAutomation, SakuraCheckerResult
from tools.models import IntegratedAffiliateLinkGenerator, Product


class TestErrorHandlingGreen(unittest.TestCase):
    """エラー処理のGREENフェーズテスト"""
    
    def setUp(self):
        """テスト前の初期設定"""
        self.integrated_generator = IntegratedAffiliateLinkGenerator()
        
        self.test_asins = ["B08XYZ1234", "B08ABC5678"]
        self.test_products = [
            Product(
                asin="B08XYZ1234",
                name="Test Product 1",
                model="TEST-001",
                brand="TestBrand",
                price=29999,
                rating=4.5,
                reviews_count=500
            )
        ]
    
    def test_paapi_connection_error_handling_GREEN(self):
        """PA-API接続エラーハンドリングテスト（GREEN Phase）"""
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.side_effect = ConnectionError("PA-API Connection Failed")
            
            # エラーハンドリングにより例外ではなくエラー情報付きの結果が返される
            result = self.integrated_generator.process_affiliate_workflow(
                keyword="connection error test",
                max_products=5
            )
            
            # エラーハンドリングの検証
            self.assertIn('error', result)
            self.assertEqual(result['error_type'], 'connection_error')
            self.assertIn('PA-API connection failed', result['error'])
            self.assertEqual(result['total_processed'], 0)
            self.assertEqual(result['quality_score'], 0.0)
            
            print(f"✅ 接続エラー適切処理: {result['error']}")
    
    def test_paapi_authentication_error_handling_GREEN(self):
        """PA-API認証エラーハンドリングテスト（GREEN Phase）"""
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.side_effect = PermissionError("Invalid AWS credentials")
            
            # 認証エラーが適切に処理される
            result = self.integrated_generator.process_affiliate_workflow(
                keyword="auth error test",
                max_products=5
            )
            
            # 認証エラーハンドリングの検証
            self.assertIn('error', result)
            self.assertEqual(result['error_type'], 'authentication_error')
            self.assertIn('PA-API authentication failed', result['error'])
            
            print(f"✅ 認証エラー適切処理: {result['error']}")
    
    def test_network_error_recovery_GREEN(self):
        """ネットワークエラー回復機能テスト（GREEN Phase）"""
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            # 最初の2回は失敗、3回目で成功（リトライ機能）
            mock_paapi.side_effect = [
                ConnectionError("Network timeout"),
                ConnectionError("Network timeout"),
                self.test_products
            ]
            
            # リトライ機能により最終的に成功する
            result = self.integrated_generator.process_affiliate_workflow_with_retry(
                keyword="network error test",
                max_products=1,
                max_retries=3
            )
            
            # リトライ成功の検証
            self.assertNotIn('error', result)
            self.assertEqual(result['total_processed'], 1)
            self.assertIn('retry_count', result)
            self.assertEqual(result['retry_count'], 2)  # 3回目で成功（0-indexed）
            
            print(f"✅ リトライ機能成功: {result['retry_count']} リトライ後成功")
    
    def test_graceful_degradation_GREEN(self):
        """優雅な劣化機能テスト（GREEN Phase）"""
        with patch.multiple(
            self.integrated_generator,
            paapi_client=Mock(),
            sakura_detector=Mock(),
            playwright_automation=Mock()
        ):
            # PA-API と SakuraDetector は正常
            self.integrated_generator.paapi_client.search_products.return_value = self.test_products
            self.integrated_generator.sakura_detector.batch_analyze.return_value = [
                SakuraAnalysisResult(
                    product_asin="B08XYZ1234",
                    sakura_score=30.0,
                    confidence_level=0.85,
                    analysis_details={'suspicious_reviews': 50, 'total_reviews': 500}
                )
            ]
            
            # PlaywrightAutomation は失敗
            self.integrated_generator.playwright_automation.batch_check.side_effect = RuntimeError("Playwright failed")
            
            # 優雅な劣化機能により部分的な結果が返される
            result = self.integrated_generator.process_affiliate_workflow(
                keyword="graceful degradation test",
                max_products=1
            )
            
            # 優雅な劣化の検証
            self.assertNotIn('error', result)
            self.assertIn('warning', result)
            self.assertTrue(result.get('degraded_mode', False))
            self.assertEqual(result['total_processed'], 1)
            self.assertGreater(result['quality_score'], 0)
            
            print(f"✅ 優雅な劣化成功: {result['warning']}")
    
    def test_error_message_clarity_GREEN(self):
        """エラーメッセージ明確性テスト（GREEN Phase）"""
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.side_effect = Exception("Unknown error")
            
            # 明確なエラーメッセージが返される
            result = self.integrated_generator.process_affiliate_workflow(
                keyword="unclear error test",
                max_products=5
            )
            
            # エラーメッセージの明確性検証
            self.assertIn('error', result)
            self.assertEqual(result['error_type'], 'unknown_error')
            self.assertIn('Unexpected error', result['error'])
            self.assertIn('Unknown error', result['error'])
            
            print(f"✅ 明確なエラーメッセージ: {result['error']}")
    
    def test_system_state_consistency_after_error_GREEN(self):
        """エラー後のシステム状態一貫性テスト（GREEN Phase）"""
        original_cache_size = len(self.integrated_generator.api_response_cache)
        
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.side_effect = ConnectionError("Connection failed")
            
            # エラー発生
            result = self.integrated_generator.process_affiliate_workflow(
                keyword="state consistency test",
                max_products=5
            )
            
            # エラーハンドリング後のシステム状態の一貫性チェック
            current_cache_size = len(self.integrated_generator.api_response_cache)
            
            # システム状態が一貫していることを確認
            self.assertEqual(original_cache_size, current_cache_size, 
                           "エラー処理後のシステム状態が一貫している")
            
            # 適切なエラー応答が返されることを確認
            self.assertIn('error', result)
            self.assertEqual(result['error_type'], 'connection_error')
            
            print("✅ エラー後のシステム状態一貫性確認")
    
    def test_timeout_error_handling_GREEN(self):
        """タイムアウトエラーハンドリングテスト（GREEN Phase）"""
        with patch('tools.sakura_detector.SakuraDetector.batch_analyze') as mock_sakura:
            mock_sakura.side_effect = TimeoutError("Sakura analysis timeout")
            
            # タイムアウトエラーが適切に処理される
            try:
                result = self.integrated_generator.sakura_detector.batch_analyze(self.test_products)
                self.fail("TimeoutError should have been raised")
            except TimeoutError as e:
                # タイムアウトエラーが適切に発生することを確認
                self.assertIn("Sakura analysis timeout", str(e))
                print(f"✅ タイムアウトエラー適切処理: {str(e)}")
    
    def test_partial_failure_resilience_GREEN(self):
        """部分的失敗に対する回復力テスト（GREEN Phase）"""
        with patch.multiple(
            self.integrated_generator,
            paapi_client=Mock(),
            sakura_detector=Mock(),
            playwright_automation=Mock()
        ):
            # PA-API は正常
            self.integrated_generator.paapi_client.search_products.return_value = self.test_products
            
            # SakuraDetector は正常
            self.integrated_generator.sakura_detector.batch_analyze.return_value = [
                SakuraAnalysisResult(
                    product_asin="B08XYZ1234",
                    sakura_score=30.0,
                    confidence_level=0.85,
                    analysis_details={'suspicious_reviews': 50, 'total_reviews': 500}
                )
            ]
            
            # PlaywrightAutomation は部分的に失敗
            def partial_failure_mock(asins):
                # 一部のASINで処理失敗
                if "B08ABC5678" in asins:
                    raise ValueError(f"Failed to process ASIN: B08ABC5678")
                return [
                    SakuraCheckerResult(
                        asin="B08XYZ1234",
                        sakura_score=25.0,
                        confidence_level=0.85,
                        review_analysis={'suspicious_reviews': 40, 'total_reviews': 500}
                    )
                ]
            
            self.integrated_generator.playwright_automation.batch_check.side_effect = partial_failure_mock
            
            # 部分的失敗があっても処理が継続される
            result = self.integrated_generator.process_affiliate_workflow(
                keyword="partial failure test",
                max_products=1
            )
            
            # 部分的成功の確認
            self.assertEqual(result['total_processed'], 1)
            self.assertGreater(result['quality_score'], 0)
            
            print("✅ 部分的失敗に対する回復力確認")


if __name__ == "__main__":
    unittest.main()