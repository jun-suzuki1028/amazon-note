# 効率化ツールセット

長期運用での効率性と品質向上を支援するツール集です。繰り返し作業の自動化とClaude Code活用のベストプラクティスを提供します。

---

## 🚀 クイックスタートコマンド集

### 1. プロジェクト初期化コマンド

```bash
# 新規プロジェクトの一括セットアップ
init_project() {
  PROJECT_ID="$1-$(date +%Y%m%d)"
  mkdir -p projects/$PROJECT_ID/{persona,prompts,research,articles,meta}
  
  # メタデータ初期化
  cat > projects/$PROJECT_ID/meta/project.yaml << EOF
project_id: $PROJECT_ID
created_at: $(date -Iseconds)
status: initialized
category: $1
target_revenue: 50000
quality_target: 85
EOF
  
  echo "✅ Project $PROJECT_ID initialized"
  echo "📁 Path: projects/$PROJECT_ID/"
}

# 使用例: init_project "gaming-monitor"
```

### 2. バッチ処理用コマンド

```bash
# 複数カテゴリの一括ペルソナ作成
batch_persona_creation() {
  CATEGORIES=("$@")
  for category in "${CATEGORIES[@]}"; do
    echo "Creating persona for $category..."
    PROJECT_ID="$category-$(date +%Y%m%d)"
    init_project "$category"
    
    claude-code "
    @templates/persona/basic_template.md を使用して
    $category のペルソナを作成し、
    projects/$PROJECT_ID/persona/persona-001.md に保存
    "
    
    sleep 2  # API制限対策
  done
}

# 使用例: batch_persona_creation "gaming-monitor" "wireless-earbuds" "robot-vacuum"
```

### 3. ステータス確認コマンド

```bash
# 全プロジェクトの進捗確認
check_all_projects() {
  echo "📊 Project Status Overview"
  echo "========================="
  
  for project in projects/*/; do
    if [ -f "$project/meta/project.yaml" ]; then
      PROJECT_ID=$(basename "$project")
      STATUS=$(grep "status:" "$project/meta/project.yaml" | cut -d' ' -f2)
      CATEGORY=$(grep "category:" "$project/meta/project.yaml" | cut -d' ' -f2)
      
      # 各フェーズのファイル存在確認
      PERSONA="❌"
      PROMPTS="❌"
      RESEARCH="❌"
      ARTICLE="❌"
      
      [ -f "$project/persona/persona-001.md" ] && PERSONA="✅"
      [ -f "$project/prompts/research-prompts.md" ] && PROMPTS="✅"
      [ -f "$project/research/research-data.md" ] && RESEARCH="✅"
      [ -f "$project/articles/final-001.md" ] && ARTICLE="✅"
      
      echo "📁 $PROJECT_ID ($CATEGORY)"
      echo "   Status: $STATUS"
      echo "   Progress: Persona:$PERSONA Prompts:$PROMPTS Research:$RESEARCH Article:$ARTICLE"
      echo ""
    fi
  done
}
```

---

## 🔄 繰り返し作業の自動化テンプレート

### 1. 週次記事作成バッチ

```bash
#!/bin/bash
# weekly_article_batch.sh - 週5本の記事を効率的に作成

# 設定
WEEKLY_TARGET=5
CATEGORIES=("gaming-monitor" "wireless-earbuds" "robot-vacuum" "standing-desk" "air-purifier")

# 週次バッチ実行
run_weekly_batch() {
  WEEK_ID="week-$(date +%Y-%W)"
  mkdir -p reports/$WEEK_ID
  
  echo "🚀 Starting Weekly Batch: $WEEK_ID"
  echo "Target: $WEEKLY_TARGET articles"
  echo ""
  
  START_TIME=$(date +%s)
  COMPLETED=0
  
  for i in $(seq 0 $((WEEKLY_TARGET-1))); do
    CATEGORY="${CATEGORIES[$i]}"
    PROJECT_ID="$CATEGORY-$(date +%Y%m%d-%H%M)"
    
    echo "[$((i+1))/$WEEKLY_TARGET] Processing: $CATEGORY"
    
    # Phase 1: ペルソナ作成
    create_persona "$PROJECT_ID" "$CATEGORY"
    
    # Phase 2: プロンプト生成
    generate_prompts "$PROJECT_ID"
    
    # Phase 3: リサーチ実行
    execute_research "$PROJECT_ID"
    
    # Phase 4: 記事生成
    generate_article "$PROJECT_ID"
    
    # Phase 5: 品質チェック
    quality_check "$PROJECT_ID"
    
    COMPLETED=$((COMPLETED+1))
    echo "✅ Completed: $PROJECT_ID"
    echo ""
  done
  
  END_TIME=$(date +%s)
  DURATION=$((END_TIME - START_TIME))
  
  # レポート生成
  generate_weekly_report "$WEEK_ID" "$COMPLETED" "$DURATION"
}
```

