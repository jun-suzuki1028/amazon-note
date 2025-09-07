# Amazon アフィリエイトリンク自動生成ツール

このツールは記事内の製品名からAmazonアフィリエイトリンクを自動生成し、記事内の `<!-- AFFILIATE_LINK_X -->` マーカーを実際のリンクに置換します。

## 機能

- ✅ 記事内の製品名を自動検出
- ✅ Amazonアフィリエイトリンクを自動生成
- ✅ マーカー `<!-- AFFILIATE_LINK_X -->` を実際のリンクに置換
- ✅ 日本のAmazon.co.jpに対応
- ✅ ボタン形式の見栄えの良いリンク生成
- ✅ 設定ファイルによるアソシエイトID管理
- ✅ ドライランモードでの事前確認

## セットアップ

### 1. 初期設定

```bash
python tools/affiliate_link_generator.py --setup
```

AmazonアソシエイトIDを入力してください（例: `yourid-22`）

### 2. 必要なライブラリのインストール（必要に応じて）

```bash
# 基本的にはPython標準ライブラリのみを使用
# 実用化する際は以下のライブラリを追加することを推奨
pip install requests beautifulsoup4 boto3
```

## 使用方法

### 基本的な使用方法

```bash
python tools/affiliate_link_generator.py --article-path "projects/gaming-monitor-fighter-2025-01-07/articles/draft-001.md"
```

### オプション指定

```bash
# アソシエイトIDを個別指定
python tools/affiliate_link_generator.py --article-path "articles/draft.md" --associate-id "yourid-22"

# 出力ファイルを別途指定
python tools/affiliate_link_generator.py --article-path "articles/draft.md" --output "articles/final.md"

# ドライラン（実際の変更は行わず結果のみ表示）
python tools/affiliate_link_generator.py --article-path "articles/draft.md" --dry-run
```

## 記事の書き方

### 製品見出しの形式

```markdown
### 第1位：BenQ ZOWIE XL2411K
<!-- AFFILIATE_LINK_1 -->

### 第2位：I-O DATA GigaCrysta EX-LDGC242HTB  
<!-- AFFILIATE_LINK_2 -->
```

### 生成されるリンク例

```html
<div style="text-align: center; margin: 20px 0;">
    <a href="https://www.amazon.co.jp/dp/B08FJ7XQ5N?tag=yourid-22" target="_blank" rel="noopener" 
       style="display: inline-block; padding: 12px 24px; background-color: #ff9900; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
        🛒 BenQ ZOWIE XL2411KをAmazonで見る
    </a>
</div>
```

## 設定ファイル

アソシエイトIDは `~/.amazon_affiliate_config.json` に保存されます：

```json
{
  "associate_id": "yourid-22"
}
```

## 注意事項と制限

### 現在の実装について

1. **ASIN取得**: デモ用の実装では製品名からハッシュ値を生成してASINを作成しています
2. **検索機能**: 実際のAmazon APIは使用していません
3. **リンク検証**: 簡易的な検証のみ実装

### 実用化のために必要な改善

1. **Amazon PA API 5.0の統合**
   ```python
   # boto3を使用したPA API実装例
   import boto3
   from botocore.exceptions import ClientError
   
   client = boto3.client('paapi5')
   ```

2. **Web スクレイピングの実装**
   ```python
   # BeautifulSoupを使用した検索結果解析
   import requests
   from bs4 import BeautifulSoup
   ```

3. **リンクの有効性確認**
   ```python
   def verify_amazon_link(url):
       try:
           response = requests.head(url, timeout=5)
           return response.status_code == 200
       except:
           return False
   ```

## 実用化ロードマップ

### Phase 1: 基本機能（完了）
- ✅ 記事パース機能
- ✅ アフィリエイトリンク生成
- ✅ マーカー置換機能
- ✅ 設定管理

### Phase 2: 検索機能強化
- 🔄 Amazon PA API 5.0 統合
- 🔄 製品名の正規化処理
- 🔄 ブランド名の自動検出強化

### Phase 3: 高度な機能
- ⏳ 価格取得機能
- ⏳ レビュー数・評価取得
- ⏳ 在庫状況確認
- ⏳ 価格変動アラート

### Phase 4: 自動化・運用
- ⏳ バッチ処理機能
- ⏳ 定期的なリンク更新
- ⏳ 統計・レポート機能
- ⏳ Web UIの実装

## トラブルシューティング

### 製品が検出されない場合

1. 見出し形式を確認:
   ```markdown
   ### 第X位：製品名
   ```

2. 製品名にブランド名を含める:
   ```markdown
   ### 第1位：BenQ ZOWIE XL2411K  # ✅ Good
   ### 第1位：XL2411K              # ❌ Brand missing
   ```

### アソシエイトIDが保存されない場合

```bash
# 権限確認
ls -la ~/.amazon_affiliate_config.json

# 手動作成
echo '{"associate_id": "yourid-22"}' > ~/.amazon_affiliate_config.json
```

### リンクが生成されない場合

1. ドライランモードで確認:
   ```bash
   python tools/affiliate_link_generator.py --article-path "article.md" --dry-run
   ```

2. 製品名の確認:
   - 英数字のみで構成されているか
   - 特殊文字が含まれていないか
   - ブランド名が正しく認識されているか

## サンプル記事

`projects/gaming-monitor-fighter-2025-01-07/articles/draft-001.md` が実際の使用例として参考になります。

## 法的注意事項

1. **Amazonアソシエイトプログラムの規約遵守**
2. **適切な広告表示の明記**
3. **ユーザーに対する透明性の確保**

記事内に以下のような注記を含めることを推奨します：

```markdown
*この記事にはAmazonアフィリエイトリンクが含まれています。商品購入時に得られる収益は、より良いコンテンツ作成のために使用されます。*
```

## ライセンス

MIT License - 自由にご利用ください。