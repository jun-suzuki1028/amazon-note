# Requirements Document

## Introduction

PA-API実装とサクラ検出システムは、現在デモ実装となっているAmazon商品データ取得機能を実用化するための中核機能です。現状の偽造ASINとランダム生成データを、実際のAmazon PA-API 5.0からの実データ取得に置き換え、信頼性の高いサクラ検出システムを構築します。これにより、記事作成ワークフローの品質と実用性を大幅に向上させます。

## Alignment with Product Vision

このシステムは、「月5万円の収益を目指し、週5本の高品質なアフィリエイト記事を作成する」というプロジェクト目標の実現に不可欠です。実際の商品データと品質検証により、読者の信頼を得られる記事作成を可能にし、アフィリエイト収益の安定的な向上に貢献します。

## Requirements

### Requirement 1: 実際のAmazon商品データ取得

**User Story:** アフィリエイト記事作成者として、実在するAmazon商品の正確な情報（価格、レビュー数、評価、ASIN）を取得したい。そうすることで、信頼性の高い記事を作成し、読者に価値のある情報を提供できる。

#### Acceptance Criteria

1. WHEN 商品名とブランド名を入力 THEN システムは Amazon PA-API 5.0 を使用して実際のASINを取得 SHALL する
2. IF 検索結果が複数存在する場合 THEN システムは品質基準（レビュー数500件以上、評価4.0以上）に基づいて最適な商品を選択 SHALL する
3. WHEN ASIN取得後 THEN システムは価格、レビュー数、評価、画像URL、メーカー名の最新情報を取得 SHALL する
4. IF API制限に達した場合 THEN システムはエラーを発生させ、処理を中断 SHALL する

### Requirement 2: 基本品質フィルタリング

**User Story:** アフィリエイト記事作成者として、信頼性の低い商品を自動的に除外したい。そうすることで、読者に推奨しても問題のない商品のみを記事に含めることができる。

#### Acceptance Criteria

1. WHEN 商品情報を取得後 THEN システムはレビュー数200件未満の商品を除外 SHALL する
2. IF 商品の平均評価が4.0未満の場合 THEN システムは該当商品を除外対象として分類 SHALL する
3. WHEN 出品者情報を確認時 THEN システムはAmazon本体（MerchantId: AN1VRQENFRJN5）以外の商品を中華製品の可能性として識別 SHALL する
4. IF 設定で中華製品除外が有効な場合 THEN システムはマーケットプレイス商品を除外 SHALL する

### Requirement 3: サクラ検出システム

**User Story:** アフィリエイト記事作成者として、サクラレビューが疑われる商品を識別したい。そうすることで、読者に信頼性の高い商品のみを推奨でき、アフィリエイトサイトの信頼性を維持できる。

#### Acceptance Criteria

1. WHEN レビュー数と評価の組み合わせを分析時 THEN システムは統計的異常値（レビュー数が少ないのに評価が極めて高い等）を検出 SHALL する
2. IF サクラ疑惑スコアが設定値（30%）を超えた場合 THEN システムは該当商品を除外対象として分類 SHALL する
3. WHEN 複数の商品を比較分析時 THEN システムは同カテゴリ内での評価分布の偏りを検出 SHALL する
4. IF レビュー時系列データが利用可能な場合 THEN システムは短期間での急激なレビュー増加を異常として検出 SHALL する

### Requirement 4: サクラチェッカー自動化

**User Story:** アフィリエイト記事作成者として、サクラチェッカーでの手動確認作業（15商品60分）を自動化したい。そうすることで、作業時間を大幅に短縮し、より多くの商品を効率的にチェックできる。

#### Acceptance Criteria

1. WHEN 商品ASINのリストが提供された時 THEN システムはPlaywrightを使用してサクラチェッカーサイトにアクセス SHALL する
2. IF 複数商品の処理時 THEN システムは適切な間隔（3-5秒）を設けてアクセスし、サイトへの負荷を最小化 SHALL する
3. WHEN サクラチェッカーから結果取得時 THEN システムは結果を構造化データとして保存 SHALL する
4. IF 15商品のバッチ処理時 THEN システムは60分から20分への処理時間短縮を実現 SHALL する
5. IF サクラチェッカーサイトがアクセス不可能またはエラーの場合 THEN システムはエラーを発生させ、処理を中断 SHALL する

## Non-Functional Requirements

### Code Architecture and Modularity
- **Single Responsibility Principle**: PA-API操作、サクラ検出、データキャッシュを独立したモジュールに分離
- **Modular Design**: 各検出アルゴリズムを個別のクラスとして実装し、組み合わせ可能な設計
- **Dependency Management**: 外部API依存を抽象化し、モックテストを可能にする
- **Clear Interfaces**: データ取得、品質判定、結果出力の明確なインターフェース定義

### Performance
- PA-API呼び出し: 1商品あたり平均2秒以内のレスポンス
- バッチ処理: 15商品の処理を20分以内で完了
- キャッシュ効率: 同一商品の再取得時は500ms以内での応答
- メモリ使用量: 同時処理時でも500MB以内に制限

### Security
- API認証情報の環境変数による管理
- 外部サイトアクセス時のUser-Agent適切設定
- レート制限遵守によるサービス利用規約準拠
- 商品データの暗号化保存（個人情報含む場合）

### Reliability
- API呼び出し失敗時はエラーとして処理を中断
- システム障害時は明確なエラーメッセージで停止
- データ整合性チェック機能
- エラー発生時の詳細なログ出力

### Usability
- 進捗状況の視覚的表示
- エラー発生時の具体的なメッセージ表示
- システム停止時の明確な原因表示
- 設定変更のための分かりやすいインターフェース

### Technical Environment
- **Python Package Manager**: uvを使用した依存関係管理
- **Browser Automation**: Playwright for Pythonを使用
- **Python Version**: Python 3.9以上（uvでの管理）
- **Dependencies**: pyproject.tomlでの依存関係定義