### 2. ペルソナ再利用システム

```yaml
# persona_library.yaml - 再利用可能なペルソナライブラリ

persona_templates:
  young_gamer:
    name: "ゲーマー太郎"
    age: "25-30"
    occupation: "ITエンジニア"
    categories: ["gaming-monitor", "gaming-chair", "gaming-keyboard"]
    pain_points:
      - "長時間プレイでの疲労"
      - "競技性と快適性の両立"
      - "コスパと性能のバランス"
  
  remote_worker:
    name: "在宅花子"
    age: "30-40"
    occupation: "リモートワーカー"
    categories: ["standing-desk", "monitor", "webcam", "chair"]
    pain_points:
      - "自宅の作業環境改善"
      - "長時間作業での健康管理"
      - "限られたスペースの有効活用"
  
  health_conscious:
    name: "健康重視さん"
    age: "35-45"
    occupation: "会社員"
    categories: ["air-purifier", "water-filter", "fitness-tracker"]
    pain_points:
      - "家族の健康管理"
      - "アレルギー対策"
      - "生活の質向上"
```

### 3. リサーチデータ統合ツール

```python
# merge_research_data.py - 複数のリサーチ結果を統合

import os
import yaml
import json
from datetime import datetime

def merge_research_data(project_ids):
    """複数プロジェクトのリサーチデータを統合"""
    merged_data = {
        "merged_at": datetime.now().isoformat(),
        "projects": project_ids,
        "products": {},
        "trends": [],
        "keywords": set()
    }
    
    for project_id in project_ids:
        research_file = f"projects/{project_id}/research/research-data.md"
        if os.path.exists(research_file):
            # リサーチデータを読み込み
            with open(research_file, 'r') as f:
                content = f.read()
                # YAMLセクションを抽出
                # ... パース処理 ...
                
    # 重複製品の除去と統合
    # トレンドの集約
    # キーワードの統合
    
    return merged_data

# 使用例
projects = ["gaming-monitor-20250906", "gaming-monitor-20250905"]
merged = merge_research_data(projects)
```

---

## 📈 Claude Code活用ベストプラクティス

### 1. コンテキスト管理の最適化

#### 1.1 効率的なファイル参照

```bash
# ❌ 非効率な例 - 個別に読み込み
claude-code "
ファイル1を読んでください: @file1.md
"
claude-code "
ファイル2を読んでください: @file2.md
"

# ✅ 効率的な例 - 一括読み込み
claude-code "
以下のファイルを参照して作業を進めてください：
@templates/persona/basic_template.md
@prompts/persona_creation.md
@projects/$PROJECT_ID/meta/project.yaml

これらを基に[具体的な指示]を実行してください。
"
```

#### 1.2 段階的なコンテキスト構築

```bash
# Phase別のコンテキスト管理
claude-code "
# Phase 1: 基本コンテキスト設定
プロジェクト: $PROJECT_ID
カテゴリ: $CATEGORY
目標: 高品質なランキング記事作成

# Phase 2: データ読み込み
@projects/$PROJECT_ID/persona/persona-001.md
@projects/$PROJECT_ID/research/research-data.md

# Phase 3: 実行指示
上記のデータを基に記事を生成してください。
"
```

### 2. プロンプトの構造化

#### 2.1 CRISP形式（Context-Role-Instruction-Steps-Product）

