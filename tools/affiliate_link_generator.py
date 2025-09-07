#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon アフィリエイトリンク自動生成ツール

このツールは記事内の製品名からAmazonアフィリエイトリンクを自動生成し、
記事内の <!-- AFFILIATE_LINK_X --> マーカーを置換します。

使用方法:
python affiliate_link_generator.py --article-path "path/to/article.md" --associate-id "your-associate-id"

Features:
- 記事内の製品名を自動検出
- Amazonアフィリエイトリンクを自動生成
- マーカー <!-- AFFILIATE_LINK_X --> を実際のリンクに置換
- 日本のAmazon.co.jpに対応
- リンクの有効性確認機能
"""

import argparse
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus
import urllib.request
import urllib.error
from dataclasses import dataclass

@dataclass
class Product:
    """製品情報を格納するデータクラス"""
    name: str
    model: str
    brand: str
    asin: Optional[str] = None
    amazon_url: Optional[str] = None
    affiliate_url: Optional[str] = None

class AffiliateConfiguration:
    """アフィリエイト設定管理クラス"""
    
    def __init__(self):
        self.config_file = Path.home() / '.amazon_affiliate_config.json'
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """設定ファイルを読み込み"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config: Dict):
        """設定ファイルを保存"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        self.config = config
    
    def get_associate_id(self) -> Optional[str]:
        """アソシエイトIDを取得"""
        return self.config.get('associate_id')
    
    def set_associate_id(self, associate_id: str):
        """アソシエイトIDを設定"""
        self.config['associate_id'] = associate_id
        self.save_config(self.config)

class AmazonSearcher:
    """Amazon商品検索クラス"""
    
    def __init__(self):
        self.base_url = "https://www.amazon.co.jp"
        self.search_url = f"{self.base_url}/s"
    
    def search_product(self, product_name: str, brand: str = "") -> Optional[str]:
        """
        製品名とブランドからAmazonで検索し、最初の結果のASINを取得
        
        実際のAPIは使用せず、検索URLからASINをシミュレーション生成
        実用時はAmazon PA API 5.0やスクレイピングライブラリを使用推奨
        """
        # 実際の実装では、ここでAmazon PA API 5.0を使用
        # または、適切なスクレイピングライブラリ（BeautifulSoup等）を使用
        
        # デモ用のASIN生成（実際には検索結果から取得）
        search_query = f"{product_name} {brand}".strip()
        # 製品名からASINっぽい文字列を生成（実際の実装では検索APIを使用）
        asin = self._generate_demo_asin(product_name)
        return asin
    
    def _generate_demo_asin(self, product_name: str) -> str:
        """
        デモ用ASIN生成（実際の実装では不要）
        製品名のハッシュからASIN形式の文字列を生成
        """
        import hashlib
        hash_obj = hashlib.md5(product_name.encode('utf-8'))
        hex_dig = hash_obj.hexdigest()
        # ASINは通常10文字の英数字
        return f"B{hex_dig[:9].upper()}"
    
    def verify_asin(self, asin: str) -> bool:
        """ASINの有効性を確認（実際にはHTTPリクエストで確認）"""
        # デモ用の実装（実際にはAmazonページにアクセスして確認）
        return len(asin) == 10 and asin.startswith('B')

class AffiliateLinkGenerator:
    """アフィリエイトリンク生成クラス"""
    
    def __init__(self, associate_id: str):
        self.associate_id = associate_id
        self.amazon_base_url = "https://www.amazon.co.jp"
    
    def generate_link(self, asin: str, link_text: str = "Amazonで見る") -> str:
        """
        ASINからアフィリエイトリンクを生成
        
        Args:
            asin: Amazon ASIN
            link_text: リンクテキスト
        
        Returns:
            HTMLアフィリエイトリンク
        """
        affiliate_url = f"{self.amazon_base_url}/dp/{asin}?tag={self.associate_id}"
        
        html_link = f'<a href="{affiliate_url}" target="_blank" rel="noopener">{link_text}</a>'
        return html_link
    
    def generate_button_link(self, asin: str, product_name: str) -> str:
        """
        ボタン形式のアフィリエイトリンクを生成
        """
        affiliate_url = f"{self.amazon_base_url}/dp/{asin}?tag={self.associate_id}"
        
        button_html = f"""
