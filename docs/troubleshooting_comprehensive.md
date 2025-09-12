# 包括的トラブルシューティングガイド

AI Amazon記事生成システムで発生する可能性のある問題と、その解決方法をまとめた統合ガイドです。汎用的な問題からPA-API特化の問題まで、すべてのトラブルシューティングを網羅しています。

---

## 📖 目次

1. [システム共通の問題](#システム共通の問題)
2. [PA-API特化の問題](#pa-api特化の問題)
3. [パフォーマンス問題の解決](#パフォーマンス問題の解決)
4. [データ復旧方法](#データ復旧方法)
5. [緊急時の対応手順](#緊急時の対応手順)
6. [予防保守とモニタリング](#予防保守とモニタリング)

---

## システム共通の問題

### 1. ペルソナ作成時の問題

#### 問題: ペルソナ情報が不完全
**症状**
- ペルソナプロフィールの重要項目が空欄
- 商品カテゴリとペルソナの不一致
- 矛盾する設定値

**解決方法**
```bash
# 1. ペルソナテンプレートを再読み込み
cat templates/persona/default_persona.md

# 2. Claude Codeで対話的にペルソナを再生成
# prompts/persona_creation.mdのフェーズ1から順番に実行

# 3. 検証チェックリストで確認
# checklists/persona_validation.mdを使用して品質確認
```

**予防策**
- ペルソナ作成時は必ず全フェーズを完了させる
- 作成後は必ず検証チェックリストを実行
- 定期的にペルソナの妥当性を見直す

#### 問題: ペルソナファイルが見つからない
**症状**
```
Error: Persona file not found at persona/[persona-name].md
```

**解決方法**
```bash
# 1. personaディレクトリの確認
ls -la persona/

# 2. ファイル名の確認（大文字小文字、スペース等）
find . -name "*persona*" -type f

# 3. 必要に応じて新規作成
mkdir -p persona
touch persona/target-persona.md
```

### 2. リサーチ実行時の問題

#### 問題: Gemini MCPのタイムアウト
**症状**
- リサーチが長時間応答なし
- "Request timeout"エラー
- 部分的な結果のみ取得

**解決方法**
```markdown
## 段階的リサーチ戦略

### Step 1: リサーチ範囲を縮小
- 商品数を50→10に削減
- 調査項目を必須項目のみに限定
- 時間範囲を直近3ヶ月に限定

### Step 2: 分割実行
```bash
# キーワードリサーチのみ実行
mcp__gemini-cli__ask-gemini --prompt "キーワードのみ調査"

# 商品調査を別途実行
mcp__gemini-cli__ask-gemini --prompt "商品10個の基本情報のみ"
```

### Step 3: 結果の統合
prompts/research_integration.mdを使用して結果を統合
```

#### 問題: リサーチ結果の品質が低い
**症状**
- 情報が古い
- 関連性の低い商品が含まれる
- 重要な情報が欠落

**解決方法**
```markdown
## 品質改善プロセス

### 1. プロンプトの最適化
- より具体的な条件を追加
- ペルソナ情報を明確に含める
- 出力形式を構造化

### 2. 追加リサーチの実施
```bash
# 不足情報を特定
prompts/research_integration.md の「情報補完プロンプト」を使用

# 追加調査を実行
mcp__gemini-cli__ask-gemini --prompt "[不足情報の具体的な調査]"
```

### 3. 手動での情報補完
- Amazon直接確認
- 公式サイト情報の追加
- レビューサイトからの補完
```

### 3. 記事生成時の問題

#### 問題: 生成された記事が長すぎる/短すぎる
**症状**
- 目標文字数から大幅に逸脱
- 冗長な説明の繰り返し
- 必要な情報の不足

**解決方法**
```markdown
## 文字数調整方法

### 長すぎる場合
1. prompts/content_optimization.mdで優先順位を設定
2. 各セクションに文字数制限を明記
3. 重複内容を削除

### 短すぎる場合
1. 不足セクションを特定
2. 以下を追加：
   - 詳細な商品説明
   - ユーザーレビューの引用
   - FAQ セクション
   - 使用例・活用方法
```

#### 問題: SEOスコアが低い
**症状**
- キーワード密度が不適切
- メタデータが未設定
- 見出し構造が不適切

**解決方法**
```bash
# キーワード密度の調整
- メインキーワード: 1-2%に調整
- 自然な文脈で配置

# メタデータの設定
prompts/article_finalization.md の「メタデータ最適化」を実行

# 見出し構造の修正
- H1: 1個のみ
- H2-H3: 階層構造を整理
```

### 4. Claude Code関連エラー

#### Error: "Context length exceeded"
**原因**: 入力データが長すぎる

**対処法**:
```bash
# 1. データを分割
# 記事を3000文字ごとに分割して処理

# 2. --uc フラグを使用
# prompts/content_optimization.md --uc

# 3. 不要な情報を削除
# リサーチ結果から重複を除去
```

#### Error: "Invalid prompt format"
**原因**: プロンプトの構造が不正

**対処法**:
```markdown
## 正しいプロンプト構造

### 必須要素
1. 【入力データ】セクション
2. 【要求事項】セクション
3. 【出力形式】セクション

### 修正例
```
【入力データ】
[データをここに]

【要求事項】
[具体的な指示]

【出力形式】
[期待する出力形式]
```
```

---

## PA-API特化の問題

### 1. 認証エラー

#### 症状
```
PAAPIAuthenticationError: access_keyが設定されていません
```

#### 原因と解決策

**原因**: PA-API認証情報が正しく設定されていない

**解決策**:
1. 環境変数を確認：
```bash
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

2. 環境変数が設定されていない場合：
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

3. config/settings.yamlを確認：
```yaml
pa_api:
  associate_tag: "your-associate-tag"
  # access_key と secret_key は環境変数推奨
```

### 2. レート制限エラー

#### 症状
```
PAAPIRateLimitError: レート制限エラー: Request throttled
```

#### 原因と解決策

**原因**: PA-APIの呼び出し制限に達した

**解決策**:
1. 待機してからリトライ（システムは自動リトライを実装済み）
2. requests_per_dayの設定を確認：
```yaml
pa_api:
  requests_per_day: 8640  # 調整可能
  retry_attempts: 3       # リトライ回数
  retry_delay: 1.0        # リトライ間隔（秒）
```

### 3. ネットワークエラー

#### 症状
```
PAAPINetworkError: ネットワークエラー: Unable to locate credentials
```

#### 原因と解決策

**原因**: ネットワーク接続またはAWS認証情報の問題

**解決策**:
1. インターネット接続を確認
2. AWS認証情報を再設定
3. プロキシ設定がある場合は環境変数設定：
```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
```

### 4. Playwright関連エラー

#### 症状
```
playwright._impl._api_types.Error: Browser closed
```

#### 原因と解決策

**原因**: Playwrightブラウザの初期化または操作エラー

**解決策**:
1. Playwrightブラウザを再インストール：
```bash
uv run playwright install --with-deps chromium
```

2. 権限問題の場合：
```bash
sudo apt-get update
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
```

### 5. サクラ検出エラー

#### 症状
```
ValueError: 統計計算でエラーが発生しました
```

#### 原因と解決策

**原因**: 商品データが不足またはフォーマット異常

**解決策**:
1. 商品データの最小要件確認：
   - レビュー数: 10件以上
   - 評価値: 1.0-5.0の範囲
2. データ前処理で異常値を除外
3. ログで詳細エラー内容を確認：
```bash
tail -f logs/sakura_detector.log
```

### 6. テスト関連問題

#### 症状
```bash
FAILED tests/test_pa_api_client.py::test_authentication
```

#### 解決策

**モック設定の確認**:
```python
# テスト用の環境変数設定
os.environ['AWS_ACCESS_KEY_ID'] = 'test-key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret'
```

**テストデータの更新**:
```python
# テスト用商品データが古い場合
test_products = generate_fresh_test_data()
```

### 7. 設定ファイル問題

#### 症状
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

#### 解決策

**YAML構文チェック**:
```bash
python -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"
```

**インデントの確認**:
- スペース使用（タブ禁止）
- 一貫したインデント（2スペース推奨）

---

## パフォーマンス問題の解決

### 処理速度の改善

#### 問題: リサーチに時間がかかりすぎる
**最適化方法**:

**1. 並列処理の活用**
```python
# 直列処理（遅い）
const result1 = await research1();
const result2 = await research2();
const result3 = await research3();

# 並列処理（速い）
const [result1, result2, result3] = await Promise.all([
  research1(),
  research2(),
  research3()
]);
```

**2. キャッシュの活用**
```python
cache_enabled = True
cache_ttl = 3600  # 1時間
```

**3. PA-API専用最適化**
```python
# バッチサイズを調整
batch_size = 5  # デフォルト値、環境に応じて調整
```

#### 問題: 15商品の処理が20分を超える
**解決策**

1. **並列処理の最適化**:
```python
# バッチサイズを調整
batch_size = 5  # デフォルト値、環境に応じて調整
```

2. **キャッシュの活用**:
```python
# キャッシュ設定確認
cache_enabled = True
cache_ttl = 3600  # 1時間
```

3. **リソース使用量の監視**:
```bash
python scripts/pa_api_quality_check.py --performance
```

### メモリ使用量の削減

#### 症状: メモリ使用量が500MBを超える

**解決策**

1. **バッチ処理サイズを削減**:
```python
MAX_BATCH_SIZE = 3  # デフォルト5から削減
```

2. **不要なデータの削除**:
```python
# 生データのクリーンアップを頻繁に実行
del raw_data_cache
gc.collect()
```

#### 大量データ処理時の対策
```javascript
// ストリーミング処理の実装
const stream = fs.createReadStream('large-file.json');
const parser = JSONStream.parse('*');

stream.pipe(parser)
  .on('data', (item) => {
    // 各アイテムを個別に処理
    processItem(item);
  })
  .on('end', () => {
    console.log('Processing complete');
  });
```

---

## データ復旧方法

### 作業データのバックアップと復元

#### 自動バックアップの設定
```bash
# バックアップディレクトリ作成
mkdir -p backups/$(date +%Y%m%d)

# 重要ファイルのバックアップスクリプト
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# ペルソナデータ
cp -r persona/ $BACKUP_DIR/
# リサーチ結果
cp -r research/ $BACKUP_DIR/
# 生成済み記事
cp -r articles/ $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh
```

#### データ復旧手順
```bash
# 1. 最新のバックアップを確認
ls -la backups/

# 2. 復旧するバックアップを選択
BACKUP_DATE="20240912_120000"

# 3. データを復元
cp -r backups/$BACKUP_DATE/persona/* persona/
cp -r backups/$BACKUP_DATE/research/* research/
cp -r backups/$BACKUP_DATE/articles/* articles/

# 4. 整合性確認
find . -name "*.md" -type f | head -10 | xargs -I {} head -1 {}
```

### 部分的なデータ損失への対処

#### リサーチ結果の部分復旧
```bash
# 1. 残存データの確認
find research/ -name "*.json" -mtime -7

# 2. 不足データの特定
python -c "
import json
from pathlib import Path

required_fields = ['products', 'keywords', 'competitors', 'trends']
data_file = Path('research/data.json')

if data_file.exists():
    existing_data = json.loads(data_file.read_text())
    missing_fields = [field for field in required_fields if field not in existing_data]
    print('Missing fields:', missing_fields)
else:
    print('No data file found')
"

# 3. 部分的な再生成
# 不足フィールドのみを再調査して統合
```

---

## 緊急時の対応手順

### システム停止時の対応

#### 完全停止からの復旧
**Step 1: 状態確認（5分以内）**
```bash
# プロセス確認
ps aux | grep python

# ログ確認
tail -100 logs/error.log

# ディスク容量確認
df -h
```

**Step 2: 基本復旧（10分以内）**
```bash
# キャッシュクリア
rm -rf .cache/

# 一時ファイル削除
rm -rf /tmp/amazon-*

# システム再起動（該当する場合）
# 手動プロセスなので、通常は必要なし
```

**Step 3: データ整合性確認（15分以内）**
```bash
# ファイル整合性チェック
find . -name "*.md" -size 0

# JSONバリデーション
for file in research/*.json; do
  python -m json.tool "$file" > /dev/null || echo "Invalid: $file"
done
```

### データ消失時の対応

#### 復旧優先順位
**Priority 1: ペルソナデータ**
- 最重要：作業の基盤
- バックアップから復元
- なければ再作成（3-5分）

**Priority 2: リサーチ結果**
- 重要：時間のかかる作業
- 部分データから再構築
- 必要最小限の再調査（30-45分）

**Priority 3: 生成記事**
- 中程度：再生成可能
- ドラフトから復元
- 最悪再生成（10-15分）

**Priority 4: 設定・テンプレート**
- 低：gitから復元可能

### サポート連絡先

#### エスカレーション手順

**Level 1: 自己解決（30分以内）**
- このガイドを確認
- ログを確認
- 基本的なトラブルシューティング

**Level 2: コミュニティサポート**
- GitHub Issues で検索
- 類似の問題を探す
- 新規Issue作成

**Level 3: 緊急サポート**
- 重大なデータ損失
- システム完全停止
- セキュリティ問題

---

## 予防保守とモニタリング

### 定期メンテナンス

#### 週次チェックリスト
```markdown
## 週次メンテナンス項目

- [ ] バックアップの実行と確認
- [ ] ログファイルのローテーション
- [ ] キャッシュのクリーンアップ
- [ ] 不要ファイルの削除
- [ ] パフォーマンス指標の確認
- [ ] PA-API実装状況の確認（該当する場合）
```

#### 月次チェックリスト
```markdown
## 月次メンテナンス項目

- [ ] システム全体のバックアップ
- [ ] 依存関係の更新確認
- [ ] セキュリティパッチの適用
- [ ] ドキュメントの更新
- [ ] 使用統計の分析
- [ ] PA-API制限状況の確認（該当する場合）
```

### モニタリング設定

#### ログ監視
```bash
# エラーログの監視設定
tail -f logs/error.log | grep -E "ERROR|CRITICAL" | while read line; do
  echo "$(date): $line" >> logs/critical.log
  # アラート送信（必要に応じて）
done
```

#### パフォーマンス監視
```python
# 実行時間の計測
import time
start_time = time.time()
# 処理実行
elapsed_time = time.time() - start_time
print(f'処理時間: {elapsed_time:.2f}秒')

# メモリ使用量の監視（Python）
import psutil
import os

process = psutil.Process(os.getpid())
memory_usage = process.memory_info().rss / 1024 / 1024  # MB
print(f'メモリ使用量: {memory_usage:.2f}MB')
```

#### PA-API専用監視
```bash
# 継続的品質チェック（実装時）
python scripts/pa_api_quality_check.py --all

# システム診断
python -c "
import os
from pathlib import Path

print('=== PA-API実装システム診断 ===')
print(f'AWS_ACCESS_KEY_ID: {"✓" if os.environ.get("AWS_ACCESS_KEY_ID") else "✗"}')
print(f'AWS_SECRET_ACCESS_KEY: {"✓" if os.environ.get("AWS_SECRET_ACCESS_KEY") else "✗"}')
print(f'settings.yaml: {"✓" if Path("config/settings.yaml").exists() else "✗"}')
"
```

### ログとデバッグ

#### ログレベルの調整
```python
import logging

# デバッグモード有効
logging.getLogger('tools.pa_api_client').setLevel(logging.DEBUG)
logging.getLogger('tools.sakura_detector').setLevel(logging.DEBUG)
```

#### 詳細ログの確認
```bash
# 全ログを表示
python your_script.py --verbose

# 特定コンポーネントのログ
grep "PAAPIClient" logs/application.log
```

---

## よくある質問 (FAQ)

### システム共通

**Q: 記事作成にどのくらいの時間がかかりますか？**
**A**: 現実的には90-120分です。品質を保ちながらこの時間で作成できます。

**Q: どのツールが必要ですか？**
**A**: Claude Code（必須）、サクラチェッカー（手動確認）、Gemini MCP（推奨）

### PA-API関連

**Q: どのPA-APIプランが必要ですか？**
**A**: 基本プラン（無料）で開始可能。1日8640回のリクエスト制限があります。

**Q: サクラ検出の精度はどの程度ですか？**
**A**: 統計的手法により約85-90%の精度を達成。継続的な改善を実施中。

**Q: システムの導入にかかる時間は？**
**A**: 
- 基本設定: 15分
- テスト実行確認: 10分
- 本格運用開始: 30分程度

**Q: 商用利用は可能ですか？**
**A**: プライベート使用のみ。商用利用には別途ライセンス取得が必要。

---

## まとめ

このトラブルシューティングガイドを参考に、問題が発生した際は落ち着いて対処してください。多くの問題は基本的な手順で解決可能です。解決できない場合は、エスカレーション手順に従ってサポートを受けてください。

**重要なポイント**:
- 定期的なバックアップの実行
- ログの継続的な監視
- 予防保守の徹底
- データ信頼性の確保
- 現実的な時間設定での運用