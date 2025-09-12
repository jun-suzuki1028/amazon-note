# トラブルシューティングガイド

AI Amazon記事生成システムで発生する可能性のある問題と、その解決方法をまとめたガイドです。

## 目次

1. [よくある問題と解決方法](#よくある問題と解決方法)
2. [エラーメッセージ別対処法](#エラーメッセージ別対処法)
3. [データ復旧方法](#データ復旧方法)
4. [パフォーマンス問題の解決](#パフォーマンス問題の解決)
5. [緊急時の対応手順](#緊急時の対応手順)

---

## よくある問題と解決方法

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

**エラー回避設定**
```javascript
// タイムアウト設定の調整
const geminiConfig = {
  timeout: 60000,  // 60秒に延長
  maxRetries: 3,   // リトライ回数
  retryDelay: 5000 // リトライ間隔
};
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
guides/prompt_optimization.mdを参照して：
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
```markdown
## SEO最適化手順

### 1. 品質チェック実行
prompts/quality_check.md の「SEO品質チェック」を実行

### 2. 問題箇所の修正
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

### 3. 再チェック
修正後、再度品質チェックを実行
```

---

## エラーメッセージ別対処法

### Claude Code関連エラー

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

### API/外部サービスエラー

#### Error: "Amazon API rate limit exceeded"
**原因**: API呼び出し回数の上限超過

**対処法**:
```javascript
// レート制限対策
const rateLimiter = {
  requestsPerMinute: 10,
  retryAfter: 60000, // 1分待機
  
  async executeWithLimit(request) {
    try {
      return await request();
    } catch (error) {
      if (error.code === 'RATE_LIMIT') {
        await sleep(this.retryAfter);
        return await request();
      }
      throw error;
    }
  }
};
```

#### Error: "Network connection failed"
**原因**: ネットワーク接続の問題

**対処法**:
```bash
# 1. ネットワーク状態確認
ping amazon.co.jp

# 2. プロキシ設定確認
echo $HTTP_PROXY
echo $HTTPS_PROXY

# 3. DNSキャッシュクリア
# Windows
ipconfig /flushdns
# Mac/Linux
sudo dscacheutil -flushcache
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
BACKUP_DATE="20240906_120000"

# 3. データを復元
cp -r backups/$BACKUP_DATE/persona/* persona/
cp -r backups/$BACKUP_DATE/research/* research/
cp -r backups/$BACKUP_DATE/articles/* articles/

# 4. 整合性確認
find . -name "*.md" -type f | head -10 | xargs -I {} head -1 {}
```

### 部分的なデータ損失への対処

#### リサーチ結果の部分復旧
```markdown
## 復旧可能なデータの特定

### 1. 残存データの確認
```bash
find research/ -name "*.json" -mtime -7
```

### 2. 不足データの特定
```javascript
const requiredFields = [
  'products', 'keywords', 'competitors', 'trends'
];

const existingData = JSON.parse(fs.readFileSync('research/data.json'));
const missingFields = requiredFields.filter(field => !existingData[field]);
console.log('Missing fields:', missingFields);
```

### 3. 部分的な再生成
不足フィールドのみを再調査して統合
```

---

## パフォーマンス問題の解決

### 処理速度の改善

#### 問題: リサーチに時間がかかりすぎる
**最適化方法**:
```markdown
## パフォーマンス改善策

### 1. 並列処理の活用
```javascript
// 直列処理（遅い）
const result1 = await research1();
const result2 = await research2();
const result3 = await research3();

// 並列処理（速い）
const [result1, result2, result3] = await Promise.all([
  research1(),
  research2(),
  research3()
]);
```

### 2. キャッシュの活用
```javascript
const cache = new Map();

async function getCachedResearch(key) {
  if (cache.has(key)) {
    return cache.get(key);
  }
  const result = await performResearch(key);
  cache.set(key, result);
  return result;
}
```

### 3. 不要な処理の削減
- 重複チェックの実装
- 既存データの再利用
- 条件付き処理の追加
```

### メモリ使用量の削減

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

## 緊急時の対応手順

### システム停止時の対応

#### 完全停止からの復旧
```markdown
## 緊急復旧手順

### Step 1: 状態確認（5分以内）
```bash
# プロセス確認
ps aux | grep node
# ログ確認
tail -100 error.log
# ディスク容量確認
df -h
```

### Step 2: 基本復旧（10分以内）
```bash
# キャッシュクリア
rm -rf .cache/
# 一時ファイル削除
rm -rf /tmp/amazon-*
# サービス再起動
npm restart
```

### Step 3: データ整合性確認（15分以内）
```bash
# ファイル整合性チェック
find . -name "*.md" -size 0
# JSONバリデーション
for file in research/*.json; do
  python -m json.tool "$file" > /dev/null || echo "Invalid: $file"
done
```
```

### データ消失時の対応

#### 優先順位に基づく復旧
```markdown
## 復旧優先順位

### Priority 1: ペルソナデータ
- 最重要：作業の基盤
- バックアップから復元
- なければ再作成（1-2時間）

### Priority 2: リサーチ結果
- 重要：時間のかかる作業
- 部分データから再構築
- 必要最小限の再調査（2-3時間）

### Priority 3: 生成記事
- 中程度：再生成可能
- ドラフトから復元
- 最悪再生成（1時間）

### Priority 4: 設定・テンプレート
- 低：gitから復元可能
```

### サポート連絡先

#### 技術サポート
```markdown
## エスカレーション手順

### Level 1: 自己解決（30分以内）
- このガイドを確認
- ログを確認
- 基本的なトラブルシューティング

### Level 2: コミュニティサポート
- GitHub Issues で検索
- 類似の問題を探す
- 新規Issue作成

### Level 3: 緊急サポート
- 重大なデータ損失
- システム完全停止
- セキュリティ問題

連絡先: [support@example.com]
対応時間: 平日 9:00-18:00
```

---

## 予防保守

### 定期メンテナンス

#### 週次チェックリスト
```markdown
## 週次メンテナンス項目

- [ ] バックアップの実行と確認
- [ ] ログファイルのローテーション
- [ ] キャッシュのクリーンアップ
- [ ] 不要ファイルの削除
- [ ] パフォーマンス指標の確認
```

#### 月次チェックリスト
```markdown
## 月次メンテナンス項目

- [ ] システム全体のバックアップ
- [ ] 依存関係の更新確認
- [ ] セキュリティパッチの適用
- [ ] ドキュメントの更新
- [ ] 使用統計の分析
```

### モニタリング設定

#### ログ監視
```bash
# エラーログの監視設定
tail -f error.log | grep -E "ERROR|CRITICAL" | while read line; do
  echo "$(date): $line" >> critical.log
  # アラート送信（必要に応じて）
done
```

#### パフォーマンス監視
```javascript
// 実行時間の計測
console.time('research');
await performResearch();
console.timeEnd('research');

// メモリ使用量の監視
const used = process.memoryUsage();
console.log('Memory usage:', {
  rss: `${Math.round(used.rss / 1024 / 1024)}MB`,
  heap: `${Math.round(used.heapUsed / 1024 / 1024)}MB`
});
```

---

## まとめ

このトラブルシューティングガイドを参考に、問題が発生した際は落ち着いて対処してください。多くの問題は基本的な手順で解決可能です。解決できない場合は、エスカレーション手順に従ってサポートを受けてください。