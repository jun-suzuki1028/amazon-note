#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PA-API サクラ検出システム品質チェックスクリプト

継続的品質改善システムの一部として、以下の品質メトリクスを監視：
- テストカバレッジ
- コード品質スコア
- TDD遵守チェック
- パフォーマンスベンチマーク
- セキュリティ検証

Usage:
    python scripts/pa_api_quality_check.py [--coverage] [--performance] [--security] [--all]
"""

import argparse
import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import yaml


class PAAPIQualityChecker:
    """PA-APIシステム品質チェッククラス"""
    
    def __init__(self, project_root: Path = None):
        """初期化"""
        self.project_root = project_root or Path.cwd()
        self.quality_thresholds = {
            'test_coverage': 85.0,  # 85%以上のカバレッジ
            'unit_test_coverage': 90.0,  # 90%以上の単体テストカバレッジ
            'performance_threshold': 20.0,  # 15商品20分以内処理
            'memory_limit_mb': 500.0,  # メモリ使用量制限
            'api_response_time': 5.0,  # API応答時間制限（秒）
        }
        self.results = {}
    
    def run_test_coverage(self) -> Dict[str, Any]:
        """テストカバレッジ測定実行"""
        print("🧪 テストカバレッジ測定を実行中...")
        
        try:
            # pytestでカバレッジ測定
            cmd = [
                "uv", "run", "pytest", 
                "tests/", 
                "--cov=tools",
                "--cov-report=json",
                "--cov-report=term",
                "-v"
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            
            # カバレッジJSONレポート読み込み
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data['totals']['percent_covered']
                
                # 品質判定
                coverage_passed = total_coverage >= self.quality_thresholds['test_coverage']
                
                return {
                    'status': 'PASSED' if coverage_passed else 'FAILED',
                    'total_coverage': total_coverage,
                    'threshold': self.quality_thresholds['test_coverage'],
                    'details': coverage_data['files'],
                    'command_output': result.stdout,
                    'command_errors': result.stderr
                }
            else:
                return {
                    'status': 'ERROR',
                    'error': 'カバレッジレポートファイルが見つかりません',
                    'command_output': result.stdout,
                    'command_errors': result.stderr
                }
                
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': f'カバレッジ測定エラー: {e}'
            }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """パフォーマンステスト実行"""
        print("⚡ パフォーマンステストを実行中...")
        
        try:
            cmd = [
                "uv", "run", "pytest", 
                "tests/test_performance.py",
                "-v", 
                "--tb=short"
            ]
            
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            execution_time = time.time() - start_time
            
            # テスト結果解析
            performance_passed = result.returncode == 0
            
            return {
                'status': 'PASSED' if performance_passed else 'FAILED',
                'execution_time_seconds': execution_time,
                'threshold_minutes': self.quality_thresholds['performance_threshold'],
                'command_output': result.stdout,
                'command_errors': result.stderr,
                'return_code': result.returncode
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': f'パフォーマンステストエラー: {e}'
            }
    
    def run_tdd_compliance_check(self) -> Dict[str, Any]:
        """TDD遵守チェック"""
        print("📋 TDD遵守状況をチェック中...")
        
        try:
            test_files = list((self.project_root / "tests").glob("test_*.py"))
            tdd_compliance = {
                'total_test_files': len(test_files),
                'red_phase_tests': 0,
                'green_phase_tests': 0,
                'refactor_phase_tests': 0,
                'tdd_compliance_score': 0.0
            }
            
            # テストファイル内のTDDフェーズマーカーをチェック
            for test_file in test_files:
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # TDDフェーズマーカーを検索
                        if '_RED' in content or 'RED Phase' in content:
                            tdd_compliance['red_phase_tests'] += 1
                        if '_GREEN' in content or 'GREEN Phase' in content:
                            tdd_compliance['green_phase_tests'] += 1
                        if '_REFACTOR' in content or 'REFACTOR Phase' in content:
                            tdd_compliance['refactor_phase_tests'] += 1
                            
                except Exception as e:
                    print(f"警告: {test_file} の読み込みエラー: {e}")
            
            # TDD遵守スコア計算
            if tdd_compliance['total_test_files'] > 0:
                phases_total = (
                    tdd_compliance['red_phase_tests'] + 
                    tdd_compliance['green_phase_tests'] + 
                    tdd_compliance['refactor_phase_tests']
                )
                expected_phases = tdd_compliance['total_test_files'] * 3  # 各ファイルで3フェーズ期待
                tdd_compliance['tdd_compliance_score'] = (phases_total / expected_phases) * 100
            
            # 品質判定（70%以上のTDD遵守率を期待）
            tdd_passed = tdd_compliance['tdd_compliance_score'] >= 70.0
            
            return {
                'status': 'PASSED' if tdd_passed else 'FAILED',
                'compliance_details': tdd_compliance,
                'threshold': 70.0
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': f'TDD遵守チェックエラー: {e}'
            }
    
    def run_security_check(self) -> Dict[str, Any]:
        """セキュリティチェック（基本）"""
        print("🛡️  セキュリティチェックを実行中...")
        
        try:
            security_issues = []
            
            # 設定ファイルのハードコード認証情報チェック
            config_file = self.project_root / "config" / "settings.yaml"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                    
                    # 危険なパターンをチェック
                    dangerous_patterns = [
                        ('access_key:', 'ハードコードされたアクセスキー'),
                        ('secret_key:', 'ハードコードされたシークレットキー'),
                        ('password:', 'ハードコードされたパスワード'),
                        ('token:', 'ハードコードされたトークン')
                    ]
                    
                    for pattern, description in dangerous_patterns:
                        if pattern in config_content and not config_content.split(pattern)[1].strip().startswith('${'):
                            # 環境変数参照でない場合は警告
                            if not any(env_var in config_content.split(pattern)[1][:50] for env_var in ['${', 'ENV[']):
                                security_issues.append({
                                    'type': 'hardcoded_credentials',
                                    'description': description,
                                    'file': str(config_file),
                                    'severity': 'HIGH'
                                })
            
            # Pythonファイルでの潜在的セキュリティ問題チェック
            python_files = list(self.project_root.glob("**/*.py"))
            for py_file in python_files:
                if py_file.name.startswith('.'):
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 危険な関数使用をチェック
                        dangerous_functions = [
                            ('eval(', 'eval()関数の使用'),
                            ('exec(', 'exec()関数の使用'),
                            ('shell=True', 'shell=Trueの使用'),
                            ('input(', 'input()関数の使用（注意）')
                        ]
                        
                        for func, description in dangerous_functions:
                            if func in content:
                                security_issues.append({
                                    'type': 'dangerous_function',
                                    'description': description,
                                    'file': str(py_file),
                                    'severity': 'MEDIUM'
                                })
                                
                except Exception:
                    continue
            
            # セキュリティ判定
            high_severity_count = len([issue for issue in security_issues if issue['severity'] == 'HIGH'])
            security_passed = high_severity_count == 0
            
            return {
                'status': 'PASSED' if security_passed else 'FAILED',
                'issues_found': len(security_issues),
                'high_severity_issues': high_severity_count,
                'security_issues': security_issues
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': f'セキュリティチェックエラー: {e}'
            }
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """品質レポート生成"""
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results.values() if r.get('status') == 'PASSED'])
        
        overall_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        overall_status = 'PASSED' if overall_score >= 80.0 else 'FAILED'
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_status': overall_status,
            'overall_score': overall_score,
            'checks_total': total_checks,
            'checks_passed': passed_checks,
            'checks_failed': total_checks - passed_checks,
            'individual_results': self.results,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """改善推奨事項生成"""
        recommendations = []
        
        # カバレッジ改善推奨
        if 'coverage' in self.results:
            coverage_result = self.results['coverage']
            if coverage_result.get('status') != 'PASSED':
                recommendations.append(
                    f"テストカバレッジを{self.quality_thresholds['test_coverage']}%以上に向上させてください。"
                    f"現在: {coverage_result.get('total_coverage', 0):.1f}%"
                )
        
        # パフォーマンス改善推奨
        if 'performance' in self.results:
            performance_result = self.results['performance']
            if performance_result.get('status') != 'PASSED':
                recommendations.append(
                    "パフォーマンステストを通過するよう最適化を実施してください。"
                )
        
        # TDD遵守改善推奨
        if 'tdd_compliance' in self.results:
            tdd_result = self.results['tdd_compliance']
            if tdd_result.get('status') != 'PASSED':
                recommendations.append(
                    "TDD（Red-Green-Refactor）サイクルの遵守を向上させてください。"
                    "テストファイルにフェーズマーカーを追加してください。"
                )
        
        # セキュリティ改善推奨
        if 'security' in self.results:
            security_result = self.results['security']
            if security_result.get('status') != 'PASSED':
                issues = security_result.get('security_issues', [])
                high_issues = [issue for issue in issues if issue['severity'] == 'HIGH']
                if high_issues:
                    recommendations.append(
                        f"高優先度セキュリティ問題を修正してください: {len(high_issues)}件"
                    )
        
        if not recommendations:
            recommendations.append("すべての品質チェックをパスしています。継続的な品質維持を心がけてください。")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], output_path: Path = None) -> None:
        """レポート保存"""
        if output_path is None:
            output_path = self.project_root / "quality_report.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 品質レポートを保存しました: {output_path}")
    
    def run_all_checks(self, include_coverage=True, include_performance=True, 
                      include_security=True, include_tdd=True) -> Dict[str, Any]:
        """全品質チェック実行"""
        print("🚀 PA-API サクラ検出システム品質チェックを開始...")
        print("=" * 60)
        
        if include_coverage:
            self.results['coverage'] = self.run_test_coverage()
        
        if include_performance:
            self.results['performance'] = self.run_performance_tests()
        
        if include_tdd:
            self.results['tdd_compliance'] = self.run_tdd_compliance_check()
        
        if include_security:
            self.results['security'] = self.run_security_check()
        
        # 品質レポート生成
        report = self.generate_quality_report()
        
        print("\n" + "=" * 60)
        print("📊 品質チェック結果サマリー")
        print("=" * 60)
        print(f"総合ステータス: {report['overall_status']}")
        print(f"総合スコア: {report['overall_score']:.1f}%")
        print(f"チェック項目: {report['checks_passed']}/{report['checks_total']} 通過")
        
        print("\n🔍 個別結果:")
        for check_name, result in self.results.items():
            status_emoji = "✅" if result.get('status') == 'PASSED' else "❌" if result.get('status') == 'FAILED' else "⚠️"
            print(f"  {status_emoji} {check_name}: {result.get('status', 'UNKNOWN')}")
        
        if report['recommendations']:
            print("\n💡 改善推奨事項:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        return report


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='PA-API サクラ検出システム品質チェック')
    parser.add_argument('--coverage', action='store_true', help='テストカバレッジチェック')
    parser.add_argument('--performance', action='store_true', help='パフォーマンステスト')
    parser.add_argument('--security', action='store_true', help='セキュリティチェック')
    parser.add_argument('--tdd', action='store_true', help='TDD遵守チェック')
    parser.add_argument('--all', action='store_true', help='全チェック実行')
    parser.add_argument('--output', type=str, help='レポート出力先')
    
    args = parser.parse_args()
    
    # 実行するチェック項目を決定
    if args.all or not any([args.coverage, args.performance, args.security, args.tdd]):
        # デフォルトまたは--allの場合は全チェック
        include_coverage = True
        include_performance = True
        include_security = True
        include_tdd = True
    else:
        include_coverage = args.coverage
        include_performance = args.performance
        include_security = args.security
        include_tdd = args.tdd
    
    # 品質チェック実行
    checker = PAAPIQualityChecker()
    report = checker.run_all_checks(
        include_coverage=include_coverage,
        include_performance=include_performance,
        include_security=include_security,
        include_tdd=include_tdd
    )
    
    # レポート保存
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = None
    
    checker.save_report(report, output_path)
    
    # 終了コード設定
    exit_code = 0 if report['overall_status'] == 'PASSED' else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()