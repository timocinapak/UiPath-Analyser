#!/usr/bin/env python3
"""
UiPath Workflow Analyzer - Komut Satırı Aracı

Kullanım:
    python analyze_workflow.py <xaml_path> <json_path> [--output <report_path>]

Örnek:
    python analyze_workflow.py xaml_files/Main.xaml xaml_files/project.json --output report.md
"""

import sys
import argparse
from pathlib import Path
from workflow_analyzer_module import analyze_workflow


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description='UiPath Workflow Analyzer - Workflow dosyalarını analiz et',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  %(prog)s xaml_files/Main.xaml xaml_files/project.json
  %(prog)s xaml_files/Main.xaml xaml_files/project.json --output report.md
        """
    )
    
    parser.add_argument('xaml', help='XAML dosyasının yolu')
    parser.add_argument('json', help='JSON dosyasının yolu')
    parser.add_argument('--output', '-o', help='Rapor dosyasının kaydedileceği yol')
    
    args = parser.parse_args()
    
    # Dosyaların varlığını kontrol et
    if not Path(args.xaml).exists():
        print(f"❌ Hata: {args.xaml} dosyası bulunamadı")
        sys.exit(1)
    
    if not Path(args.json).exists():
        print(f"❌ Hata: {args.json} dosyası bulunamadı")
        sys.exit(1)
    
    try:
        print("🚀 UiPath Workflow Analyzer başlanıyor...\n")
        
        # Analiz yap
        analysis = analyze_workflow(args.xaml, args.json)
        
        # Sonuçları göster
        print(f"✅ Analiz tamamlandı!\n")
        print(f"📊 Sağlık Skoru: {analysis.overall_health_score:.1f}/100")
        print(f"📌 Aktivite Sayısı: {len(analysis.activities)}")
        print(f"⚠️ Sorun Sayısı: {len(analysis.issues)}")
        print(f"💡 Öneri Sayısı: {len(analysis.recommendations)}")
        
        # Sorunları göster
        if analysis.issues:
            print(f"\n⚠️ Tespit Edilen Sorunlar:")
            for i, issue in enumerate(analysis.issues, 1):
                print(f"  {i}. [{issue.severity}] {issue.title}")
                print(f"     → {issue.solution}\n")
        
        # Raporunu kaydet
        if args.output:
            print(f"\n💾 Rapor kaydediliyor: {args.output}")
            # Markdown rapor oluştur
            report = _generate_markdown_report(analysis)
            Path(args.output).write_text(report, encoding='utf-8')
            print(f"✅ Rapor başarıyla kaydedildi!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)


def _generate_markdown_report(analysis) -> str:
    """Markdown rapor oluştur"""
    report = []
    report.append("# 📋 UiPath Workflow Analiz Raporu\n")
    report.append(f"**Workflow**: {analysis.workflow_name}\n")
    report.append(f"**Sağlık Skoru**: {analysis.overall_health_score:.1f}/100\n\n")
    
    report.append("## 📊 Özet\n")
    report.append(f"- Aktivite: {len(analysis.activities)}\n")
    report.append(f"- Değişken: {len(analysis.variables)}\n")
    report.append(f"- Sorun: {len(analysis.issues)}\n")
    report.append(f"- Öneri: {len(analysis.recommendations)}\n\n")
    
    if analysis.issues:
        report.append("## ⚠️ Sorunlar\n\n")
        for issue in analysis.issues:
            report.append(f"### {issue.title}\n")
            report.append(f"- **Severity**: {issue.severity}\n")
            report.append(f"- **Category**: {issue.category}\n")
            report.append(f"- **Problem**: {issue.description}\n")
            report.append(f"- **Solution**: {issue.solution}\n\n")
    
    return '\n'.join(report)


if __name__ == '__main__':
    main()