```markdown
# Context（背景）
Amazonランキング記事作成システムで、週5本の記事作成目標があります。

# Role（役割）
あなたは経験豊富なコンテンツマーケターとして行動してください。

# Instruction（指示）
ペルソナとリサーチデータを基に、SEO最適化された記事を作成します。

# Steps（手順）
1. ペルソナ分析
2. リサーチデータ整理
3. 記事構成作成
4. コンテンツ生成
5. 品質チェック

# Product（成果物）
3000文字以上のマークダウン形式記事
```

#### 2.2 チェーンプロンプティング

```bash
# Step 1: 分析フェーズ
claude-code "
@projects/$PROJECT_ID/persona/persona-001.md を分析し、
主要な悩みとニーズを3つ抽出してください。
結果を projects/$PROJECT_ID/meta/analysis.md に保存。
"

# Step 2: 構成フェーズ
claude-code "
@projects/$PROJECT_ID/meta/analysis.md の分析結果を基に、
記事の構成案を作成してください。
各セクションの目的と文字数目安を含めてください。
"

# Step 3: 生成フェーズ
claude-code "
承認された構成案に従って、
実際の記事コンテンツを生成してください。
"
```

### 3. エラーハンドリングパターン

#### 3.1 自動リトライメカニズム

```bash
# retry_with_claude.sh
retry_claude_operation() {
  local MAX_RETRIES=3
  local RETRY_COUNT=0
  local COMMAND="$1"
  
  while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "Attempt $((RETRY_COUNT+1))/$MAX_RETRIES"
    
    if claude-code "$COMMAND"; then
      echo "✅ Success"
      return 0
    else
      RETRY_COUNT=$((RETRY_COUNT+1))
      echo "⚠️ Failed, retrying in 5 seconds..."
      sleep 5
    fi
  done
  
  echo "❌ Failed after $MAX_RETRIES attempts"
  return 1
}
```

#### 3.2 フォールバック戦略

```yaml
fallback_strategies:
  gemini_mcp_failure:
    primary: "Gemini MCPでリサーチ実行"
    fallback_1: "手動プロンプト表示 + 入力待機"
    fallback_2: "過去の類似リサーチデータ再利用"
    fallback_3: "基本テンプレートで仮生成"
  
  quality_check_failure:
    primary: "自動品質チェック"
    fallback_1: "チェックリスト表示 + 手動確認"
    fallback_2: "最小限チェック + ドラフト保存"
```

### 4. パフォーマンス最適化

#### 4.1 並列処理の活用

```bash
# parallel_processing.sh
parallel_article_generation() {
  local PROJECTS=("$@")
  
  for project in "${PROJECTS[@]}"; do
    (
      echo "Starting: $project"
      generate_article_for_project "$project"
      echo "Completed: $project"
    ) &
  done
  
  wait  # すべてのバックグラウンドジョブを待機
  echo "All parallel tasks completed"
}
```

#### 4.2 キャッシュ戦略

```yaml
cache_strategy:
  persona_cache:
    duration: "30 days"
    reuse_conditions:
      - "同一カテゴリ"
      - "類似ターゲット層"
    
  research_cache:
    duration: "7 days"
    reuse_conditions:
      - "同一キーワード"
      - "価格変動±10%以内"
  
  template_cache:
    duration: "permanent"
    versioning: true
```

---

## 🎯 品質保証の自動化

### 1. 自動品質スコアリング

```python
# quality_scorer.py
def calculate_quality_score(article_path):
    """記事の品質スコアを自動計算"""
    
    with open(article_path, 'r') as f:
        content = f.read()
    
    scores = {
        'word_count': check_word_count(content, target=3000),
        'keyword_density': check_keyword_density(content, target=0.015),
        'heading_structure': check_heading_structure(content),
        'readability': check_readability(content),
        'persona_alignment': check_persona_alignment(content),
        'seo_optimization': check_seo_factors(content)
    }
    
    # 重み付け平均
    weights = {
        'word_count': 0.15,
        'keyword_density': 0.20,
        'heading_structure': 0.15,
        'readability': 0.20,
        'persona_alignment': 0.15,
        'seo_optimization': 0.15
    }
    
    total_score = sum(scores[k] * weights[k] for k in scores)
    return total_score, scores

def check_word_count(content, target):
    """文字数チェック"""
    count = len(content)
    if count >= target:
        return 100
    else:
        return (count / target) * 100

def check_keyword_density(content, target):
    """キーワード密度チェック"""
    # 実装...
    pass
```

