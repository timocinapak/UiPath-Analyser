import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set
import re

@dataclass
class Issue:
    """Tespit edilen sorun"""
    severity: str  # CRITICAL, WARNING, INFO
    category: str
    description: str
    location: str
    suggestion: str

class UiPathXAMLAnalyzer:
    """UiPath XAML dosyalarını analiz eden sınıf"""

    def __init__(self, xaml_path: str):
        self.xaml_path = Path(xaml_path)
        self.tree = None
        self.root = None
        self.namespaces = {}
        self.issues: List[Issue] = []
        self.urls: Set[str] = set()
        self.db_connections: Set[str] = set()
        self.used_activities: Set[str] = set()

    def load_xaml(self):
        """XAML dosyasını yükle"""
        try:
            self.tree = ET.parse(self.xaml_path)
            self.root = self.tree.getroot()

            # Namespace'leri otomatik tespit et
            for event, elem in ET.iterparse(str(self.xaml_path), events=['start-ns']):
                prefix, uri = event
                self.namespaces[prefix if prefix else 'default'] = uri

            return True
        except Exception as e:
            print(f"❌ XAML dosyası yüklenemedi: {e}")
            return False

    def analyze(self):
        """Tam analiz yap"""
        if not self.load_xaml():
            return

        print("🔍 UiPath XAML Analizi Başlıyor...\n")

        # Analizleri çalıştır
        self.check_error_handling()
        self.check_excel_operations()
        self.check_browser_operations()
        self.check_loops()
        self.check_selectors()
        self.check_delays()
        self.check_logging()
        self.check_file_paths()
        self.check_variables()
        self.check_performance()
        self.extract_resources()

        # Sonuçları göster
        self.print_report()

    def extract_resources(self):
        """URL, DB ve Aktiviteler gibi kaynakları çıkar"""
        self.extract_urls()
        self.extract_database_connections()
        self.extract_activities()

    def find_all_elements(self, tag: str) -> List[ET.Element]:
        """Tüm elementleri bul (namespace aware)"""
        results = []
        for ns_prefix, ns_uri in self.namespaces.items():
            results.extend(self.root.findall(f".//{{{ns_uri}}}{tag}"))
        return results

    def check_error_handling(self):
        """Try-Catch kontrolü"""
        try_catch_elements = self.find_all_elements("TryCatch")
        total_activities = len(self.find_all_elements("Sequence"))
        total_activities += len(self.find_all_elements("Flowchart"))

        if len(try_catch_elements) == 0:
            self.issues.append(Issue(
                severity="CRITICAL",
                category="Error Handling",
                description="Hiçbir Try-Catch bloğu bulunamadı",
                location="Tüm workflow",
                suggestion="Ana iş akışına ve kritik işlemlere Try-Catch ekleyin. "
                          "Özellikle Excel, Browser ve Loop işlemlerini koruyun."
            ))
        elif len(try_catch_elements) < total_activities / 2:
            self.issues.append(Issue(
                severity="WARNING",
                category="Error Handling",
                description=f"Yetersiz hata yönetimi: {len(try_catch_elements)} Try-Catch, "
                          f"{total_activities} aktivite için",
                location="Çeşitli lokasyonlar",
                suggestion="Kritik işlemlere daha fazla hata yönetimi ekleyin"
            ))

    def check_excel_operations(self):
        """Excel işlemlerini kontrol et"""
        excel_scopes = self.find_all_elements("ExcelProcessScopeX")
        excel_app_cards = self.find_all_elements("ExcelApplicationCard")
        for_each_rows = self.find_all_elements("ForEachRow")
        write_cells = self.find_all_elements("WriteCellX")

        # Excel scope döngü içinde mi?
        for loop in for_each_rows:
            # Döngü içindeki tüm çocuk elementleri kontrol et
            nested_excel = self._find_nested_elements(loop, ["ExcelProcessScopeX", "ExcelApplicationCard"])
            if nested_excel:
                self.issues.append(Issue(
                    severity="CRITICAL",
                    category="Performance",
                    description="Excel Process Scope/Application Card döngü içinde bulundu",
                    location="ForEachRow içinde",
                    suggestion="Excel dosyasını döngü DIŞINDA açın, sadece Write işlemini döngü içinde yapın. "
                              "Bu 10-100x performans artışı sağlar."
                ))

        # Write Cell işlemleri
        if len(write_cells) > 0:
            for write_cell in write_cells:
                auto_increment = write_cell.get("AutoIncrementRow", "False")
                if auto_increment == "True":
                    self.issues.append(Issue(
                        severity="WARNING",
                        category="Excel Operations",
                        description="AutoIncrementRow kullanılıyor",
                        location="WriteCellX aktivitesi",
                        suggestion="AutoIncrement yerine satır indeksi ile çalışmayı düşünün. "
                                  "Daha kontrollü ve tahmin edilebilir."
                    ))

    def check_browser_operations(self):
        """Browser işlemlerini kontrol et"""
        browser_scopes = self.find_all_elements("NApplicationCard")

        # İç içe browser scope kontrolü
        for scope in browser_scopes:
            nested_scopes = self._find_nested_elements(scope, ["NApplicationCard"])
            if nested_scopes:
                self.issues.append(Issue(
                    severity="WARNING",
                    category="Browser Operations",
                    description="İç içe Browser Scope bulundu",
                    location="NApplicationCard içinde NApplicationCard",
                    suggestion="İç içe browser scope'ları kaldırın. Tek bir scope yeterlidir."
                ))

        # Type Into işlemleri
        type_intos = self.find_all_elements("NTypeInto")
        for type_into in type_intos:
            click_before = type_into.get("ClickBeforeMode")
            empty_field = type_into.get("EmptyFieldMode")

            if empty_field != "SingleLine":
                self.issues.append(Issue(
                    severity="INFO",
                    category="Browser Operations",
                    description="Type Into EmptyFieldMode önerisi",
                    location="NTypeInto aktivitesi",
                    suggestion="EmptyFieldMode='SingleLine' kullanarak alanı önce temizleyin"
                ))

        # Click işlemlerinden sonra delay kontrolü
        clicks = self.find_all_elements("NClick")
        delay_tag = f"{{{self.namespaces.get('s', 'http://schemas.microsoft.com/netfx/2009/xaml/activities')}}}Delay"
        for i, click in enumerate(clicks):
            display_name = click.get("DisplayName", "")
            if "calculate" in display_name.lower() or "submit" in display_name.lower():
                # Sonraki elementi kontrol et
                parent = self._find_parent(self.root, click)
                if parent is not None:
                    children = list(parent)
                    click_index = children.index(click)
                    if click_index < len(children) - 1:
                        next_elem = children[click_index + 1]
                        if next_elem.tag != delay_tag:
                            self.issues.append(Issue(
                                severity="WARNING",
                                category="Browser Operations",
                                description=f"'{display_name}' sonrası bekleme yok",
                                location="NClick aktivitesi",
                                suggestion="Calculate/Submit butonundan sonra 2-3 saniye Delay ekleyin. "
                                          "Sayfa yanıt süresi için gerekli."
                            ))

    def check_loops(self):
        """Döngü yapılarını kontrol et"""
        for_each_rows = self.find_all_elements("ForEachRow")

        for loop in for_each_rows:
            # Döngü içinde Try-Catch var mı?
            try_catches = self._find_nested_elements(loop, ["TryCatch"])
            if not try_catches:
                self.issues.append(Issue(
                    severity="CRITICAL",
                    category="Error Handling",
                    description="ForEachRow döngüsü içinde Try-Catch yok",
                    location="ForEachRow aktivitesi",
                    suggestion="Döngü içinde her iterasyonu Try-Catch ile koruyun. "
                              "Bir satırda hata olsa bile diğer satırlar işlensin."
                ))

            # Döngü içinde Log Message var mı?
            log_messages = self._find_nested_elements(loop, ["LogMessage"])
            if len(log_messages) < 2:
                self.issues.append(Issue(
                    severity="WARNING",
                    category="Logging",
                    description="ForEachRow döngüsünde yetersiz logging",
                    location="ForEachRow aktivitesi",
                    suggestion="Her iterasyonun başında ve sonunda log mesajı ekleyin. "
                              "Hata ayıklama için kritik."
                ))

    def check_selectors(self):
        """Selector güvenilirliğini kontrol et"""
        all_targets = self.find_all_elements("TargetAnchorable")

        for target in all_targets:
            browser_url = target.get("BrowserURL", "")

            # URL'de parametreler var mı?
            if "?" in browser_url and len(browser_url.split("?")[1]) > 50:
                self.issues.append(Issue(
                    severity="WARNING",
                    category="Selectors",
                    description="Selector'da uzun parametreli URL kullanılıyor",
                    location="TargetAnchorable",
                    suggestion="Dinamik parametreler içeren URL'ler selector'ları kırabilir. "
                              "Sadece base URL kullanın veya wildcard kullanın."
                ))

            # Selector güvenilirliği
            full_selector = target.get("FullSelectorArgument", "")
            fuzzy_selector = target.get("FuzzySelectorArgument", "")

            if not fuzzy_selector and full_selector:
                self.issues.append(Issue(
                    severity="INFO",
                    category="Selectors",
                    description="Sadece Full Selector kullanılıyor, Fuzzy yok",
                    location="TargetAnchorable",
                    suggestion="Fuzzy Selector ekleyerek selector güvenilirliğini artırın"
                ))

    def check_delays(self):
        """Delay/Wait aktivitelerini kontrol et"""
        delays = self.find_all_elements("Delay")

        if len(delays) == 0:
            self.issues.append(Issue(
                severity="WARNING",
                category="Timing",
                description="Hiç Delay aktivitesi bulunamadı",
                location="Tüm workflow",
                suggestion="Web işlemleri için uygun yerlere Delay ekleyin. "
                          "Özellikle form submit ve sayfa yükleme sonrasında."
            ))

    def check_logging(self):
        """Log mesajlarını kontrol et"""
        log_messages = self.find_all_elements("LogMessage")

        total_activities = len(self.find_all_elements("Sequence"))
        total_activities += len(self.find_all_elements("Flowchart"))

        if len(log_messages) == 0:
            self.issues.append(Issue(
                severity="CRITICAL",
                category="Logging",
                description="Hiç Log Message bulunamadı",
                location="Tüm workflow",
                suggestion="İş akışının kritik noktalarına log mesajları ekleyin: "
                          "- Başlangıç/Bitiş\n"
                          "- Her döngü iterasyonu\n"
                          "- Hata durumları\n"
                          "- Önemli kararlar (If/Switch)"
            ))
        elif len(log_messages) < 3:
            self.issues.append(Issue(
                severity="WARNING",
                category="Logging",
                description=f"Yetersiz logging: Sadece {len(log_messages)} log mesajı",
                location="Tüm workflow",
                suggestion="Daha fazla log mesajı ekleyin. Debug ve production monitoring için gerekli."
            ))

    def check_file_paths(self):
        """Dosya yollarını kontrol et"""
        # Excel dosya yolları
        excel_paths = []
        for elem in self.root.iter():
            if "WorkbookPath" in elem.attrib:
                path = elem.get("WorkbookPath")
                if re.search(r"[a-zA-Z]:\\", path) or path.startswith("\\\\"):
                    self.issues.append(Issue(
                        severity="WARNING",
                        category="File Paths",
                        description=f"Hardcoded dosya yolu kullanılıyor: {path}",
                        location="WorkbookPath",
                        suggestion="Path.Combine ile mutlak yol oluşturun veya Config dosyası kullanın. "
                                  "Örnek: Path.Combine(Environment.CurrentDirectory, 'Data', 'file.xlsx')"
                    ))
                if "Auxilliary" in path:
                    self.issues.append(Issue(
                        severity="INFO",
                        category="File Paths",
                        description=f"Yazım hatası: 'Auxilliary' -> 'Auxiliary'",
                        location=f"Path: {path}",
                        suggestion="Klasör ismini düzeltin"
                    ))

    def check_variables(self):
        """Değişken kullanımını kontrol et"""
        variables = self.find_all_elements("Variable")
        var_names = [(var.get("Name"), var.get(f"{{{self.namespaces['x']}}}TypeArguments")) for var in variables]

        for name, var_type in var_names:
            if name and not re.match(r"^[a-z]+([A-Z][a-z0-9]+)*$|^[A-Z][a-z0-9]+([A-Z][a-z0-9]+)*$", name):
                if len(name) > 3 : # Kısa değişken adlarını (örn: i, j, dt) yoksay
                    self.issues.append(Issue(
                        severity="INFO",
                        category="Naming Convention",
                        description=f"Değişken ismi convention'a uymuyor: {name}",
                        location="Variable tanımı",
                        suggestion="camelCase (örn: 'kullaniciAdi') veya PascalCase (örn: 'KullaniciAdi') kullanın."
                    ))

    def check_performance(self):
        """Performans sorunlarını tespit et"""
        # Çok derin nested yapılar
        max_depth = self._calculate_max_depth()
        if max_depth > 7: # Genellikle 5-7 arası makul, 7'den sonrası karmaşıklaşır
            self.issues.append(Issue(
                severity="WARNING",
                category="Performance",
                description=f"Çok derin iç içe yapı: {max_depth} seviye",
                location="Workflow yapısı",
                suggestion="İç içe geçmiş yapıları yeniden düzenleyin. "
                          "Invoke Workflow kullanarak modüler hale getirin."
            ))

    def extract_urls(self):
        """URL'leri dosyadan çıkar."""
        url_pattern = re.compile(r'https?://[^\s"\'\]]+')
        for elem in self.root.iter():
            for key, value in elem.attrib.items():
                if "Url" in key or "Uri" in key:
                    if value and isinstance(value, str):
                        self.urls.add(value.strip())
                # Bazen URL'ler genel stringlerde olabilir
                if isinstance(value, str):
                    found = url_pattern.findall(value)
                    for url in found:
                        self.urls.add(url)

    def extract_database_connections(self):
        """Veritabanı bağlantılarını dosyadan çıkar."""
        db_connect_activities = self.find_all_elements("DatabaseConnect")
        for activity in db_connect_activities:
            conn_string = activity.get("ConnectionString")
            if conn_string:
                self.db_connections.add(conn_string)

    def extract_activities(self):
        """Kullanılan tüm aktiviteleri listele."""
        for elem in self.root.iter():
            # Namespace'i kaldırıp sadece aktivite adını al
            tag = elem.tag
            if '}' in tag:
                self.used_activities.add(tag.split('}', 1)[1])


    def _find_nested_elements(self, parent: ET.Element, tag_names: List[str]) -> List[ET.Element]:
        """Parent element içindeki belirli tag'leri bul"""
        results = []
        for tag_name in tag_names:
            for ns_uri in self.namespaces.values():
                results.extend(parent.findall(f".//{{{ns_uri}}}{tag_name}"))
        return results

    def _find_parent(self, root: ET.Element, child: ET.Element) -> ET.Element:
        """Bir elementin parent'ını bul"""
        for parent in root.iter():
            if child in list(parent):
                return parent
        return None

    def _calculate_max_depth(self, element: ET.Element = None, current_depth: int = 0) -> int:
        """Maksimum nested depth'i hesapla"""
        if element is None:
            element = self.root

        if len(element) == 0:
            return current_depth

        max_child_depth = current_depth
        for child in element:
            child_depth = self._calculate_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def print_report(self):
        """Analiz raporunu yazdır"""
        print("=" * 80)
        print("📊 UiPath XAML ANALİZ RAPORU")
        print("=" * 80)
        print(f"📁 Dosya: {self.xaml_path.name}\n")

        # Severity bazında grupla
        critical = [i for i in self.issues if i.severity == "CRITICAL"]
        warnings = [i for i in self.issues if i.severity == "WARNING"]
        info = [i for i in self.issues if i.severity == "INFO"]

        print(f"🔴 Kritik Sorunlar: {len(critical)}")
        print(f"⚠️  Uyarılar: {len(warnings)}")
        print(f"ℹ️  Bilgilendirmeler: {len(info)}")
        print()

        # Kritik sorunlar
        if critical:
            print("=" * 80)
            print("🔴 KRİTİK SORUNLAR")
            print("=" * 80)
            for i, issue in enumerate(critical, 1):
                self._print_issue(i, issue)

        # Uyarılar
        if warnings:
            print("=" * 80)
            print("⚠️  UYARILAR")
            print("=" * 80)
            for i, issue in enumerate(warnings, 1):
                self._print_issue(i, issue)

        # Bilgilendirmeler
        if info:
            print("=" * 80)
            print("ℹ️  BİLGİLENDİRMELER")
            print("=" * 80)
            for i, issue in enumerate(info, 1):
                self._print_issue(i, issue)

        # Kaynaklar
        print("=" * 80)
        print("🛠️ KULLANILAN TEKNOLOJİLER VE SERVİSLER")
        print("=" * 80)
        print(f"🔗 Bulunan URL'ler: {len(self.urls)}")
        for url in self.urls:
            print(f"  - {url}")
        print()
        print(f"🗄️ Bulunan Veritabanı Bağlantıları: {len(self.db_connections)}")
        for db in self.db_connections:
            print(f"  - {db}") # Güvenlik için bağlantı detaylarını gizle
        print()
        print(f"🧩 Kullanılan Aktiviteler: {len(self.used_activities)}")
        # for activity in sorted(self.used_activities):
        #     print(f"  - {activity}")

        # Özet
        print("=" * 80)
        print("📈 GENEL DEĞERLENDİRME")
        print("=" * 80)

        if len(critical) == 0 and len(warnings) == 0:
            print("✅ Mükemmel! Hiçbir kritik sorun veya uyarı bulunamadı.")
        elif len(critical) == 0:
            print(f"✅ İyi! Kritik sorun yok, ancak {len(warnings)} uyarı var.")
        elif len(critical) <= 2:
            print(f"⚠️  Orta: {len(critical)} kritik sorun ve {len(warnings)} uyarı bulundu.")
        else:
            print(f"🔴 Kötü: {len(critical)} kritik sorun bulundu. Acilen düzeltilmeli!")

        print() 
        print("💡 ÖNERİ: Kritik sorunları önce düzeltin, sonra uyarılara geçin.")
        print("=" * 80)

    def _print_issue(self, index: int, issue: Issue):
        """Tek bir sorunu formatla ve yazdır"""
        print(f"\n#{index} [{issue.category}]")
        print(f"📍 Konum: {issue.location}")
        print(f"📝 Sorun: {issue.description}")
        print(f"💡 Öneri: {issue.suggestion}")
        print("-" * 80)

    def export_to_html(self, output_path: str = "analysis_report.html"):
        """Raporu HTML formatında dışa aktar"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>UiPath XAML Analiz Raporu</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; border-bottom: 3px solid #007acc; padding-bottom: 10px; }}
                h2 {{ color: #333; border-bottom: 2px solid #ccc; padding-bottom: 5px; margin-top: 40px;}}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .summary-box {{ flex: 1; padding: 20px; border-radius: 8px; text-align: center; color: white;}}
                .critical {{ background: #d9534f; }}
                .warning {{ background: #f0ad4e; }}
                .info {{ background: #5bc0de; }}
                .issue {{ margin: 20px 0; padding: 20px; border-left: 4px solid; border-radius: 5px; background: #f9f9f9;}}
                .issue.critical-border {{ border-left-color: #d9534f; }}
                .issue.warning-border {{ border-left-color: #f0ad4e; }}
                .issue.info-border {{ border-left-color: #5bc0de; }}
                .issue h3 {{ margin-top: 0; }}
                .issue-category {{ display: inline-block; padding: 5px 10px; color: white; border-radius: 3px; font-size: 12px; }}
                .category-critical {{ background: #d9534f; }}
                .category-warning {{ background: #f0ad4e; }}
                .category-info {{ background: #5bc0de; }}
                .issue-location {{ color: #666; font-style: italic; }}
                .suggestion {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin-top: 10px; }}
                .resource-list {{ list-style-type: none; padding-left: 0; }}
                .resource-list li {{ background: #eee; padding: 8px 12px; margin-bottom: 5px; border-radius: 3px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 UiPath XAML Analiz Raporu</h1>
                <p><strong>Dosya:</strong> {self.xaml_path.name}</p>

                <div class="summary">
                    <div class="summary-box critical">
                        <h2>{len([i for i in self.issues if i.severity == "CRITICAL"])}</h2>
                        <p>Kritik Sorun</p>
                    </div>
                    <div class="summary-box warning">
                        <h2>{len([i for i in self.issues if i.severity == "WARNING"])}</h2>
                        <p>Uyarı</p>
                    </div>
                    <div class="summary-box info">
                        <h2>{len([i for i in self.issues if i.severity == "INFO"])}</h2>
                        <p>Bilgilendirme</p>
                    </div>
                </div>
        """

        # Sorunlar
        sections = {{"CRITICAL": "🔴 Kritik Sorunlar", "WARNING": "⚠️ Uyarılar", "INFO": "ℹ️ Bilgilendirmeler"}}
        for severity, title in sections.items():
            issues = [i for i in self.issues if i.severity == severity]
            if issues:
                html_content += f"<h2>{{title}}</h2>"
                for issue in issues:
                    html_content += f"""
                        <div class="issue {{severity.lower()}}-border">
                            <span class="issue-category category-{{severity.lower()}}">{{issue.category}}</span>
                            <h3>{{issue.description}}</h3>
                            <p class="issue-location">📍 {{issue.location}}</p>
                            <div class="suggestion">
                                <strong>💡 Öneri:</strong> {{issue.suggestion}}
                            </div>
                        </div>
                    """

        # Kaynaklar
        html_content += "<h2>🛠️ Kullanılan Teknolojiler ve Servisler</h2>"
        html_content += f"<h3>🔗 Bulunan URL'ler ({len(self.urls)})</h3>"
        if self.urls:
            html_content += "<ul class='resource-list'>"
            for url in self.urls:
                html_content += f"<li>{{url}}</li>"
            html_content += "</ul>"

        html_content += f"<h3>🗄️ Bulunan Veritabanı Bağlantıları ({len(self.db_connections)})</h3>"
        if self.db_connections:
            html_content += "<ul class='resource-list'>"
            for db in self.db_connections:
                html_content += f"<li>{{db}}</li>"
            html_content += "</ul>"

        html_content += f"<h3>🧩 Kullanılan Aktiviteler ({len(self.used_activities)})</h3>"
        if self.used_activities:
            html_content += "<ul class='resource-list'>"
            for activity in sorted(self.used_activities):
                html_content += f"<li>{{activity}}</li>"
            html_content += "</ul>"


        html_content += """
            </div>
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n✅ HTML raporu oluşturuldu: {output_path}")


# KULLANIM
if __name__ == "__main__":
    # Analiz edilecek XAML dosyalarının bulunduğu klasör
    xaml_folder = "xaml_files"

    # Klasördeki tüm .xaml dosyalarını bul
    xaml_files = list(Path(xaml_folder).glob("*.xaml"))

    if not xaml_files:
        print(f"'{xaml_folder}' klasöründe .xaml dosyası bulunamadı.")
    else:
        for xaml_file in xaml_files:
            print(f"--- Analiz ediliyor: {xaml_file.name} ---")
            # Analiz et
            analyzer = UiPathXAMLAnalyzer(xaml_file)
            analyzer.analyze()

            # Her dosya için ayrı bir HTML raporu oluştur (opsiyonel)
            report_filename = f"report_{{xaml_file.stem}}.html"
            analyzer.export_to_html(report_filename)
