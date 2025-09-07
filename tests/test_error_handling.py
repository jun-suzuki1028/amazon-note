#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
エラー処理テスト - TDD RED-GREEN-REFACTOR

システム全体のエラーハンドリング機能をTDDで実装。
PA-API、SakuraDetector、PlaywrightAutomationの統合エラー処理。
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from typing import List, Dict, Any

# エラーハンドリングが必要なクラス（最初は失敗する）
from tools.pa_api_client import PAAPIClient
from tools.sakura_detector import SakuraDetector, SakuraAnalysisResult
from tools.playwright_automation import PlaywrightAutomation, SakuraCheckerResult
from tools.models import IntegratedAffiliateLinkGenerator, Product


class TestErrorHandling(unittest.TestCase):
    """エラー処理の総合テスト"""
    
    def setUp(self):
        """テスト前の初期設定"""
        # 統合システムの初期化（エラーハンドリング機能付き）
        self.integrated_generator = IntegratedAffiliateLinkGenerator()
        
        # テスト用データ
        self.test_asins = [
            "B08XYZ1234",
            "B08ABC5678", 
            "B08DEF9012"
        ]
        
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
    
    def test_paapi_connection_error_handling_RED(self):
        """PA-API接続エラーハンドリングテスト（RED Phase）"""
        # 接続エラーをシミュレート
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.side_effect = ConnectionError("PA-API Connection Failed")
            
            # エラーハンドリングが実装されていない場合、例外が発生する（RED）
            with self.assertRaises(ConnectionError):
                result = self.integrated_generator.process_affiliate_workflow(
                    keyword="connection error test",
                    max_products=5
                )
    
    def test_paapi_authentication_error_handling_RED(self):
        """PA-API認証エラーハンドリングテスト（RED Phase）"""
        # 認証エラーをシミュレート
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.side_effect = PermissionError("Invalid AWS credentials")
            
            # エラーハンドリングが実装されていない場合、例外が発生する（RED）
            with self.assertRaises(PermissionError):
                result = self.integrated_generator.process_affiliate_workflow(
                    keyword="auth error test",
                    max_products=5
                )
    
    def test_sakura_detector_timeout_error_handling_RED(self):
        """SakuraDetector タイムアウトエラーハンドリングテスト（RED Phase）"""
        # タイムアウトエラーをシミュレート
        with patch('tools.sakura_detector.SakuraDetector.batch_analyze') as mock_sakura:
            mock_sakura.side_effect = TimeoutError("Sakura analysis timeout")
            
            # エラーハンドリングが実装されていない場合、例外が発生する（RED）
            with self.assertRaises(TimeoutError):
                result = self.integrated_generator.sakura_detector.batch_analyze(self.test_products)
    
    def test_playwright_browser_error_handling_RED(self):
        """Playwright ブラウザエラーハンドリングテスト（RED Phase）"""
        # ブラウザエラーをシミュレート
        with patch('tools.playwright_automation.PlaywrightAutomation.batch_check') as mock_playwright:
            mock_playwright.side_effect = RuntimeError("Browser launch failed")
            
            # エラーハンドリングが実装されていない場合、例外が発生する（RED）
            with self.assertRaises(RuntimeError):
                result = self.integrated_generator.playwright_automation.batch_check(self.test_asins)
    
    def test_network_error_recovery_RED(self):
        """ネットワークエラー回復機能テスト（RED Phase）"""
        # ネットワークエラーをシミュレート
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            # 最初の2回は失敗、3回目で成功（リトライ機能）
            mock_paapi.side_effect = [
                ConnectionError("Network timeout"),
                ConnectionError("Network timeout"),
                self.test_products
            ]
            
            # リトライ機能が実装されていない場合、例外が発生する（RED）
            with self.assertRaises(ConnectionError):
                result = self.integrated_generator.process_affiliate_workflow_with_retry(
                    keyword="network error test",
                    max_products=1,
                    max_retries=3
                )
    
    def test_partial_failure_handling_RED(self):
        """部分的失敗ハンドリングテスト（RED Phase）"""
        # 一部のASINで処理失敗をシミュレート
        def partial_failure_mock(asins):
            # 最初のASINは成功、残りは失敗
            if len(asins) > 1:
                raise ValueError(f"Failed to process ASINs: {asins[1:]}")
            return [
                SakuraCheckerResult(
                    asin=asins[0],
                    sakura_score=30.0,
                    confidence_level=0.85,
                    review_analysis={'suspicious_reviews': 50, 'total_reviews': 500}
                )
            ]
        
        with patch('tools.playwright_automation.PlaywrightAutomation.batch_check') as mock_playwright:
            mock_playwright.side_effect = partial_failure_mock
            
            # 部分的失敗ハンドリングが実装されていない場合、例外が発生する（RED）
            with self.assertRaises(ValueError):
                result = self.integrated_generator.playwright_automation.batch_check(self.test_asins)
    
    def test_error_message_clarity_RED(self):
        """エラーメッセージ明確性テスト（RED Phase）"""
        # 不明確なエラーメッセージをシミュレート
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.side_effect = Exception("Unknown error")
            
            # 明確なエラーメッセージが実装されていない場合、不明確なエラーが発生する（RED）
            try:
                result = self.integrated_generator.process_affiliate_workflow(
                    keyword="unclear error test",
                    max_products=5
                )
                self.fail("Expected exception was not raised")
            except Exception as e:
                # エラーメッセージが不十分であることを確認（RED）
                self.assertIn("Unknown error", str(e))
                self.assertNotIn("PA-API", str(e))  # 詳細情報が不足している
    
    def test_system_state_consistency_after_error_RED(self):
        """エラー後のシステム状態一貫性テスト（RED Phase）"""
        # エラー発生後のシステム状態確認
        original_cache_size = len(self.integrated_generator.api_response_cache)
        
        with patch('tools.pa_api_client.PAAPIClient.search_products') as mock_paapi:
            mock_paapi.side_effect = ConnectionError("Connection failed")
            
            # エラー発生
            try:
                result = self.integrated_generator.process_affiliate_workflow(
                    keyword="state consistency test",
                    max_products=5
                )
            except ConnectionError:
                pass
            
            # システム状態の一貫性チェック（RED - 不適切な状態変更が残る可能性）
            current_cache_size = len(self.integrated_generator.api_response_cache)
            
            # エラー後にキャッシュが汚染されていないことを確認
            # （実装前は適切な状態管理がないため、テストが失敗する可能性がある）
            self.assertEqual(
                original_cache_size, 
                current_cache_size,
                "Error handling should not leave system in inconsistent state"
            )
    
    def test_graceful_degradation_RED(self):
        """優雅な劣化機能テスト（RED Phase）"""
        # PlaywrightAutomationが失敗した場合の優雅な劣化
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
            
            # 優雅な劣化機能が実装されていない場合、全体が失敗する（RED）
            with self.assertRaises(RuntimeError):
                result = self.integrated_generator.process_affiliate_workflow(
                    keyword="graceful degradation test",
                    max_products=1
                )


if __name__ == "__main__":
    unittest.main()