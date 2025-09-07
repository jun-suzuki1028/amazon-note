# Tasks Document

## Phase 1: プロジェクト基盤構築

- [x] 1. プロジェクト構造の初期化
  - File: README.md, .gitignore
  - プロジェクトディレクトリ構造の作成
  - プロジェクト概要とセットアップ手順の記述
  - Purpose: システムの基盤となるディレクトリ構造を構築
  - _Requirements: Design/Project Structure_

- [x] 2. 設定ファイルの作成
  - File: config/settings.yaml
  - アフィリエイトID、デフォルト設定値の定義
  - プロジェクト共通設定の管理
  - Purpose: システム全体で使用する設定情報を管理
  - _Requirements: Design/Architecture_

## Phase 2: テンプレートシステム構築

- [x] 3. ペルソナテンプレートの作成
  - File: templates/persona/default_persona.md
  - 基本情報、ライフスタイル、購買行動、悩みのテンプレート構造
  - Claude Codeとの対話用プロンプトテンプレート
  - Purpose: ペルソナ作成時のガイドと構造化フォーマットを提供
  - _Requirements: 1. ペルソナ作成とDeepResearchプロンプト生成機能_

- [x] 4. DeepResearchプロンプトテンプレートの作成
  - File: templates/prompts/research_prompts.md
  - キーワードリサーチ、競合分析、製品調査用プロンプトテンプレート
  - ペルソナ情報を活用したプロンプト生成ガイド
  - Purpose: 効果的なDeepResearchプロンプトのテンプレートを提供
  - _Requirements: 1. ペルソナ作成とDeepResearchプロンプト生成機能_

- [x] 5. リサーチ結果テンプレートの作成
  - File: templates/research/research_template.md
  - キーワード分析、競合分析、製品情報の構造化フォーマット
  - サクラチェッカー確認結果記録テンプレート
  - Purpose: リサーチ結果の統一フォーマットと記録方法を提供
  - _Requirements: 2. DeepResearch実行と結果管理機能_

- [x] 6. 記事テンプレートの作成
  - File: templates/article/ranking_article.md
  - 導入文、ランキング、製品レビュー、まとめの構造テンプレート
  - アフィリエイトリンク挿入箇所のマーカー定義
  - Purpose: 記事の標準構造とフォーマットを提供
  - _Requirements: 3. 調査結果参照型記事生成機能_

## Phase 3: ワークフロー管理システム

- [x] 7. プロジェクト管理テンプレートの作成
  - File: templates/project/project_status.md
  - プロジェクト進捗管理フォーマット
  - 各フェーズの完了チェックリスト
  - Purpose: プロジェクト全体の状態管理と進捗追跡を支援
  - _Requirements: 5. ワークフロー管理とプロジェクト追跡機能_

- [x] 8. 作業手順書の作成
  - File: docs/workflow_guide.md
  - 各フェーズでのClaude Codeとの対話手順
  - テンプレート活用方法とベストプラクティス
  - Purpose: 効率的なワークフロー実行のガイドを提供
  - _Requirements: 5. ワークフロー管理とプロジェクト追跡機能_

## Phase 4: ペルソナ作成ワークフロー

- [x] 9. ペルソナ作成プロンプトの実装
  - File: prompts/persona_creation.md
  - Claude Codeでペルソナを作成するための詳細プロンプト
  - 対話形式でペルソナ情報を収集するガイド
  - Purpose: Claude Codeを活用した効果的なペルソナ作成を実現
  - _Leverage: templates/persona/default_persona.md_
  - _Requirements: 1. ペルソナ作成とDeepResearchプロンプト生成機能_

- [x] 10. ペルソナ検証チェックリストの作成
  - File: checklists/persona_validation.md
  - 作成されたペルソナの品質確認項目
  - ペルソナの改善提案生成ガイド
  - Purpose: 高品質なペルソナ作成を保証する検証システム
  - _Requirements: 1. ペルソナ作成とDeepResearchプロンプト生成機能_

## Phase 5: プロンプト生成ワークフロー

- [x] 11. プロンプト生成プロンプトの実装
  - File: prompts/prompt_generation.md
  - ペルソナ情報を基にDeepResearchプロンプトを生成するプロンプト
  - Gemini用とDeepResearch用のプロンプト最適化ガイド
  - Purpose: ペルソナに最適化されたリサーチプロンプトの自動生成
  - _Leverage: templates/prompts/research_prompts.md_
  - _Requirements: 1. ペルソナ作成とDeepResearchプロンプト生成機能_

