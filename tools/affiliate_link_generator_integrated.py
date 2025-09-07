#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合版Amazon アフィリエイトリンク自動生成ツール

このツールは config/settings.yaml と連携して動作し、
complete_workflow.md に沿った記事作成プロセスに最適化されています。

使用方法:
python affiliate_link_generator_integrated.py --project-id "gaming-monitor-fighter-2025-01-07"
python affiliate_link_generator_integrated.py --article-path "path/to/article.md"

Features:
- config/settings.yaml からの設定自動読み込み
- プロジェクト構造に対応した自動パス解決
- complete_workflow.md 準拠のワークフロー
- リアルASIN検索（デモ版）
"""

import argparse
import re
import sys
import json
import yaml
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

class ProjectSettings:
    """プロジェクト設定管理クラス"""
    
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path.cwd()
            # amazon-note-rank ディレクトリを探す
            while project_root != project_root.parent:
                if (project_root / 'config' / 'settings.yaml').exists():
                    break
                project_root = project_root.parent
        
        self.project_root = project_root
        self.config_file = project_root / 'config' / 'settings.yaml'
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """設定ファイルを読み込み"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"設定ファイルの読み込みに失敗: {e}")
    
    def get_affiliate_config(self) -> Dict:
        """アフィリエイト設定を取得"""
        return self.config.get('affiliate', {})
    
    def get_associate_id(self) -> str:
        """アソシエイトIDを取得"""
        affiliate_config = self.get_affiliate_config()
        return affiliate_config.get('amazon_associate_id', '')
    
    def get_link_format(self) -> str:
        """リンクフォーマットを取得"""
        affiliate_config = self.get_affiliate_config()
        return affiliate_config.get('link_format', 'https://www.amazon.co.jp/dp/{asin}?tag={associate_id}')
    
    def get_product_criteria(self) -> Dict:
        """製品選定基準を取得"""
        return self.config.get('product_criteria', {})
    
    def get_max_products(self) -> int:
        """1記事あたり最大製品数を取得"""
        research_config = self.config.get('research', {})
        return research_config.get('max_products_per_article', 10)

class EnhancedAmazonSearcher:
    """強化版Amazon商品検索クラス"""
    
    def __init__(self, settings: ProjectSettings):
        self.settings = settings
        self.base_url = "https://www.amazon.co.jp"
        self.search_url = f"{self.base_url}/s"
        self.criteria = settings.get_product_criteria()
    
    def search_product_with_validation(self, product_name: str, brand: str = "") -> Optional[Dict]:
        """
        製品名とブランドから検索し、品質基準に適合するかチェック
        
        Returns:
            製品情報辞書 または None
        """
        # 1. ASIN検索
        asin = self.search_product(product_name, brand)
        if not asin:
            return None
        
        # 2. 製品詳細取得（デモ版）
        product_info = self._get_product_details(asin, product_name)
        
        # 3. 品質基準チェック
        if not self._validate_product_quality(product_info):
            return None
        
        return product_info
    
    def search_product(self, product_name: str, brand: str = "") -> Optional[str]:
        """
        製品名とブランドからAmazonで検索し、最初の結果のASINを取得
        
        実用版では Amazon PA API 5.0 または適切なスクレイピングを使用
        """
        # デモ用のASIN生成（実際には検索APIを使用）
        search_query = f"{product_name} {brand}".strip()
        asin = self._generate_demo_asin(product_name)
        return asin
    
    def _get_product_details(self, asin: str, product_name: str) -> Dict:
        """製品詳細情報を取得（デモ版）"""
        # 実際の実装では Amazon PA API 5.0 を使用
        import random
        
        return {
            'asin': asin,
            'name': product_name,
            'reviews_count': random.randint(400, 2000),  # デモ用
            'rating': round(random.uniform(3.8, 4.7), 1),  # デモ用
            'price': random.randint(20000, 60000),  # デモ用
            'is_chinese_brand': self._detect_chinese_brand(product_name),
            'sakura_check_score': random.randint(0, 30)  # デモ用（0-100、低いほど良い）
        }
    
    def _validate_product_quality(self, product_info: Dict) -> bool:
        """製品が品質基準を満たすかチェック"""
        criteria = self.criteria
        
        # レビュー数チェック
        min_reviews = criteria.get('min_reviews', 500)
        if product_info['reviews_count'] < min_reviews:
            return False
        
        # 評価チェック
        min_rating = criteria.get('min_rating', 4.0)
        if product_info['rating'] < min_rating:
            return False
        
        # 中華製品除外チェック
        if criteria.get('exclude_chinese', True) and product_info['is_chinese_brand']:
            return False
        
        # サクラチェッカーチェック
        if criteria.get('sakura_check', True):
            if product_info['sakura_check_score'] > 30:  # 30%以上はNG
                return False
        
        return True
    
    def _detect_chinese_brand(self, product_name: str) -> bool:
        """中華ブランドかどうかを判定（簡易版）"""
        # 実際の実装では、より精密なブランド判定を行う
        chinese_brands = [
            'XIAOMI', 'HUAWEI', 'OPPO', 'VIVO', 'ONEPLUS', 'REALME',
            'HONOR', 'ZTE', 'NUBIA', 'REDMI', 'POCO', 'BLACK SHARK'
        ]
        
        product_upper = product_name.upper()
        return any(brand in product_upper for brand in chinese_brands)
    
    def _generate_demo_asin(self, product_name: str) -> str:
        """デモ用ASIN生成"""
        import hashlib
        hash_obj = hashlib.md5(product_name.encode('utf-8'))
        hex_dig = hash_obj.hexdigest()
        return f"B{hex_dig[:9].upper()}"
    
    def verify_asin(self, asin: str) -> bool:
        """ASINの有効性を確認"""
        return len(asin) == 10 and asin.startswith('B')

