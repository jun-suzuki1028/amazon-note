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

## 🚀 クイックスタート

```bash
# 1. リポジトリのクローン
git clone <repository-url>
cd amazon-note-rank

# 2. 依存関係のインストール (UV使用)
uv sync

# 3. 環境設定 (推奨方法)
export AWS_ACCESS_KEY_ID="your-pa-api-access-key"
export AWS_SECRET_ACCESS_KEY="your-pa-api-secret-key"

# 4. 設定ファイル編集
cp config/settings.yaml.example config/settings.yaml
# アフィリエイトIDを設定

# 5. テスト実行
uv run pytest tests/ -v

# 6. サンプル記事の作成
uv run python3 tools/affiliate_link_generator_integrated.py --project-id "gaming-monitor-fighter-2025-01-07"
```

## プロジェクト構造

```
amazon-note-rank/
├── 📁 projects/                     # プロジェクト管理
│   └── {project-id}/               # 個別プロジェクト
│       ├── persona/                # ペルソナデータ
│       ├── prompts/                # DeepResearchプロンプト
│       ├── research/               # リサーチ結果
│       ├── articles/               # 生成記事
│       └── meta/                   # プロジェクトメタデータ (project.yaml)
│
├── 🛠️ tools/                       # コアツール群
│   ├── affiliate_link_generator_integrated.py  # アフィリエイトリンク統合生成
│   ├── pa_api_client.py            # Amazon PA-API 5.0 クライアント
│   ├── sakura_detector.py          # サクラレビュー検出システム
│   ├── playwright_automation.py    # ブラウザ自動化
│   └── note_article_converter.py   # note記事変換ツール
│
├── 📝 templates/                    # 各種テンプレート
│   ├── persona/                    # ペルソナテンプレート
│   ├── prompts/                    # プロンプトテンプレート
│   ├── research/                   # リサーチテンプレート
│   ├── article/                    # 記事テンプレート
│   ├── project/                    # プロジェクト管理テンプレート
│   ├── analytics/                  # 分析テンプレート
│   └── character/                  # AIキャラクター設定
│
├── 📚 docs/                        # ドキュメント
│   ├── complete_workflow.md        # 完全ワークフローガイド
│   ├── PA-API.md                   # PA-API仕様書
│   ├── tdd_implementation_pa_api.md # TDD実装ガイド
│   └── troubleshooting.md          # トラブルシューティング
│
├── ✅ tests/                       # テストスイート
│   └── test_pa_api_client.py       # PA-APIクライアントテスト
│
├── ⚙️ config/                      # 設定管理
│   └── settings.yaml               # メイン設定ファイル
│
├── 📋 checklists/                  # 品質チェックリスト
├── 🔧 workflows/                   # ワークフロー定義
├── 📖 guides/                      # 操作ガイド
└── 🚀 scripts/                     # 自動化スクリプト
```

### 💾 実際のプロジェクト例

現在のシステムで管理されているプロジェクト：

```
projects/
├── gaming-monitor-fighter-2025-01-07/    # 格闘ゲーム用モニターランキング
│   ├── articles/final-integrated-with-affiliate.md
│   ├── research/gemini.md, perplexity.md, chatgpt.md
│   └── persona/persona-001.md
│
└── gaming-keyboard-2025-09-07/           # ゲーミングキーボード比較
    ├── articles/final-note-article.md
    ├── research/キーボード製品比較レポート作成_.md
    └── persona/persona-001.md
```

## 🔄 5フェーズワークフロー

### Phase 1: ペルソナ作成 (30-45分)
```bash
# templates/persona/default_persona.md を基に実行
# Claude Codeでターゲット読者の詳細ペルソナを作成
```

### Phase 2: プロンプト生成 (20-30分)  
```bash
# templates/prompts/research_prompts.md を使用
# ペルソナを基にGemini MCP最適化されたDeepResearchプロンプトを生成
```

### Phase 3: DeepResearch実行 (5分)
```bash
# Perplexity.ai使用（推奨）
# リアルタイムWeb検索による最新情報取得
# templates/prompts/perplexity_research.md のプロンプト使用
```

### Phase 4: 記事生成 (45-60分)
```bash
# templates/article/ranking_article.md テンプレート使用
# リサーチデータを参照してClaude Codeで高品質記事生成
```

### Phase 5: 品質チェック & アフィリエイトリンク統合 (30-45分)
```bash
# 品質チェックリストによる最終確認
uv run python3 tools/affiliate_link_generator_integrated.py --project-id "your-project-id"
```

## 📋 使用方法

### 基本ワークフロー
詳細な使用方法は `docs/complete_workflow.md` を参照してください。

### 🛠️ コアツール群