- [x] 12. プロンプト最適化ガイドの作成
  - File: guides/prompt_optimization.md
  - プロンプトの効果を高める改善手法
  - リサーチ目的別のプロンプト調整方法
  - Purpose: より効果的なリサーチを実現するプロンプト改善支援
  - _Requirements: 1. ペルソナ作成とDeepResearchプロンプト生成機能_

## Phase 6: リサーチ実行ワークフロー

- [x] 13. Gemini MCP活用ガイドの作成
  - File: guides/gemini_research.md
  - Gemini MCPでのDeepResearch実行手順
  - エラー時のトラブルシューティング方法
  - Purpose: Gemini MCPを活用した効率的なリサーチ実行を支援
  - _Requirements: 2. DeepResearch実行と結果管理機能_

- [x] 14. 手動リサーチガイドの作成
  - File: guides/manual_research.md
  - Gemini MCP利用不可時の手動リサーチ手順
  - リサーチ結果の構造化保存方法
  - Purpose: Gemini MCP非依存でのリサーチ実行を支援
  - _Leverage: templates/research/research_template.md_
  - _Requirements: 2. DeepResearch実行と結果管理機能_

- [x] 15. サクラチェッカー確認ワークフローの構築
  - File: workflows/sakura_validation.md
  - 製品リストからサクラチェッカー確認手順
  - 確認結果の記録と評価基準
  - Purpose: 信頼性の高い製品選定ワークフローを提供
  - _Requirements: 2. DeepResearch実行と結果管理機能_

- [x] 16. リサーチ結果統合プロンプトの実装
  - File: prompts/research_integration.md
  - 複数のリサーチ結果を統合するプロンプト
  - データ品質チェックと改善提案生成
  - Purpose: Claude Codeでリサーチデータの品質向上と統合を実現
  - _Requirements: 2. DeepResearch実行と結果管理機能_

## Phase 7: 記事生成ワークフロー

- [x] 17. 記事生成プロンプトの実装
  - File: prompts/article_generation.md
  - ペルソナとリサーチデータを統合した記事生成プロンプト
  - ランキング記事の構造と品質基準
  - Purpose: Claude Codeで高品質なランキング記事を生成
  - _Leverage: templates/article/ranking_article.md_
  - _Requirements: 3. 調査結果参照型記事生成機能_

- [x] 18. コンテンツ最適化プロンプトの実装
  - File: prompts/content_optimization.md
  - 記事の読みやすさとSEO最適化プロンプト
  - ペルソナに響くトーンと表現の調整ガイド
  - Purpose: ターゲットユーザーに最適化された記事コンテンツを作成
  - _Requirements: 3. 調査結果参照型記事生成機能_

- [x] 19. アフィリエイトリンク挿入ガイドの作成
  - File: guides/affiliate_integration.md
  - 記事内での自然なアフィリエイトリンク配置方法
  - リンククリック率を高める記述テクニック
  - Purpose: 収益最大化を目指すアフィリエイト戦略を提供
  - _Requirements: 3. 調査結果参照型記事生成機能_

## Phase 8: 品質管理ワークフロー

- [x] 20. 品質チェックプロンプトの実装
  - File: prompts/quality_check.md
  - 記事の品質評価と改善提案生成プロンプト
  - 誤字脱字、文章構造、論理性のチェック項目
  - Purpose: Claude Codeで記事品質の自動評価と改善を実現
  - _Requirements: 4. 記事品質チェック・最適化機能_

- [x] 21. SEO最適化チェックリストの作成
  - File: checklists/seo_optimization.md
  - タイトル、見出し、キーワード配置の最適化項目
  - 検索エンジン対応のベストプラクティス
  - Purpose: 検索エンジンでの上位表示を支援
  - _Requirements: 4. 記事品質チェック・最適化機能_

- [x] 22. 記事最終化プロンプトの実装
  - File: prompts/article_finalization.md
  - 手動修正後の最終品質確認プロンプト
  - 公開準備チェックリストと改善提案
  - Purpose: 記事公開前の最終品質保証を実現
  - _Requirements: 4. 記事品質チェック・最適化機能_

## Phase 9: 統合ワークフローと最適化