### 2. 自動改善提案システム

```bash
# auto_improvement.sh
generate_improvement_suggestions() {
  local ARTICLE_PATH="$1"
  local SCORE_RESULT="$2"
  
  claude-code "
  記事: @$ARTICLE_PATH
  品質スコア: @$SCORE_RESULT
  
  以下の観点で具体的な改善提案を生成してください：
  1. 低スコア項目の改善方法
  2. ペルソナ適合性の向上
  3. SEO要素の強化
  4. 読みやすさの改善
  
  各提案には：
  - 具体的な修正箇所
  - 修正前後の例
  - 期待される効果
  を含めてください。
  "
}
```

---

## 📊 分析・レポーティングツール

### 1. 週次パフォーマンスレポート

```bash
# weekly_report_generator.sh
generate_weekly_report() {
  local WEEK_ID="$1"
  local COMPLETED="$2"
  local DURATION="$3"
  
  cat > reports/$WEEK_ID/summary.md << EOF
# 週次レポート: $WEEK_ID

## 📈 生産性指標
- 作成記事数: $COMPLETED / 5
- 総作業時間: $(($DURATION / 60))分
- 平均作成時間: $(($DURATION / $COMPLETED / 60))分/記事

## 📊 品質指標
$(calculate_weekly_quality_metrics)

## 💰 収益予測
$(estimate_weekly_revenue)

## 📝 改善提案
$(generate_improvement_suggestions)

## 📅 次週の計画
$(generate_next_week_plan)
EOF
  
  echo "📊 Report generated: reports/$WEEK_ID/summary.md"
}
```

### 2. トレンド分析ツール

```python
# trend_analyzer.py
import pandas as pd
from datetime import datetime, timedelta

def analyze_trends(days=30):
    """過去N日間のトレンド分析"""
    
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # プロジェクトデータ収集
    for project_dir in os.listdir('projects'):
        if os.path.isdir(f'projects/{project_dir}'):
            meta_file = f'projects/{project_dir}/meta/project.yaml'
            if os.path.exists(meta_file):
                # メタデータ読み込み
                # ... 
                pass
    
    df = pd.DataFrame(data)
    
    trends = {
        'productivity': df.groupby('date')['completion_time'].mean(),
        'quality': df.groupby('date')['quality_score'].mean(),
        'categories': df['category'].value_counts(),
        'success_rate': (df['status'] == 'completed').mean()
    }
    
    return trends

def generate_trend_report(trends):
    """トレンドレポート生成"""
    report = f"""
# トレンド分析レポート

## 生産性トレンド
- 平均作成時間: {trends['productivity'].mean():.1f}分
- 改善率: {calculate_improvement_rate(trends['productivity'])}%

## 品質トレンド  
- 平均品質スコア: {trends['quality'].mean():.1f}
- 最高スコア: {trends['quality'].max():.1f}

## カテゴリ分布
{format_category_distribution(trends['categories'])}

## 成功率
- 完了率: {trends['success_rate']*100:.1f}%
"""
    return report
```

---

## 🔧 メンテナンス・最適化ツール

### 1. プロジェクトクリーンアップ

```bash
# cleanup_projects.sh
cleanup_old_projects() {
  local DAYS_TO_KEEP=30
  local ARCHIVE_DIR="archives/$(date +%Y%m)"
  
  mkdir -p "$ARCHIVE_DIR"
  
  echo "🧹 Cleaning up projects older than $DAYS_TO_KEEP days"
  
  find projects -type d -name "*-20*" -mtime +$DAYS_TO_KEEP | while read project; do
    PROJECT_ID=$(basename "$project")
    
    # 完了プロジェクトのみアーカイブ
    if grep -q "status: completed" "$project/meta/project.yaml" 2>/dev/null; then
      echo "📦 Archiving: $PROJECT_ID"
      tar -czf "$ARCHIVE_DIR/$PROJECT_ID.tar.gz" "$project"
      rm -rf "$project"
    fi
  done
  
  echo "✅ Cleanup completed"
}
```

### 2. テンプレート更新チェッカー

