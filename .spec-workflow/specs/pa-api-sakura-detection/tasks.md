# Tasks Document

## Phase 1: PA-API基盤実装

- [x] 1. 設定ファイル拡張でPA-API認証情報追加
  - File: config/settings.yaml
  - Amazon PA-API 5.0の認証情報（access_key, secret_key, associate_tag）を追加
  - API制限設定（requests_per_day, timeout_seconds）を追加
  - Purpose: PA-API接続に必要な認証情報と制限設定を提供
  - _Leverage: 既存のconfig/settings.yaml構造_
  - _Requirements: 1.1_

- [x] 2. PA-API認証情報の環境変数管理実装
  - File: tools/pa_api_client.py (新規作成)
  - os.environ経由での認証情報読み込み機能
  - 環境変数不足時の適切なエラーハンドリング
  - Purpose: セキュアな認証情報管理とエラー処理
  - _Leverage: tools/affiliate_link_generator_integrated.py の ProjectSettings パターン_
  - _Requirements: 1.1_

- [x] 3. PAAPIClient基本クラスの実装
  - File: tools/pa_api_client.py (継続)
  - boto3を使用したPA-API 5.0接続クラス
  - 基本的なSearchItems, GetItems APIメソッド実装
  - レート制限とタイムアウト処理
  - Purpose: Amazon PA-API 5.0との安全で効率的な通信基盤
  - _Leverage: ProjectSettings設定読み込みパターン_
  - _Requirements: 1.1, 1.3_

- [x] 4. 商品検索メソッドの詳細実装
  - File: tools/pa_api_client.py (継続)
  - search_products()メソッドでキーワード・ブランド検索
  - 検索結果の品質基準フィルタリング（レビュー数500件以上、評価4.0以上）
  - 複数結果からの最適商品選択ロジック
  - Purpose: 品質基準を満たす商品の自動選択
  - _Leverage: 既存の品質基準設定 (config/settings.yaml)_
  - _Requirements: 1.2_

- [x] 5. 商品詳細情報取得メソッドの実装
  - File: tools/pa_api_client.py (継続)
  - get_product_details()メソッドでASIN詳細取得
  - 価格、レビュー数、評価、画像URL、メーカー名の構造化
  - batch_lookup()メソッドで複数商品の一括処理
  - Purpose: 記事作成に必要な商品情報の完全取得
  - _Leverage: Product dataclass構造_
  - _Requirements: 1.3_

## Phase 2: TDD実装フェーズ - PA-API Components

- [x] 6. PA-APIクライアントのTDD実装 (RED)
  - File: tests/test_pa_api_client.py (拡張)
  - PA-API認証、商品検索、詳細取得の失敗テスト作成
  - エラーハンドリング（AuthenticationError, RateLimitError, NetworkError）のテスト
  - Purpose: PA-APIクライアントの仕様を明確化し、失敗ケースを定義
  - _TDD Phase: RED - Write failing tests first_
  - _Leverage: 既存のtests/test_pa_api_client.py_
  - _Requirements: 1.1, 1.3_

- [x] 7. PA-APIクライアントのTDD実装 (GREEN)
  - File: tools/pa_api_client.py (継続)
  - テストを通過するPA-API例外処理とエラーハンドリング
  - カスタム例外クラス（AuthenticationError, RateLimitError等）
  - エラー発生時の詳細ログ出力
  - Purpose: RED段階のテストを全て通過させる実装
  - _TDD Phase: GREEN - Make tests pass with minimal code_
  - _Leverage: tests/test_pa_api_client.py_
  - _Requirements: 1.1, 1.3_

- [x] 8. PA-APIクライアントのTDD実装 (REFACTOR)
  - File: tools/pa_api_client.py (継続)
  - コードの重複削除、設定ファイル連携強化、パフォーマンス最適化
  - ログ出力改善、ドキュメンテーション追加
  - Purpose: テストを維持しながらコード品質を向上
  - _TDD Phase: REFACTOR - Improve code quality while keeping tests green_
  - _Leverage: tests/test_pa_api_client.py, config/settings.yaml_
  - _Requirements: 1.1, 1.3_

- [x] 9. Product dataclass拡張のTDD実装 (RED)
  - File: tests/test_product_dataclass.py (新規作成)
  - Product dataclass拡張フィールドの失敗テスト
  - 新フィールド（price, rating, reviews_count, merchant_id, sakura_score）の検証テスト
  - Purpose: Product dataclass拡張の仕様明確化
  - _TDD Phase: RED - Write failing tests first_
  - _Requirements: 1.3_

- [x] 10. Product dataclass拡張のTDD実装 (GREEN)
  - File: tools/affiliate_link_generator_integrated.py (修正)
  - 既存Product dataclassに新フィールド追加（price, rating, reviews_count, merchant_id, sakura_score）
  - is_quality_approved フラグの追加
  - Purpose: テストを通過する最小限のdataclass拡張
  - _TDD Phase: GREEN - Make tests pass with minimal code_
  - _Leverage: tests/test_product_dataclass.py, 既存Product dataclass_
  - _Requirements: 1.3_