- [x] 23. 統合ワークフローガイドの作成
  - File: docs/complete_workflow.md
  - ペルソナ作成から記事公開までの完全手順
  - 各フェーズでの成果物と品質基準
  - Purpose: システム全体の効率的な活用を支援
  - _Leverage: 全テンプレートとガイド_
  - _Requirements: 5. ワークフロー管理とプロジェクト追跡機能_

- [x] 24. トラブルシューティングガイドの作成
  - File: docs/troubleshooting.md
  - よくある問題と解決方法
  - エラー回復手順とデータ復旧方法
  - Purpose: 問題発生時の迅速な対応を支援
  - _Requirements: All エラーハンドリング_

- [x] 25. 効率化ツールセットの作成
  - File: tools/productivity_helpers.md
  - 繰り返し作業の自動化テンプレート
  - Claude Code活用のベストプラクティス集
  - Purpose: 長期運用での効率性と品質の向上を支援
  - _Requirements: 5. ワークフロー管理とプロジェクト追跡機能_

- [x] 26. 成果測定とKPIダッシュボードの構築
  - File: templates/analytics/performance_tracking.md
  - 記事作成数、品質スコア、収益予測の記録フォーマット
  - 継続的改善のためのデータ分析ガイド
  - Purpose: 月5万円目標達成に向けた進捗管理を実現
  - _Requirements: 5. ワークフロー管理とプロジェクト追跡機能_

## Phase 10: TDD実装フェーズ - Core Python Components

- [ ] 27. PA-APIクライアントのTDD実装 (RED)
  - File: tests/test_pa_api_client.py
  - PA-API認証、製品検索、レスポンス処理の失敗テスト作成
  - エラーハンドリング（認証失敗、レート制限、ネットワークエラー）のテスト
  - Purpose: PA-APIクライアントの仕様を明確化し、失敗ケースを定義
  - _TDD Phase: RED - Write failing tests first_
  - _Requirements: 2. DeepResearch実行と結果管理機能_

- [ ] 28. PA-APIクライアントのTDD実装 (GREEN)
  - File: tools/pa_api_client.py
  - テストを通過する最小限のPAAPIクライアント実装
  - boto3を使用したPA-API 5.0認証とリクエスト処理
  - Purpose: RED段階のテストを全て通過させる実装
  - _TDD Phase: GREEN - Make tests pass with minimal code_
  - _Leverage: tests/test_pa_api_client.py_
  - _Requirements: 2. DeepResearch実行と結果管理機能_

- [ ] 29. PA-APIクライアントのTDD実装 (REFACTOR)
  - File: tools/pa_api_client.py
  - コードの重複削除、設定ファイル連携、エラーメッセージ改善
  - パフォーマンス最適化、ログ追加、ドキュメンテーション
  - Purpose: テストを維持しながらコード品質を向上
  - _TDD Phase: REFACTOR - Improve code quality while keeping tests green_
  - _Leverage: tests/test_pa_api_client.py, config/settings.yaml_
  - _Requirements: 2. DeepResearch実行と結果管理機能_

## Phase 11: TDD実装フェーズ - Affiliate Link Generator

- [ ] 30. アフィリエイトリンク生成ツールのTDD実装 (RED)
  - File: tests/test_affiliate_link_generator.py
  - ASIN抽出、アフィリエイトリンク生成、記事内リンク置換の失敗テスト
  - マークダウン解析エラー、不正ASIN、設定ファイル読み込みエラーのテスト
  - Purpose: アフィリエイトリンク生成の仕様明確化と失敗ケース定義
  - _TDD Phase: RED - Write failing tests first_
  - _Requirements: 3. 調査結果参照型記事生成機能_

- [ ] 31. アフィリエイトリンク生成ツールのTDD実装 (GREEN)
  - File: tools/affiliate_link_generator_integrated.py
  - 失敗テストを通過する最小限の実装
  - ASIN正規表現抽出、URL生成、マークダウン置換機能
  - Purpose: RED段階のテストを全て通過させる実装
  - _TDD Phase: GREEN - Make tests pass with minimal code_
  - _Leverage: tests/test_affiliate_link_generator.py_
  - _Requirements: 3. 調査結果参照型記事生成機能_