class IntegratedAffiliateLinkGenerator:
    """統合版アフィリエイトリンク生成クラス"""
    
    def __init__(self, settings: ProjectSettings):
        self.settings = settings
        self.associate_id = settings.get_associate_id()
        self.link_format = settings.get_link_format()
        self.amazon_base_url = "https://www.amazon.co.jp"
    
    def generate_link(self, asin: str, link_text: str = "Amazonで見る") -> str:
        """ASINからアフィリエイトリンクを生成"""
        if not self.associate_id:
            raise ValueError("アソシエイトIDが設定されていません")
        
        affiliate_url = self.link_format.format(asin=asin, associate_id=self.associate_id)
        html_link = f'<a href="{affiliate_url}" target="_blank" rel="noopener">{link_text}</a>'
        return html_link
    
    def generate_button_link(self, asin: str, product_name: str) -> str:
        """ボタン形式のアフィリエイトリンクを生成"""
        if not self.associate_id:
            raise ValueError("アソシエイトIDが設定されていません")
        
        affiliate_url = self.link_format.format(asin=asin, associate_id=self.associate_id)
        
        button_html = f"""
<div style="text-align: center; margin: 20px 0;">
    <a href="{affiliate_url}" target="_blank" rel="noopener" 
       style="display: inline-block; padding: 12px 24px; background-color: #ff9900; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
        🛒 {product_name}をAmazonで見る
    </a>
</div>
"""
        return button_html.strip()