#### 1. アフィリエイトリンク統合生成ツール
```bash
# 基本実行（プロジェクトID指定）
uv run python3 tools/affiliate_link_generator_integrated.py --project-id "gaming-monitor-fighter-2025-01-07"

# 特定記事のリンク生成
uv run python3 tools/affiliate_link_generator_integrated.py --article-path "projects/project-id/articles/draft.md"

# ドライラン（変更前に確認）
uv run python3 tools/affiliate_link_generator_integrated.py --project-id "your-project-id" --dry-run
```

#### 2. PA-APIクライアント & サクラ検出システム
```bash
# PA-APIクライアントのテスト
uv run pytest tests/test_pa_api_client.py -v

# サクラ検出機能の実行
python3 tools/sakura_detector.py --asin "B08FJ7XQ5N" --threshold 0.3
```

#### 3. ブラウザ自動化（Playwright）
```bash
# サクラチェッカー自動実行
python3 tools/playwright_automation.py --url "https://sakura-checker.jp/search/B08FJ7XQ5N"
```

### 🔧 環境設定

#### セキュリティ重要: 環境変数での認証情報管理
```bash
# 推奨方法: 環境変数設定
export AWS_ACCESS_KEY_ID="your-pa-api-access-key"
export AWS_SECRET_ACCESS_KEY="your-pa-api-secret-key"

# .bashrc または .zshrc に追記して永続化
echo 'export AWS_ACCESS_KEY_ID="your-key"' >> ~/.bashrc
echo 'export AWS_SECRET_ACCESS_KEY="your-secret"' >> ~/.bashrc
source ~/.bashrc
```

#### ⚠️ セキュリティ改善が必要
現在の `config/settings.yaml` にはハードコードされた認証情報が含まれています。本格運用前に以下の対応が必要です：

```bash
# 1. 機密情報の環境変数移行
mv config/settings.yaml config/settings.yaml.backup

# 2. 設定テンプレートの作成
cp config/settings.yaml config/settings.yaml.example
# settings.yaml.example から機密情報を削除

# 3. .gitignore の確認
echo "config/settings.yaml" >> .gitignore
echo "config/settings.local.yaml" >> .gitignore
```

### 📊 パフォーマンス指標

- **処理能力**: 15商品を20分以内で処理
- **品質基準**: レビュー数500件以上、評価4.0以上  
- **サクラ検出**: 30%閾値でのサクラ度判定
- **記事品質**: 80点以上の品質スコア目標
- **収益目標**: 月50,000円のアフィリエイト収益

## ✨ 特徴

### 🎯 記事作成システム
- **Claude Code中心**: 全工程でClaude Codeが核となる効率的処理
- **テンプレートベース**: 標準化されたテンプレートで一貫した高品質記事
- **対話型ワークフロー**: Claude Codeとの対話による効率的作業フロー
- **品質保証**: 各フェーズでの厳格な品質チェックとエラー復旧機能
- **柔軟性**: Gemini MCP利用可/不可両対応の柔軟な運用体制

### 🔍 PA-APIサクラ検出システム
- **TDD実装**: Red-Green-Refactorサイクルによる高信頼性システム
- **統合API**: Amazon PA-API 5.0による公式データ取得と処理
- **統計分析**: 統計的異常値検出によるサクラレビューの識別
- **自動化**: Playwright使用の完全自動ブラウザ操作
- **CI/CD対応**: GitHub Actionsによる継続的品質管理と自動テスト
- **セキュリティ**: 環境変数管理による認証情報の安全な取り扱い

### 🛠️ 技術スタック

**コア技術**:
- Python 3.12+ (uv パッケージ管理)
- Amazon PA-API 5.0 (boto3)
- Playwright (ブラウザ自動化)
- pytest (TDD実装)

**依存関係**:
```toml
dependencies = [
    "boto3>=1.40.25",           # AWS SDK, PA-API
    "numpy>=2.3.2",             # 数値計算
    "pandas>=2.3.2",            # データ処理 
    "playwright>=1.55.0",       # ブラウザ自動化
    "python-amazon-paapi>=5.0.1", # PA-API専用クライアント
    "pyyaml>=6.0.2",           # 設定ファイル管理
    "scipy>=1.16.1",           # 統計分析（サクラ検出）
]
```

## 📚 関連ドキュメント

- [`docs/complete_workflow.md`](docs/complete_workflow.md) - 完全ワークフローガイド
- [`docs/PA-API.md`](docs/PA-API.md) - PA-API仕様とトラブルシューティング  
- [`docs/tdd_implementation_pa_api.md`](docs/tdd_implementation_pa_api.md) - TDD実装ガイド
- [`tools/README.md`](tools/README.md) - ツール詳細仕様

## 🚨 重要な注意事項

### セキュリティ
現在の `config/settings.yaml` には認証情報がハードコードされています。**本格運用前に環境変数管理への移行が必須**です。

### 記事作成時の正確性原則
- **調査レポート記載情報のみ使用** - 調査レポート外の情報は絶対に含めない
- **すべての情報に根拠が必要** - 推測や憶測は一切禁止
- **不確実な情報の排除** - 確認できない情報は含めない

## 📄 ライセンス

Private Use Only