- [x] 11. Product dataclass拡張のTDD実装 (REFACTOR)
  - File: tools/affiliate_link_generator_integrated.py (継続)
  - dataclass構造の最適化、型安全性向上、バリデーション強化
  - Purpose: テストを維持しながらdataclass品質向上
  - _TDD Phase: REFACTOR - Improve code quality while keeping tests green_
  - _Leverage: tests/test_product_dataclass.py_
  - _Requirements: 1.3_

## Phase 3: TDD実装フェーズ - Sakura Detection System

- [x] 12. SakuraDetectorのTDD実装 (RED)
  - File: tests/test_sakura_detector.py (新規作成)
  - 統計的異常値検出、レビュー数と評価の相関分析の失敗テスト
  - 同カテゴリ製品との比較分析機能のテスト
  - Purpose: サクラ検出システムの仕様明確化と失敗ケース定義
  - _TDD Phase: RED - Write failing tests first_
  - _Requirements: 3.1, 3.3_

- [x] 13. SakuraDetectorのTDD実装 (GREEN)
  - File: tools/sakura_detector.py (新規作成)
  - SakuraDetector基本クラス実装
  - 統計的異常値検出のベースクラス
  - レビュー数と評価の相関分析メソッド
  - Purpose: RED段階のテストを全て通過させる実装
  - _TDD Phase: GREEN - Make tests pass with minimal code_
  - _Leverage: tests/test_sakura_detector.py, ProjectSettings品質基準値_
  - _Requirements: 3.1, 3.3_

- [x] 14. SakuraDetector統計分析のTDD実装 (GREEN継続)
  - File: tools/sakura_detector.py (継続)
  - analyze_product()メソッドで個別商品分析
  - レビュー数vs評価の異常値検出アルゴリズム
  - 評価分布の偏り検出（極端に高評価が多い等）
  - Purpose: 数値的根拠に基づくサクラ度算出
  - _TDD Phase: GREEN - Make tests pass with minimal code_
  - _Leverage: tests/test_sakura_detector.py, pandas/numpyによる統計計算_
  - _Requirements: 3.1, 3.2_

- [x] 15. SakuraDetectorのTDD実装 (REFACTOR)
  - File: tools/sakura_detector.py (継続)
  - バッチ分析とスコアリング機能の最適化
  - batch_analyze()メソッドで複数商品の効率的分析
  - is_suspicious()メソッドでサクラ度判定（閾値30%）
  - Purpose: テストを維持しながらパフォーマンスとコード品質向上
  - _TDD Phase: REFACTOR - Improve code quality while keeping tests green_
  - _Leverage: tests/test_sakura_detector.py, 既存のバッチ処理パターン_
  - _Requirements: 3.2_

- [x] 16. 時系列分析機能のTDD実装 (オプション)
  - File: tools/sakura_detector.py (継続), tests/test_sakura_detector.py (拡張)
  - レビュー増加パターンの異常検出テスト→実装→リファクタリング
  - 短期間での急激な評価上昇の検出
  - Purpose: 時間的変化からのサクラレビュー検出強化（TDD完全適用）
  - _TDD Phase: Complete RED-GREEN-REFACTOR cycle_
  - _Leverage: 既存のデータキャッシュ機能_
  - _Requirements: 3.4_

## Phase 4: TDD実装フェーズ - Playwright Automation System

- [x] 17. PlaywrightAutomationのTDD実装 (RED)
  - File: tests/test_playwright_automation.py (新規作成)
  - Playwright環境セットアップ、ブラウザ操作の失敗テスト
  - サクラチェッカーサイトアクセス、結果パースの失敗テスト
  - Purpose: Playwright自動化システムの仕様明確化
  - _TDD Phase: RED - Write failing tests first_
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 18. PlaywrightAutomation環境セットアップのTDD実装 (GREEN)
  - File: pyproject.toml (修正), tools/playwright_automation.py (新規作成)
  - playwright依存関係の追加とブラウザインストール設定
  - PlaywrightAutomation基本クラス実装
  - ブラウザ起動・終了の管理
  - Purpose: テストを通過する基本自動化環境の構築
  - _TDD Phase: GREEN - Make tests pass with minimal code_
  - _Leverage: tests/test_playwright_automation.py, 既存のuv管理システム_
  - _Requirements: 4.1_

- [x] 19. PlaywrightAutomation機能のTDD実装 (GREEN継続)
  - File: tools/playwright_automation.py (継続)
  - サクラチェッカー自動入力機能
  - ASIN入力の自動化、検索実行とページ読み込み待機
  - 結果パース機能の実装
  - Purpose: 手動プロセスの完全自動化
  - _TDD Phase: GREEN - Make tests pass with minimal code_
  - _Leverage: tests/test_playwright_automation.py_
  - _Requirements: 4.1, 4.3_