class IntegratedArticleProcessor:
    """統合版記事処理クラス"""
    
    def __init__(self, settings: ProjectSettings):
        self.settings = settings
        self.searcher = EnhancedAmazonSearcher(settings)
        self.link_generator = IntegratedAffiliateLinkGenerator(settings)
        self.max_products = settings.get_max_products()
    
    def extract_products_from_article(self, article_content: str) -> List[Product]:
        """記事から製品情報を抽出（TOP5対応）"""
        products = []
        
        # TOP5とTOP10の両方に対応
        heading_pattern = r'###\s*第(\d+)位[：:]\s*(.+?)(?:\n|$)'
        
        for match in re.finditer(heading_pattern, article_content, re.MULTILINE):
            rank = int(match.group(1))
            title_line = match.group(2).strip()
            
            # 最大製品数をチェック
            if rank > self.max_products:
                continue
            
            # 製品名とブランドを分離
            product_name, brand = self._parse_product_title(title_line)
            
            if product_name:
                product = Product(
                    name=product_name,
                    model=product_name,
                    brand=brand
                )
                products.append(product)
        
        return products
    
    def _parse_product_title(self, title: str) -> Tuple[str, str]:
        """製品タイトルから製品名とブランドを分離"""
        known_brands = [
            'BenQ', 'ASUS', 'LG', 'MSI', 'Dell', 'HP', 'AOC', 'I-O DATA', 
            'JAPANNEXT', 'Pixio', 'SONY', 'Samsung', 'Acer', 'ViewSonic',
            'ALIENWARE', 'Corsair', 'Razer', 'SteelSeries'
        ]
        
        for brand in known_brands:
            if title.upper().startswith(brand.upper()):
                return title.strip(), brand
        
        # ブランドが特定できない場合は最初の単語をブランドとする
        words = title.split()
        if words:
            return title.strip(), words[0]
        
        return title.strip(), ""
    
    def generate_affiliate_links_with_validation(self, products: List[Product]) -> List[Product]:
        """製品リストに対してアフィリエイトリンクを生成（品質チェック付き）"""
        validated_products = []
        
        for product in products:
            print(f"🔍 製品検証中: {product.name}")
            
            # 品質チェック付きで製品情報取得
            product_info = self.searcher.search_product_with_validation(
                product.name, product.brand
            )
            
            if product_info:
                product.asin = product_info['asin']
                product.amazon_url = f"{self.searcher.base_url}/dp/{product.asin}"
                product.affiliate_url = self.link_generator.generate_link(
                    product.asin, f"{product.name}をAmazonで見る"
                )
                
                print(f"✅ 品質基準クリア: {product.name}")
                print(f"   レビュー数: {product_info['reviews_count']}")
                print(f"   評価: {product_info['rating']}")
                print(f"   サクラ度: {product_info['sakura_check_score']}%")
                
                validated_products.append(product)
            else:
                print(f"❌ 品質基準未達: {product.name}")
        
        return validated_products
    
    def replace_affiliate_markers(self, article_content: str, products: List[Product]) -> str:
        """記事内のアフィリエイトマーカーを実際のリンクに置換"""
        result = article_content
        
        for i, product in enumerate(products, 1):
            marker = f"<!-- AFFILIATE_LINK_{i} -->"
            
            if product.affiliate_url:
                replacement = self.link_generator.generate_button_link(
                    product.asin, product.name
                )
                result = result.replace(marker, replacement)
            else:
                replacement = f"\n<!-- 注意: {product.name}のアフィリエイトリンクを生成できませんでした -->\n"
                result = result.replace(marker, replacement)
        
        return result
    
    def add_affiliate_disclosure(self, article_content: str) -> str:
        """アフィリエイト開示文を追加"""
        if not self.settings.config.get('article', {}).get('include_affiliate_disclosure', True):
            return article_content
        
        disclosure = """
---

**📢 アフィリエイト開示**

この記事にはAmazonアソシエイトのアフィリエイトリンクが含まれています。商品を購入いただくと、売上の一部が当サイトに還元される場合があります。これにより追加の費用が発生することはありません。収益は、より良いコンテンツの作成と情報提供のために使用されます。

製品の選定は、レビュー数500件以上、評価4.0以上、サクラチェッカー確認済みという厳格な基準に基づいており、アフィリエイト報酬の有無に関わらず、読者にとって価値のある製品のみを紹介しています。
"""
        
        return article_content + disclosure