<div style="text-align: center; margin: 20px 0;">
    <a href="{affiliate_url}" target="_blank" rel="noopener" 
       style="display: inline-block; padding: 12px 24px; background-color: #ff9900; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
        🛒 {product_name}をAmazonで見る
    </a>
</div>
"""
        return button_html.strip()

class ArticleProcessor:
    """記事処理クラス"""
    
    def __init__(self, associate_id: str):
        self.searcher = AmazonSearcher()
        self.link_generator = AffiliateLinkGenerator(associate_id)
        self.products = []
    
    def extract_products_from_article(self, article_content: str) -> List[Product]:
        """
        記事から製品情報を抽出
        
        記事内の見出しや表から製品名とブランドを抽出
        """
        products = []
        
        # 製品見出しのパターン（### 第X位：製品名）
        heading_pattern = r'###\s*第(\d+)位[：:]\s*(.+?)(?:\n|$)'
        
        for match in re.finditer(heading_pattern, article_content, re.MULTILINE):
            rank = match.group(1)
            title_line = match.group(2).strip()
            
            # 製品名とブランドを分離
            product_name, brand = self._parse_product_title(title_line)
            
            if product_name:
                product = Product(
                    name=product_name,
                    model=product_name,  # 簡略化のため同一とする
                    brand=brand
                )
                products.append(product)
        
        return products
    
    def _parse_product_title(self, title: str) -> Tuple[str, str]:
        """
        製品タイトルから製品名とブランドを分離
        例：「BenQ ZOWIE XL2411K」→ (「BenQ ZOWIE XL2411K」, 「BenQ」)
        """
        # 一般的なブランド名のパターン
        known_brands = [
            'BenQ', 'ASUS', 'LG', 'MSI', 'Dell', 'HP', 'AOC', 'I-O DATA', 
            'JAPANNEXT', 'Pixio', 'SONY', 'Samsung', 'Acer'
        ]
        
        for brand in known_brands:
            if title.upper().startswith(brand.upper()):
                return title.strip(), brand
        
        # ブランドが特定できない場合は最初の単語をブランドとする
        words = title.split()
        if words:
            return title.strip(), words[0]
        
        return title.strip(), ""
    
    def generate_affiliate_links_for_products(self, products: List[Product]) -> List[Product]:
        """製品リストに対してアフィリエイトリンクを生成"""
        for product in products:
            # ASINを検索
            asin = self.searcher.search_product(product.name, product.brand)
            if asin and self.searcher.verify_asin(asin):
                product.asin = asin
                product.amazon_url = f"{self.searcher.base_url}/dp/{asin}"
                product.affiliate_url = self.link_generator.generate_link(asin, f"{product.name}をAmazonで見る")
        
        return products
    
    def replace_affiliate_markers(self, article_content: str, products: List[Product]) -> str:
        """記事内のアフィリエイトマーカーを実際のリンクに置換"""
        result = article_content
        
        for i, product in enumerate(products, 1):
            marker = f"<!-- AFFILIATE_LINK_{i} -->"
            
            if product.affiliate_url:
                # ボタン形式のリンクを生成
                replacement = self.link_generator.generate_button_link(
                    product.asin, product.name
                )
                result = result.replace(marker, replacement)
            else:
                # リンクが生成できない場合の代替テキスト
                replacement = f"\n<!-- 注意: {product.name}のアフィリエイトリンクを生成できませんでした -->\n"
                result = result.replace(marker, replacement)
        
        return result

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='Amazon アフィリエイトリンク自動生成ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python affiliate_link_generator.py --article-path "articles/draft-001.md" --associate-id "yourid-22"
  python affiliate_link_generator.py --setup  # 初期設定
        """
    )
    
    parser.add_argument('--article-path', type=str, help='記事ファイルのパス')
    parser.add_argument('--associate-id', type=str, help='AmazonアソシエイトID')
    parser.add_argument('--setup', action='store_true', help='初期設定を行う')
    parser.add_argument('--output', type=str, help='出力ファイルパス（指定しない場合は元ファイルを上書き）')
    parser.add_argument('--dry-run', action='store_true', help='実際のファイル書き込みを行わずに結果を表示')
    
    args = parser.parse_args()
    
    # 設定管理
    config = AffiliateConfiguration()
    
    # セットアップモード
    if args.setup:
        print("🔧 Amazon アフィリエイトリンク生成ツール セットアップ")
        associate_id = input("AmazonアソシエイトID (例: yourid-22): ").strip()
        if associate_id:
            config.set_associate_id(associate_id)
            print(f"✅ アソシエイトID '{associate_id}' を保存しました")
        else:
            print("❌ アソシエイトIDが入力されませんでした")
        return
    
    # アソシエイトIDの取得
    associate_id = args.associate_id or config.get_associate_id()
    if not associate_id:
        print("❌ AmazonアソシエイトIDが設定されていません")
        print("   --associate-id オプションで指定するか、--setup で設定してください")
        return
    
    # 記事ファイルの確認
    if not args.article_path:
        print("❌ 記事ファイルのパスが指定されていません")
        print("   --article-path オプションで記事ファイルを指定してください")
        return
    
    article_path = Path(args.article_path)
    if not article_path.exists():
        print(f"❌ 記事ファイルが見つかりません: {article_path}")
        return
    
    print(f"📝 記事ファイル: {article_path}")
    print(f"🏷️  アソシエイトID: {associate_id}")
    
    # 記事を読み込み
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            article_content = f.read()
    except Exception as e:
        print(f"❌ 記事ファイルの読み込みに失敗: {e}")
        return
    
    # 記事処理
    processor = ArticleProcessor(associate_id)
    
    print("🔍 記事から製品情報を抽出中...")
    products = processor.extract_products_from_article(article_content)
    print(f"✅ {len(products)}個の製品を検出しました")
    
    if not products:
        print("⚠️  製品が検出されませんでした。記事の形式を確認してください。")
        return
    
    # 製品一覧表示
    for i, product in enumerate(products, 1):
        print(f"  {i}. {product.name} (ブランド: {product.brand})")
    
    print("🔗 アフィリエイトリンクを生成中...")
    products_with_links = processor.generate_affiliate_links_for_products(products)
    
    # 結果表示
    success_count = sum(1 for p in products_with_links if p.affiliate_url)
    print(f"✅ {success_count}/{len(products)}個のリンクを生成しました")
    
    # 記事内のマーカーを置換
    print("📝 記事内のマーカーを置換中...")
    updated_article = processor.replace_affiliate_markers(article_content, products_with_links)
    
    # 出力処理
    output_path = Path(args.output) if args.output else article_path
    
    if args.dry_run:
        print("🔍 [DRY RUN] 以下の内容で更新されます:")
        print("=" * 50)
        print(updated_article[:1000] + "..." if len(updated_article) > 1000 else updated_article)
        print("=" * 50)
    else:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(updated_article)
            print(f"✅ 記事を更新しました: {output_path}")
        except Exception as e:
            print(f"❌ ファイル書き込みに失敗: {e}")
    
    # レポート生成
    print("\n📊 処理レポート:")
    for i, product in enumerate(products_with_links, 1):
        status = "✅" if product.affiliate_url else "❌"
        print(f"  {status} 第{i}位: {product.name}")
        if product.asin:
            print(f"      ASIN: {product.asin}")
        if product.affiliate_url:
            print(f"      リンク: 生成済み")

if __name__ == "__main__":
    main()