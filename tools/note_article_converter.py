#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note用記事変換ツール

アフィリエイトリンク付きの記事をNote規約に準拠した形式に変換します。

Features:
- アフィリエイトリンクを商品名に変換
- 外部サイト誘導の自然な挿入
- Note規約準拠チェック
"""

import re
import sys
from pathlib import Path
from typing import List, Dict

class NoteArticleConverter:
    """Note用記事変換クラス"""
    
    def __init__(self, blog_url: str = "", blog_name: str = "私のブログ"):
        self.blog_url = blog_url
        self.blog_name = blog_name
    
    def convert_affiliate_article_to_note(self, article_content: str) -> str:
        """アフィリエイト記事をNote用に変換"""
        
        # 1. アフィリエイトリンクを商品名に変換
        result = self._remove_affiliate_links(article_content)
        
        # 2. 外部サイト誘導セクションを追加
        result = self._add_external_site_promotion(result)
        
        # 3. Note規約準拠の注記を追加
        result = self._add_compliance_note(result)
        
        return result
    
    def _remove_affiliate_links(self, content: str) -> str:
        """アフィリエイトリンクを削除し、商品検索案内に変更"""
        
        # <div>で囲まれたアフィリエイトボタンを検出
        affiliate_pattern = r'<div style="text-align: center[^>]*>.*?</div>'
        
        def replace_affiliate_link(match):
            link_html = match.group(0)
            
            # リンク内の商品名を抽出
            product_pattern = r'🛒\s*(.+?)をAmazonで見る'
            product_match = re.search(product_pattern, link_html)
            
            if product_match:
                product_name = product_match.group(1)
                return f"\n**💡 購入を検討される方へ**\nAmazonで「**{product_name}**」を検索してみてください。\n"
            else:
                return "\n**💡 購入を検討される方へ**\nAmazonで商品名を検索して最新の価格をチェックしてください。\n"
        
        result = re.sub(affiliate_pattern, replace_affiliate_link, content, flags=re.DOTALL)
        return result
    
    def _add_external_site_promotion(self, content: str) -> str:
        """外部サイト誘導セクションを追加"""
        
        # まとめ の直前に挿入
        summary_pattern = r'(## まとめ)'
        
        promotion_section = f"""
## 📖 さらに詳しい情報をお求めの方へ

この記事では、格闘ゲーム向けモニター選びの基本をお伝えしましたが、
**より詳細な比較情報と最新の価格情報**を{self.blog_name}で公開しています。

### {self.blog_name}限定コンテンツ
✅ **全製品の詳細スペック比較表**  
✅ **実際の購入リンクと最安値情報**  
✅ **セットアップ完全ガイド**  
✅ **プロゲーマー使用機材データベース**  
✅ **設定最適化のコツ**  

{f"👉 **[{self.blog_name}をチェック]({self.blog_url})**" if self.blog_url else f"👉 **{self.blog_name}で「格闘ゲーム モニター」で検索**"}

※価格や在庫状況は変動するため、最新情報は各販売サイトでご確認ください

\\1"""
        
        if re.search(summary_pattern, content):
            result = re.sub(summary_pattern, promotion_section, content)
        else:
            # まとめ がない場合は最後に追加
            result = content + promotion_section
        
        return result
    
    def _add_compliance_note(self, content: str) -> str:
        """規約準拠の注記を追加"""
        
        compliance_note = """
---

*この記事は格闘ゲーム向けモニター選びの情報提供を目的としています。購入の際は最新の価格・仕様を各販売サイトでご確認ください。*
"""
        
        return content + compliance_note
    
    def create_paid_section_suggestion(self) -> str:
        """有料記事部分の提案を生成"""
        
        return """
## 💰 Note有料記事活用案

以下のような構成で有料記事を作成することをお勧めします：

### 価格設定案
- **基本版**：200円（3製品の詳細比較）
- **完全版**：500円（10製品＋セットアップガイド）

### 有料部分の内容案
```
【この続きは有料部分で公開中】

## 詳細レビューと購入ガイド

### 第1位：BenQ ZOWIE XL2411K 完全レビュー
- 実際の使用感（3ヶ月使用）
- 他製品との詳細比較
- 最適な購入タイミング
- セットアップ手順（画像付き）

### 第2位：I-O DATA EX-LDGC242HTB
... (同様の詳細レビュー)

### 購入前チェックリスト
□ 使用ゲームタイトルの確認
□ PC/PS5のスペック確認
□ デスク環境の測定
...

### プロ設定集
✅ ウメハラ設定
✅ ときど設定
✅ GO1設定
```
"""

def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Note用記事変換ツール')
    parser.add_argument('--input', required=True, help='入力記事ファイル')
    parser.add_argument('--output', help='出力ファイル（指定しない場合は入力ファイル名に-note.mdを追加）')
    parser.add_argument('--blog-url', default='', help='外部ブログのURL')
    parser.add_argument('--blog-name', default='私のブログ', help='外部ブログ名')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ ファイルが見つかりません: {input_path}")
        return
    
    # 出力ファイル名を決定
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}-note{input_path.suffix}"
    
    # 記事を読み込み
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        return
    
    # 変換処理
    converter = NoteArticleConverter(args.blog_url, args.blog_name)
    
    print(f"📝 Note用記事に変換中...")
    note_content = converter.convert_affiliate_article_to_note(content)
    
    # 結果を保存
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(note_content)
        print(f"✅ Note用記事を生成しました: {output_path}")
    except Exception as e:
        print(f"❌ ファイル保存エラー: {e}")
        return
    
    # 有料記事案を表示
    print("\n" + converter.create_paid_section_suggestion())
    
    print(f"""
🎯 Note投稿時のポイント:
1. ハッシュタグ: #格闘ゲーム #ゲーミングモニター #ストリートファイター #鉄拳
2. カテゴリ: テクノロジー > ガジェット
3. アイキャッチ: モニター画像またはゲーム画面
4. 投稿時間: 平日19-21時、土日14-16時が効果的
""")

if __name__ == "__main__":
    main()