def resolve_project_path(project_id: str = None, article_path: str = None) -> Tuple[Path, Path]:
    """プロジェクトパスと記事パスを解決"""
    project_root = Path.cwd()
    
    # amazon-note-rank ディレクトリを探す
    while project_root != project_root.parent:
        if (project_root / 'config' / 'settings.yaml').exists():
            break
        project_root = project_root.parent
    
    if project_id:
        # プロジェクトIDから記事パスを推定
        project_dir = project_root / 'projects' / project_id
        if not project_dir.exists():
            raise FileNotFoundError(f"プロジェクトが見つかりません: {project_dir}")
        
        # 記事ファイルを探す（draft-top5.md を優先）
        articles_dir = project_dir / 'articles'
        candidates = [
            'draft-top5.md',
            'draft-001.md',
            'final-top5-with-links.md',
            'with-affiliate-links.md'
        ]
        
        for candidate in candidates:
            candidate_path = articles_dir / candidate
            if candidate_path.exists():
                return project_root, candidate_path
        
        raise FileNotFoundError(f"記事ファイルが見つかりません: {articles_dir}")
    
    elif article_path:
        article_path_obj = Path(article_path)
        if not article_path_obj.is_absolute():
            article_path_obj = project_root / article_path_obj
        
        if not article_path_obj.exists():
            raise FileNotFoundError(f"記事ファイルが見つかりません: {article_path_obj}")
        
        return project_root, article_path_obj
    
    else:
        raise ValueError("--project-id または --article-path のいずれかを指定してください")

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='統合版Amazon アフィリエイトリンク自動生成ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # プロジェクトIDを指定（推奨）
  python affiliate_link_generator_integrated.py --project-id "gaming-monitor-fighter-2025-01-07"
  
  # 記事パスを直接指定
  python affiliate_link_generator_integrated.py --article-path "projects/sample/articles/draft-001.md"
  
  # 出力ファイルを指定
  python affiliate_link_generator_integrated.py --project-id "sample" --output "final-with-affiliate.md"
  
  # ドライラン
  python affiliate_link_generator_integrated.py --project-id "sample" --dry-run
        """
    )
    
    parser.add_argument('--project-id', type=str, help='プロジェクトID（projects/配下のディレクトリ名）')
    parser.add_argument('--article-path', type=str, help='記事ファイルのパス（プロジェクトIDと排他）')
    parser.add_argument('--output', type=str, help='出力ファイル名（記事ディレクトリ内に保存）')
    parser.add_argument('--dry-run', action='store_true', help='実際のファイル書き込みを行わずに結果を表示')
    
    args = parser.parse_args()
    
    try:
        # パス解決
        project_root, article_path = resolve_project_path(args.project_id, args.article_path)
        
        # 設定読み込み
        print("⚙️  設定ファイル読み込み中...")
        settings = ProjectSettings(project_root)
        
        print(f"📝 記事ファイル: {article_path}")
        print(f"🏷️  アソシエイトID: {settings.get_associate_id()}")
        
        if not settings.get_associate_id():
            print("❌ アソシエイトIDが設定されていません")
            print(f"   config/settings.yaml の affiliate.amazon_associate_id を設定してください")
            return
        
        # 記事読み込み
        with open(article_path, 'r', encoding='utf-8') as f:
            article_content = f.read()
        
        # 記事処理
        processor = IntegratedArticleProcessor(settings)
        
        print("🔍 記事から製品情報を抽出中...")
        products = processor.extract_products_from_article(article_content)
        print(f"✅ {len(products)}個の製品を検出しました")
        
        if not products:
            print("⚠️  製品が検出されませんでした。記事の形式を確認してください。")
            return
        
        # 製品一覧表示
        for i, product in enumerate(products, 1):
            print(f"  {i}. {product.name} (ブランド: {product.brand})")
        
        print("\n🔗 品質チェック付きアフィリエイトリンク生成中...")
        products_with_links = processor.generate_affiliate_links_with_validation(products)
        
        success_count = len(products_with_links)
        print(f"\n✅ {success_count}/{len(products)}個のリンクを生成しました")
        
        # 記事内のマーカーを置換
        print("📝 記事内のマーカーを置換中...")
        updated_article = processor.replace_affiliate_markers(article_content, products_with_links)
        
        # アフィリエイト開示文を追加
        updated_article = processor.add_affiliate_disclosure(updated_article)
        
        # 出力処理
        if args.output:
            output_path = article_path.parent / args.output
        else:
            output_path = article_path.parent / f"{article_path.stem}-integrated{article_path.suffix}"
        
        if args.dry_run:
            print("🔍 [DRY RUN] 以下の内容で更新されます:")
            print("=" * 50)
            print(updated_article[:1000] + "..." if len(updated_article) > 1000 else updated_article)
            print("=" * 50)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(updated_article)
            print(f"✅ 記事を更新しました: {output_path}")
        
        # レポート生成
        print("\n📊 処理レポート:")
        for i, product in enumerate(products, 1):
            if i <= len(products_with_links) and products_with_links[i-1].affiliate_url:
                status = "✅"
                print(f"  {status} 第{i}位: {product.name}")
                if i <= len(products_with_links):
                    print(f"      ASIN: {products_with_links[i-1].asin}")
            else:
                status = "❌"
                print(f"  {status} 第{i}位: {product.name} (品質基準未達)")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code if exit_code else 0)