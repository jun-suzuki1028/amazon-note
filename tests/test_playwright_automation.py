#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PlaywrightAutomationのテスト - TDD RED Phase

サクラチェッカーサイト自動化システムのテスト。
Playwrightを使用した15商品60分→20分高速化の実現。

TDD RED Phase: 失敗するテストを先に書く
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
from typing import List, Dict, Any
import pandas as pd

# These imports will fail initially (RED phase)
from tools.playwright_automation import (
    PlaywrightAutomation,
    SakuraCheckerResult,
    BatchProcessor,
    BrowserManager
)


class TestPlaywrightAutomation(unittest.TestCase):
    """PlaywrightAutomationの基本機能テスト"""
    
    def setUp(self):
        """テスト前の初期設定"""
        self.automation = PlaywrightAutomation()
        
        # テスト用ASINデータ
        self.test_asins = [
            "B08XYZ1234",
            "B08ABC5678",
            "B08DEF9012"
        ]
        
        # 期待される結果データ
        self.expected_result = SakuraCheckerResult(
            asin="B08XYZ1234",
            sakura_score=65.0,
            confidence_level=0.85,
            review_analysis={
                'suspicious_reviews': 150,
                'total_reviews': 500,
                'ratio': 0.3
            },
            checked_at="2024-01-01 12:00:00"
        )
    
    def test_automation_initialization(self):
        """PlaywrightAutomation初期化のテスト"""
        self.assertIsNotNone(self.automation)
        self.assertIsInstance(self.automation, PlaywrightAutomation)
        
        # 設定の確認
        self.assertEqual(self.automation.batch_size, 5)
        self.assertEqual(self.automation.request_interval, 3.0)  # 3秒間隔
        self.assertEqual(self.automation.timeout, 30000)  # 30秒タイムアウト
    
    def test_browser_manager_setup(self):
        """ブラウザマネージャーのセットアップテスト"""
        browser_manager = BrowserManager()
        
        # ヘッドレスモード設定
        self.assertTrue(browser_manager.headless)
        
        # User-Agent設定
        self.assertIn("Mozilla", browser_manager.user_agent)
        
        # ビューポート設定
        self.assertEqual(browser_manager.viewport_width, 1920)
        self.assertEqual(browser_manager.viewport_height, 1080)
    
    @patch('tools.playwright_automation.PlaywrightAutomation.fetch_sakura_checker_data')
    def test_single_product_check(self, mock_fetch):
        """単一商品のサクラチェック"""
        # モック設定
        mock_fetch.return_value = {
            'sakura_score': 65.0,
            'suspicious_count': 150,
            'total_count': 500
        }
        
        # 実行
        result = self.automation.check_product("B08XYZ1234")
        
        # 検証
        self.assertIsInstance(result, SakuraCheckerResult)
        self.assertEqual(result.asin, "B08XYZ1234")
        self.assertEqual(result.sakura_score, 65.0)
        self.assertIsNotNone(result.review_analysis)
        
        # API呼び出し確認
        mock_fetch.assert_called_once_with("B08XYZ1234")
    
    @patch('tools.playwright_automation.PlaywrightAutomation.fetch_sakura_checker_data')
    def test_batch_processing(self, mock_fetch):
        """バッチ処理のテスト"""
        # モック設定（3つの商品）
        mock_fetch.side_effect = [
            {'sakura_score': 65.0, 'suspicious_count': 150, 'total_count': 500},
            {'sakura_score': 20.0, 'suspicious_count': 30, 'total_count': 300},
            {'sakura_score': 85.0, 'suspicious_count': 400, 'total_count': 450}
        ]
        
        # バッチ処理実行
        results = self.automation.batch_check(self.test_asins)
        
        # 検証
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].sakura_score, 65.0)
        self.assertEqual(results[1].sakura_score, 20.0)
        self.assertEqual(results[2].sakura_score, 85.0)
        
        # 呼び出し回数確認
        self.assertEqual(mock_fetch.call_count, 3)
    
    def test_rate_limiting(self):
        """レート制限のテスト"""
        import time
        
        # バッチプロセッサーを作成
        batch_processor = BatchProcessor(rate_limit=3.0)
        
        # 2つのリクエストの時間差を測定
        start_time = time.time()
        batch_processor.process_with_rate_limit(lambda: None)
        batch_processor.process_with_rate_limit(lambda: None)
        elapsed_time = time.time() - start_time
        
        # 3秒以上の間隔があることを確認
        self.assertGreaterEqual(elapsed_time, 3.0)
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # ネットワークエラーのシミュレーション
        with patch('tools.playwright_automation.PlaywrightAutomation.fetch_sakura_checker_data') as mock_fetch:
            mock_fetch.side_effect = ConnectionError("Network error")
            
            # エラーが適切に処理されることを確認
            result = self.automation.check_product("B08XYZ1234")
            
            self.assertIsNone(result)
            self.assertTrue(self.automation.has_error)
            self.assertIn("Network error", self.automation.last_error)
    
    def test_15_products_time_optimization(self):
        """15商品処理の時間最適化テスト"""
        import time
        
        # 15個のASIN
        test_asins_15 = [f"B08{i:07d}" for i in range(15)]
        
        # モック設定（高速応答）
        with patch('tools.playwright_automation.PlaywrightAutomation.fetch_sakura_checker_data') as mock_fetch:
            mock_fetch.return_value = {
                'sakura_score': 50.0,
                'suspicious_count': 100,
                'total_count': 200
            }
            
            # 時間測定
            start_time = time.time()
            results = self.automation.batch_check(test_asins_15)
            elapsed_time = time.time() - start_time
            
            # 検証
            self.assertEqual(len(results), 15)
            # 20分（1200秒）以内で完了（モックなのでもっと高速）
            self.assertLess(elapsed_time, 1200)
            
            # バッチサイズによる最適化確認（5個ずつ3バッチ）
            self.assertEqual(mock_fetch.call_count, 15)
    
    def test_parse_sakura_checker_response(self):
        """サクラチェッカーレスポンスのパーステスト"""
        # HTMLレスポンスのモック
        mock_html = """
        <div class="sakura-score">
            <span class="score-value">65</span>
            <span class="score-label">%</span>
        </div>
        <div class="review-stats">
            <div class="suspicious">疑わしいレビュー: 150件</div>
            <div class="total">総レビュー数: 500件</div>
        </div>
        """
        
        # パース実行
        result = self.automation.parse_response(mock_html)
        
        # 検証
        self.assertEqual(result['sakura_score'], 65.0)
        self.assertEqual(result['suspicious_count'], 150)
        self.assertEqual(result['total_count'], 500)
    
    def test_async_browser_operation(self):
        """非同期ブラウザ操作のテスト（同期的にテスト）"""
        # 非同期メソッドが存在することを確認
        self.assertTrue(hasattr(self.automation, 'async_check_product'))
        self.assertTrue(asyncio.iscoroutinefunction(self.automation.async_check_product))
        
        # 非同期コンテキストマネージャーのメソッドが存在することを確認
        self.assertTrue(hasattr(self.automation, '__aenter__'))
        self.assertTrue(hasattr(self.automation, '__aexit__'))
        
        # BrowserManagerクラスの非同期メソッドの存在確認
        browser_manager = BrowserManager()
        self.assertTrue(hasattr(browser_manager, 'setup'))
        self.assertTrue(hasattr(browser_manager, 'cleanup'))
    
    def test_result_caching(self):
        """結果キャッシュのテスト"""
        # キャッシュ機能の確認
        with patch('tools.playwright_automation.PlaywrightAutomation.fetch_sakura_checker_data') as mock_fetch:
            mock_fetch.return_value = {
                'sakura_score': 65.0,
                'suspicious_count': 150,
                'total_count': 500
            }
            
            # 1回目の呼び出し
            result1 = self.automation.check_product("B08XYZ1234", use_cache=True)
            
            # 2回目の呼び出し（キャッシュから）
            result2 = self.automation.check_product("B08XYZ1234", use_cache=True)
            
            # 検証
            self.assertEqual(result1.sakura_score, result2.sakura_score)
            # API呼び出しは1回のみ
            mock_fetch.assert_called_once()
    
    def test_retry_mechanism(self):
        """リトライメカニズムのテスト"""
        with patch('tools.playwright_automation.PlaywrightAutomation.fetch_sakura_checker_data') as mock_fetch:
            # 最初の2回は失敗、3回目で成功
            mock_fetch.side_effect = [
                ConnectionError("Network error"),
                TimeoutError("Timeout"),
                {'sakura_score': 65.0, 'suspicious_count': 150, 'total_count': 500}
            ]
            
            # リトライ付きで実行
            result = self.automation.check_product("B08XYZ1234", max_retries=3)
            
            # 検証
            self.assertIsNotNone(result)
            self.assertEqual(result.sakura_score, 65.0)
            self.assertEqual(mock_fetch.call_count, 3)


if __name__ == "__main__":
    unittest.main()