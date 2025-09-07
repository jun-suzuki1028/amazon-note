# AI Amazon Article Generator

AIを活用したAmazonランキング記事量産システム。Claude Codeを中心とした効率的なワークフローで、ペルソナ作成からDeepResearchプロンプト生成、調査結果管理、記事作成まで一連の流れを自動化します。

## 概要

本システムは以下の目標達成を支援します：
- **収益目標**: 月5万円のアフィリエイト収益
- **記事本数**: 週5本の高品質ランキング記事作成
- **差別化**: サクラチェッカー + レビュー数による信頼性の向上
- **効率化**: Claude Code中心のワークフロー自動化

### 🆕 PA-APIサクラ検出システム

Amazon Product Advertising API 5.0と高度なサクラレビュー検出機能を統合：
- **自動商品取得**: PA-API経由での高品質商品データ取得
- **サクラ検出**: 統計的異常値検出によるサクラレビュー識別
- **自動化**: Playwright使用のサクラチェッカー連携
- **品質保証**: TDD実装による高信頼性システム

## プロジェクト構造

```
amazon-note-rank/
├── projects/                 # プロジェクト管理
│   └── {project-id}/        # 個別プロジェクト
│       ├── persona/         # ペルソナデータ
│       ├── prompts/         # DeepResearchプロンプト
│       ├── research/        # リサーチ結果
│       ├── articles/        # 生成記事
│       └── meta/           # プロジェクトメタデータ
├── templates/               # 各種テンプレート
│   ├── persona/            # ペルソナテンプレート
│   ├── prompts/            # プロンプトテンプレート
│   ├── research/           # リサーチテンプレート
│   ├── article/            # 記事テンプレート
│   ├── project/            # プロジェクト管理テンプレート
│   └── analytics/          # 分析テンプレート
├── prompts/                # Claude Code用プロンプト
├── checklists/             # 品質チェックリスト
├── guides/                 # 操作ガイド
├── workflows/              # ワークフロー定義
├── tools/                  # 効率化ツール
├── docs/                   # ドキュメント
└── config/                 # 設定ファイル
```

## ワークフロー概要

1. **ペルソナ作成**: Claude Codeでターゲット読者のペルソナを作成
2. **プロンプト生成**: ペルソナを基にDeepResearchプロンプトを生成  
3. **リサーチ実行**: Gemini MCP/手動でDeepResearchを実行
4. **記事生成**: リサーチデータを参照してClaude Codeで記事生成
5. **品質チェック**: Claude Codeで品質確認と最適化

## セットアップ

1. プロジェクトをクローン
2. 設定ファイルを編集（config/settings.yaml）
3. テンプレートを確認・カスタマイズ
4. ワークフローガイドに従って記事作成開始

## 使用方法

### 基本ワークフロー
詳細な使用方法は `docs/complete_workflow.md` を参照してください。

### PA-APIサクラ検出システム

#### 1. 環境設定
```bash
# 環境変数設定（推奨）
export AWS_ACCESS_KEY_ID="your-pa-api-access-key"
export AWS_SECRET_ACCESS_KEY="your-pa-api-secret-key"

# または config/settings.yaml で設定
```

#### 2. システム実行
```bash
# 基本使用例
python tools/affiliate_link_generator_integrated.py --project-id "gaming-monitor-2025"

# テスト実行
uv run pytest tests/ -v

# 品質チェック
python scripts/pa_api_quality_check.py --all
```

#### 3. パフォーマンス要件
- **処理能力**: 15商品を20分以内で処理
- **品質基準**: レビュー数500件以上、評価4.0以上
- **サクラ検出**: 30%閾値でのサクラ度判定

## 特徴

### 記事作成システム
- **Claude Code中心**: 全工程でClaude Codeが核となる処理
- **テンプレートベース**: 標準化されたテンプレートで一貫した品質
- **対話型ワークフロー**: Claude Codeとの対話で効率的な作業
- **品質保証**: 各フェーズでの品質チェックとエラー復旧
- **柔軟性**: Gemini MCP利用可/不可両対応

### PA-APIサクラ検出システム
- **TDD実装**: Red-Green-Refactorサイクルによる高品質実装
- **統合API**: Amazon PA-API 5.0による公式商品データ取得
- **AI検出**: 機械学習ベースのサクラレビュー検出アルゴリズム
- **自動化**: Playwright使用のブラウザ自動化によるサクラチェッカー連携
- **CI/CD**: GitHub Actionsによる継続的品質管理
- **セキュリティ**: 環境変数管理による認証情報の安全な取り扱い

## ライセンス

Private Use Only