- [x] 20. PlaywrightAutomationのTDD実装 (REFACTOR)
  - File: tools/playwright_automation.py (継続)
  - バッチ処理最適化と自動化エラーハンドリング強化
  - check_products()メソッドでリスト処理、batch_check()で5商品ずつの効率的処理
  - NetworkError、BrowserError例外処理
  - Purpose: テストを維持しながら15商品20分処理の実現
  - _TDD Phase: REFACTOR - Improve code quality while keeping tests green_
  - _Leverage: tests/test_playwright_automation.py, 既存のエラーハンドリングパターン_
  - _Requirements: 4.4, 4.5_

## Phase 5: TDD実装フェーズ - System Integration

- [x] 21. システム統合のTDD実装 (RED)
  - File: tests/test_integration_workflow.py (新規作成)
  - IntegratedAffiliateLinkGenerator統合の失敗テスト
  - PAAPIClient, SakuraDetector, PlaywrightAutomationの連携テスト
  - 品質チェックフロー最適化のテスト
  - Purpose: システム全体の統合品質を保証する仕様定義
  - _TDD Phase: RED - Write failing integration tests first_
  - _Requirements: 全要件統合_

- [x] 22. システム統合のTDD実装 (GREEN)
  - File: tools/affiliate_link_generator_integrated.py (修正)
  - PAAPIClient, SakuraDetector, PlaywrightAutomationの統合
  - _meets_quality_criteria()メソッドの拡張
  - 新しいサクラ検出結果の品質判定への組み込み
  - Purpose: 統合テストを通過させるシステム連携
  - _TDD Phase: GREEN - Make integration tests pass_
  - _Leverage: tests/test_integration_workflow.py, 既存のIntegratedAffiliateLinkGeneratorクラス_
  - _Requirements: 全要件統合_

- [x] 23. システム統合のTDD実装 (REFACTOR)
  - File: tools/affiliate_link_generator_integrated.py (継続)
  - PA-API → サクラ検出 → Playwright確認の効率的なフロー最適化
  - 各段階での品質基準による早期除外、処理時間の最適化（キャッシュ活用等）
  - Purpose: テストを維持しながらシステム全体のパフォーマンス向上
  - _TDD Phase: REFACTOR - Improve system performance while keeping tests green_
  - _Leverage: tests/test_integration_workflow.py, 既存の処理フロー構造_
  - _Requirements: 全要件統合_

## Phase 6: TDD実装フェーズ - Quality Assurance & Performance

- [x] 24. パフォーマンステストのTDD実装 (RED)
  - File: tests/test_performance.py (新規作成)
  - 15商品20分処理の達成確認テスト
  - API呼び出し時間の測定、メモリ使用量の監視テスト
  - Purpose: パフォーマンス要件の失敗ケース定義
  - _TDD Phase: RED - Write failing performance tests first_
  - _Requirements: 全要件（パフォーマンス要件）_

- [x] 25. パフォーマンステストのTDD実装 (GREEN)
  - File: システム全体の最適化
  - パフォーマンス要件を満たす最小限の実装
  - 処理時間短縮、メモリ効率化
  - Purpose: パフォーマンステストを通過させる実装
  - _TDD Phase: GREEN - Make performance tests pass_
  - _Leverage: tests/test_performance.py, 既存の処理時間測定パターン_
  - _Requirements: 全要件（パフォーマンス要件）_

- [x] 26. エラー処理の総合TDD実装 (RED-GREEN-REFACTOR)
  - File: tests/test_error_handling.py (新規作成)
  - 各種API エラーの適切な例外発生確認テスト→実装→改善
  - エラーメッセージの明確性テスト、システム停止時の状態確認
  - Purpose: エラー処理要件の完全達成（TDD完全適用）
  - _TDD Phase: Complete RED-GREEN-REFACTOR cycle_
  - _Leverage: 既存のエラーハンドリングパターン_
  - _Requirements: 全要件（エラー処理要件）_

## Phase 7: TDD品質保証とドキュメンテーション

- [x] 27. TDD実装ドキュメントの作成
  - File: docs/tdd_implementation_pa_api.md
  - Red-Green-Refactorサイクルの実装記録と学習ポイント
  - 各コンポーネントのテスト戦略とカバレッジレポート
  - PA-API、サクラ検出、Playwright自動化のTDD実践例
  - Purpose: TDD実装プロセスの記録と今後のメンテナンスガイド
  - _Requirements: Documentation for TDD process_

- [x] 28. 継続的品質改善システムの構築
  - File: scripts/pa_api_quality_check.py, .github/workflows/pa_api_ci.yml
  - 自動テスト実行、コードカバレッジ測定、品質メトリクス監視
  - 継続的インテグレーション設定とTDD遵守チェック
  - Purpose: TDD原則の継続的な遵守と品質向上の自動化
  - _Requirements: Continuous quality improvement for PA-API system_

- [x] 29. ドキュメント更新とクリーンアップ
  - File: README.md, docs/ (修正)
  - 新機能の使用方法説明、設定ファイルの更新手順
  - トラブルシューティングガイド、TDD実装の説明
  - Purpose: ユーザビリティ要件の達成とTDD文化の浸透
  - _Leverage: 既存のドキュメント構造_
  - _Requirements: 全要件（ユーザビリティ要件）、TDD documentation_