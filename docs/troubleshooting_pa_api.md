# PA-API サクラ検出システム トラブルシューティングガイド

## 一般的な問題と解決策

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

## パフォーマンス問題

### 1. 処理時間が長い

#### 症状
15商品の処理が20分を超える

#### 解決策

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

### 2. メモリ使用量が多い

#### 症状
メモリ使用量が500MBを超える

#### 解決策

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

## テスト関連問題

### 1. テストが失敗する

#### 症状
```bash
FAILED tests/test_pa_api_client.py::test_authentication
```

#### 解決策

1. **モック設定の確認**:
```python
# テスト用の環境変数設定
os.environ['AWS_ACCESS_KEY_ID'] = 'test-key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret'
```

2. **テストデータの更新**:
```python
# テスト用商品データが古い場合
test_products = generate_fresh_test_data()
```

### 2. カバレッジが低い

#### 症状
テストカバレッジが85%を下回る

#### 解決策

1. **未テストコードの特定**:
```bash
uv run pytest --cov=tools --cov-report=html
# htmlcov/index.html で詳細確認
```

2. **エラーハンドリングのテスト追加**:
```python
def test_error_handling():
    with pytest.raises(PAAPIAuthenticationError):
        # エラーケースのテスト
```

## 設定ファイル問題

### 1. YAML構文エラー

#### 症状
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

#### 解決策

1. **YAML構文チェック**:
```bash
python -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"
```

2. **インデントの確認**:
- スペース使用（タブ禁止）
- 一貫したインデント（2スペース推奨）

### 2. 必須設定の欠落

#### 症状
```
PAAPIConfigError: associate_tagが設定されていません
```

#### 解決策

**最小必須設定**:
```yaml
pa_api:
  associate_tag: "your-associate-tag"
  region: "us-east-1"
  requests_per_day: 8640
  timeout_seconds: 10
```

## ログとデバッグ

### ログレベルの調整

```python
import logging

# デバッグモード有効
logging.getLogger('tools.pa_api_client').setLevel(logging.DEBUG)
logging.getLogger('tools.sakura_detector').setLevel(logging.DEBUG)
```

### 詳細ログの確認

```bash
# 全ログを表示
python your_script.py --verbose

# 特定コンポーネントのログ
grep "PAAPIClient" logs/application.log
```

## よくある質問 (FAQ)

### Q1: どのPA-APIプランが必要ですか？
**A**: 基本プラン（無料）で開始可能。1日8640回のリクエスト制限があります。

### Q2: サクラ検出の精度はどの程度ですか？
**A**: 統計的手法により約85-90%の精度を達成。継続的な改善を実施中。

### Q3: システムの導入にかかる時間は？
**A**: 
- 基本設定: 15分
- テスト実行確認: 10分
- 本格運用開始: 30分程度

### Q4: 商用利用は可能ですか？
**A**: プライベート使用のみ。商用利用には別途ライセンス取得が必要。

## サポート

### コミュニティ
- GitHub Issues: バグレポートと機能要求
- Discussions: 一般的な質問と議論

### 緊急時対応
1. システム停止時: ログファイルを確認
2. データ損失時: バックアップからの復旧
3. セキュリティ問題: 直ちにシステム停止とレポート

### 品質監視
```bash
# 継続的品質チェック
python scripts/pa_api_quality_check.py --all

# CI/CDパイプライン確認
git push origin main  # GitHub Actionsで自動品質チェック
```