- [ ] 32. アフィリエイトリンク生成ツールのTDD実装 (REFACTOR)
  - File: tools/affiliate_link_generator_integrated.py
  - コードの構造改善、設定ファイル統合、エラーハンドリング強化
  - CLI引数解析改善、プロジェクト構造対応強化
  - Purpose: テストを維持しながらコード品質とユーザビリティ向上
  - _TDD Phase: REFACTOR - Improve code quality while keeping tests green_
  - _Leverage: tests/test_affiliate_link_generator.py, config/settings.yaml_
  - _Requirements: 3. 調査結果参照型記事生成機能_

## Phase 12: TDD実装フェーズ - Article Converter

- [ ] 33. 記事変換ツールのTDD実装 (RED)
  - File: tests/test_note_article_converter.py
  - ノートから記事への変換、メタデータ抽出、フォーマット変換の失敗テスト
  - ファイル読み込みエラー、不正フォーマット、出力エラーのテスト
  - Purpose: 記事変換機能の仕様明確化と失敗ケース定義
  - _TDD Phase: RED - Write failing tests first_
  - _Requirements: 3. 調査結果参照型記事生成機能_

- [ ] 34. 記事変換ツールのTDD実装 (GREEN)
  - File: tools/note_article_converter.py
  - 失敗テストを通過する最小限の変換ロジック実装
  - マークダウン解析、メタデータ処理、記事フォーマット生成
  - Purpose: RED段階のテストを全て通過させる実装
  - _TDD Phase: GREEN - Make tests pass with minimal code_
  - _Leverage: tests/test_note_article_converter.py_
  - _Requirements: 3. 調査結果参照型記事生成機能_

- [ ] 35. 記事変換ツールのTDD実装 (REFACTOR)
  - File: tools/note_article_converter.py
  - 変換ロジックの最適化、エラーメッセージ改善、設定連携
  - テンプレート活用、拡張性向上、パフォーマンス最適化
  - Purpose: テストを維持しながらコード品質と機能性向上
  - _TDD Phase: REFACTOR - Improve code quality while keeping tests green_
  - _Leverage: tests/test_note_article_converter.py, templates/_
  - _Requirements: 3. 調査結果参照型記事生成機能_

## Phase 13: TDD実装フェーズ - Integration & Quality

- [ ] 36. 統合テストのTDD実装 (RED)
  - File: tests/test_integration_workflow.py
  - エンドツーエンドワークフローの失敗テスト作成
  - ペルソナ→リサーチ→記事生成の連携エラーテスト
  - Purpose: システム全体の統合品質を保証する仕様定義
  - _TDD Phase: RED - Write failing integration tests first_
  - _Requirements: 5. ワークフロー管理とプロジェクト追跡機能_

- [ ] 37. 統合テストのTDD実装 (GREEN)
  - File: main.py, tools/__init__.py
  - 統合テストを通過する最小限のワークフロー実装
  - 各コンポーネント間のデータフロー確立
  - Purpose: 統合テストを全て通過させるシステム連携
  - _TDD Phase: GREEN - Make integration tests pass_
  - _Leverage: tests/test_integration_workflow.py, all components_
  - _Requirements: All requirements integration_

- [ ] 38. 統合テストのTDD実装 (REFACTOR)
  - File: main.py, tools/__init__.py
  - ワークフロー最適化、エラー回復機能強化、ログ改善
  - 設定管理統一、パフォーマンス監視、保守性向上
  - Purpose: テストを維持しながらシステム全体の品質向上
  - _TDD Phase: REFACTOR - Improve system architecture while keeping tests green_
  - _Leverage: tests/test_integration_workflow.py, config/settings.yaml_
  - _Requirements: All requirements optimization_

## Phase 14: TDD品質保証とドキュメンテーション

- [ ] 39. TDD実装ドキュメントの作成
  - File: docs/tdd_implementation_guide.md
  - Red-Green-Refactorサイクルの実装記録と学習ポイント
  - 各コンポーネントのテスト戦略とカバレッジレポート
  - Purpose: TDD実装プロセスの記録と今後のメンテナンスガイド
  - _Requirements: Documentation for TDD process_

- [ ] 40. 継続的品質改善システムの構築
  - File: scripts/quality_check.py, .github/workflows/ci.yml
  - 自動テスト実行、コードカバレッジ測定、品質メトリクス監視
  - 継続的インテグレーション設定とTDD遵守チェック
  - Purpose: TDD原則の継続的な遵守と品質向上の自動化
  - _Requirements: Continuous quality improvement_