```bash
# template_updater.sh
check_template_updates() {
  local TEMPLATE_VERSION_FILE="templates/.version"
  local CURRENT_VERSION=$(cat "$TEMPLATE_VERSION_FILE" 2>/dev/null || echo "1.0.0")
  
  echo "📋 Current template version: $CURRENT_VERSION"
  
  # 更新が必要なテンプレートをチェック
  claude-code "
  現在のテンプレートバージョン: $CURRENT_VERSION
  
  以下のテンプレートを確認し、
  最新のベストプラクティスに基づいて
  更新が必要な項目をリストアップしてください：
  
  @templates/persona/basic_template.md
  @templates/article/ranking_article.md
  @templates/prompts/research_prompts.md
  
  各項目について：
  - 更新理由
  - 具体的な変更内容
  - 期待される効果
  を説明してください。
  "
}
```

---

## 💡 トラブルシューティング集

### よくある問題と解決策

```yaml
troubleshooting:
  issue_1:
    symptom: "Claude Codeがタイムアウトする"
    causes:
      - "大きすぎるファイルの読み込み"
      - "複雑すぎるプロンプト"
    solutions:
      - "ファイルを分割して段階的に処理"
      - "プロンプトをステップに分解"
      - "バッチサイズを縮小"
  
  issue_2:
    symptom: "品質スコアが低い"
    causes:
      - "ペルソナとコンテンツの不一致"
      - "リサーチデータ不足"
    solutions:
      - "ペルソナの再分析と調整"
      - "追加リサーチの実施"
      - "競合記事の分析強化"
  
  issue_3:
    symptom: "記事生成が途中で止まる"
    causes:
      - "メモリ不足"
      - "データ形式エラー"
    solutions:
      - "プロジェクトを再初期化"
      - "データ検証ツールの実行"
      - "段階的生成に切り替え"
```

### エラーログ分析ツール

```python
# error_log_analyzer.py
def analyze_error_logs(log_dir="logs"):
    """エラーログを分析して改善提案を生成"""
    
    error_patterns = {
        'timeout': r'timeout|timed out',
        'file_not_found': r'file not found|no such file',
        'parse_error': r'parse error|invalid syntax',
        'api_limit': r'rate limit|too many requests'
    }
    
    error_counts = {pattern: 0 for pattern in error_patterns}
    
    for log_file in os.listdir(log_dir):
        with open(f"{log_dir}/{log_file}", 'r') as f:
            content = f.read()
            for pattern_name, pattern in error_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    error_counts[pattern_name] += 1
    
    # 改善提案の生成
    suggestions = generate_improvement_suggestions(error_counts)
    return error_counts, suggestions
```

---

## 🚀 今後の拡張アイデア

### 1. AI駆動の自動最適化

```yaml
future_enhancements:
  auto_optimization:
    description: "成功パターンを学習して自動的に最適化"
    features:
      - "成功記事のパターン抽出"
      - "ペルソナの自動調整"
      - "プロンプトの動的最適化"
  
  multi_language:
    description: "多言語対応"
    features:
      - "英語圏向け記事生成"
      - "自動翻訳と最適化"
      - "地域別カスタマイズ"
  
  advanced_analytics:
    description: "高度な分析機能"
    features:
      - "収益予測モデル"
      - "トレンド予測"
      - "A/Bテスト自動化"
```

### 2. 統合ダッシュボード構想

```html
<!-- dashboard_concept.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Amazon Article Generator Dashboard</title>
</head>
<body>
    <h1>統合ダッシュボード（構想）</h1>
    
    <section id="overview">
        <h2>概要</h2>
        <div class="metrics">
            <div>今週の記事: <span id="weekly-articles">0/5</span></div>
            <div>平均品質: <span id="avg-quality">0</span></div>
            <div>予測収益: <span id="revenue-forecast">¥0</span></div>
        </div>
    </section>
    
    <section id="projects">
        <h2>プロジェクト管理</h2>
        <!-- プロジェクト一覧 -->
    </section>
    
    <section id="automation">
        <h2>自動化コントロール</h2>
        <button onclick="runWeeklyBatch()">週次バッチ実行</button>
        <button onclick="runQualityCheck()">品質チェック</button>
    </section>
</body>
</html>
```

---

このツールセットを活用することで、週5本の高品質記事作成を効率的に実現し、長期的な運用での品質向上を支援します。定期的にツールを更新し、新しいベストプラクティスを取り入れていくことが重要です。