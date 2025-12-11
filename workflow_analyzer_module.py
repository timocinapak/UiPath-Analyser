"""
UiPath Workflow Analyzer Module

UiPath .xaml ve .json dosyalarını analiz eden kütüphane
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class Issue:
    """Tespit edilen sorun"""
    severity: str  # "Critical", "High", "Medium", "Low"
    category: str
    title: str
    description: str
    location: str
    solution: str


@dataclass
class Activity:
    """Workflow aktivitesi"""
    name: str
    type: str
    purpose: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    is_error_handled: bool = False


@dataclass
class WorkflowAnalysis:
    """Workflow analiz sonuçları"""
    workflow_name: str
    workflow_purpose: str
    activities: List[Activity] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    issues: List[Issue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    overall_health_score: float = 0.0
    urls: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    prose_summary: str = ""


class XAMLParser:
    """XAML dosyasını parse eden sınıf"""
    
    def __init__(self, xaml_path: str):
        self.xaml_path = xaml_path
        self.tree = None
        self.root = None
        self.raw_content = ""
    
    def parse(self) -> bool:
        """XAML dosyasını parse et"""
        try:
            with open(self.xaml_path, 'r', encoding='utf-8') as f:
                self.raw_content = f.read()
            self.root = ET.fromstring(self.raw_content)
            self.tree = ET.ElementTree(self.root)
            return True
        except Exception as e:
            print(f"❌ XAML parse hatası: {e}")
            return False
    
    def get_activities(self) -> List[Dict[str, Any]]:
        """Tüm aktiviteleri çıkar"""
        activities = []
        
        if not self.root:
            return activities
        
        for elem in self.root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag in ['Sequence', 'Flowchart', 'ForEachRow', 'If', 'While', 
                      'NClick', 'NTypeInto', 'NGetText', 'ReadRange', 'WriteCell',
                      'ExcelApplicationCard', 'ExcelProcessScope', 'SaveExcelFile',
                      'TryCatch', 'LogMessage', 'OpenBrowser', 'AttachBrowser']:
                activities.append({
                    'type': tag,
                    'name': elem.get('DisplayName', 'Unknown'),
                    'attributes': dict(elem.attrib)
                })
        
        return activities
    
    def get_variables(self) -> List[Tuple[str, str]]:
        """Tüm değişkenleri çıkar"""
        variables = []
        
        if not self.root:
            return variables
        
        for elem in self.root.iter():
            if 'Variable' in elem.tag:
                name = elem.get('Name', 'Unknown')
                var_type = elem.get('{http://schemas.microsoft.com/winfx/2006/xaml}TypeArguments', 'Unknown')
                variables.append((name, var_type))
        
        return variables

    def get_urls(self) -> List[str]:
        """Aktivite niteliklerinden tüm URL'leri çıkar."""
        urls = set()
        if not self.root:
            return []
        
        url_attributes = ['Url', 'Uri', 'Endpoint']

        for elem in self.root.iter():
            for attr_name, attr_value in elem.attrib.items():
                if any(url_attr in attr_name for url_attr in url_attributes):
                    if attr_value.startswith('http://') or attr_value.startswith('https://'):
                        urls.add(attr_value)
                
                if isinstance(attr_value, str) and (attr_value.startswith('http://') or attr_value.startswith('https://')):
                    urls.add(attr_value)

        for elem in self.root.iter('{http://schemas.microsoft.com/winfx/2006/xaml}String'):
             if elem.text and (elem.text.startswith('http://') or elem.text.startswith('https://')):
                urls.add(elem.text)

        return sorted(list(urls))


class JSONConfigParser:
    """Project.json dosyasını parse eden sınıf"""
    
    def __init__(self, json_path: str | None = None):
        self.json_path = json_path
        self.config = {}
    
    def parse(self) -> bool:
        """JSON dosyasını parse et"""
        if not self.json_path:
            return True
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except FileNotFoundError:
            # Dosya bulunamazsa sorun değil, sadece boş bir yapılandırma kullan.
            return True
        except json.JSONDecodeError:
            print(f"⚠️ JSON dosyası çözümlenemedi: {self.json_path}")
            return True # Bozuk JSON durumunda bile devam et
        except Exception as e:
            print(f"❌ JSON parse hatası: {e}")
            return False
    
    def get_project_info(self) -> Dict[str, Any]:
        """Proje bilgilerini al"""
        if not self.config:
            return {}
        
        return {
            'name': self.config.get('name', 'Unknown'),
            'description': self.config.get('description', ''),
            'version': self.config.get('projectVersion', ''),
        }
    
    def get_dependencies(self) -> Dict[str, str]:
        """Dependency'leri al"""
        if not self.config:
            return {}
        return self.config.get('dependencies', {})


class WorkflowAnalyzer:
    """Detaylı workflow analizi yapan sınıf"""
    
    def __init__(self, xaml_parser: XAMLParser, json_parser: JSONConfigParser):
        self.xaml_parser = xaml_parser
        self.json_parser = json_parser
        self.analysis = None
    
    def analyze(self) -> WorkflowAnalysis:
        """Detaylı analiz yap"""
        project_info = self.json_parser.get_project_info()
        activities = self._extract_activities()
        components = sorted(list(set(act.type for act in activities)))
        
        self.analysis = WorkflowAnalysis(
            workflow_name=project_info.get('name', 'Unknown'),
            workflow_purpose=self._detect_workflow_purpose(),
            activities=activities,
            variables=self._extract_variables(),
            dependencies=self.json_parser.get_dependencies(),
            urls=self.xaml_parser.get_urls(),
            components=components
        )
        
        self.analysis.prose_summary = self._generate_prose_summary()
        self.analysis.issues = self._detect_issues()
        self.analysis.recommendations = self._generate_recommendations()
        self.analysis.overall_health_score = self._calculate_health_score()
        
        return self.analysis
    
    def _generate_prose_summary(self) -> str:
        """Analiz edilen aktivitelere dayanarak iş akışının düz metin bir özetini oluşturur."""
        if not self.analysis or not self.analysis.activities:
            return "İş akışı hakkında bir özet oluşturmak için yeterli aktivite bulunamadı."

        activity_types = set(act.type for act in self.analysis.activities)
        
        summary_parts = []
        
        # Identify the main category of the workflow
        is_web_automation = any(t in activity_types for t in ['OpenBrowser', 'NClick', 'NTypeInto', 'NGetText', 'Click', 'TypeInto', 'GetText', 'UseApplicationBrowser'])
        is_excel_automation = any(t in activity_types for t in ['ReadRange', 'WriteCell', 'ExcelApplicationCard', 'ExcelProcessScope', 'UseExcelFile'])
        is_data_processing = 'ForEachRow' in activity_types
        
        # Start the summary
        if is_web_automation and is_excel_automation:
            summary_parts.append("Bu iş akışı, bir Excel dosyasındaki verileri okuyup bu verileri bir web uygulamasına giren veya web'den alıp Excel'e yazan karma bir otomasyon süreci gibi görünmektedir.")
        elif is_web_automation:
            summary_parts.append("Bu iş akışı, bir web sitesi veya masaüstü uygulamasıyla etkileşime giren bir UI otomasyonu sürecidir.")
        elif is_excel_automation:
            summary_parts.append("Bu iş akışı, bir Excel dosyası üzerinde okuma, yazma veya düzenleme işlemleri yapan bir otomasyon sürecidir.")
        else:
            summary_parts.append("Bu, tanımlanmış adımları belirli bir sırada yürüten genel bir iş akışıdır.")

        # Describe the process flow
        if 'OpenBrowser' in activity_types or 'UseApplicationBrowser' in activity_types:
            summary_parts.append("Süreç, bir web tarayıcısı açarak veya mevcut bir tarayıcıyı kullanarak başlar.")
        elif 'ExcelApplicationCard' in activity_types or 'ExcelProcessScope' in activity_types or 'UseExcelFile' in activity_types:
            summary_parts.append("Süreç, bir Excel dosyasıyla çalışarak başlar.")

        if is_data_processing:
            summary_parts.append("Ardından, bir veri tablosundaki her satır için bir dizi eylemi döngüsel olarak tekrar eder.")
        
        # Mention specific common actions
        actions = set()
        if any(t in activity_types for t in ['NClick', 'Click']):
            actions.add("butonlara tıklama")
        if any(t in activity_types for t in ['NTypeInto', 'TypeInto']):
            actions.add("form alanlarına veri girme")
        if any(t in activity_types for t in ['NGetText', 'GetText']):
            actions.add("ekrandan metin okuma")
        if 'ReadRange' in activity_types:
            actions.add("Excel'den toplu veri okuma")
        if 'WriteCell' in activity_types:
            actions.add("Excel'e tekil veri yazma")
            
        if actions:
            summary_parts.append(f"Temel işlemler arasında {', '.join(actions)} gibi eylemler bulunmaktadır.")

        # Mention error handling
        if 'TryCatch' in activity_types:
            summary_parts.append("İş akışı, olası hataları yönetmek için hata yakalama blokları ('Try Catch') içermektedir, bu da onu çalışma zamanı hatalarına karşı daha dayanıklı kılar.")
            
        # Conclude
        summary_parts.append("Bu özet, aktivite türlerine dayalı otomatik bir çıkarımdır ve iş akışının karmaşık mantığını tam olarak yansıtmayabilir.")
        
        return " ".join(summary_parts)

    def _detect_workflow_purpose(self) -> str:
        """İş akışının amacını algıla"""
        project_info = self.json_parser.get_project_info()
        purpose = f"Proje: {project_info.get('name', 'Unknown')}\n"
        
        activities = self.xaml_parser.get_activities()
        activity_types = set(act['type'] for act in activities)
        
        if any(x in str(activity_types) for x in ['NClick', 'NTypeInto', 'NGetText']):
            purpose += "- Web Automation\n"
        if any(x in str(activity_types) for x in ['ReadRange', 'WriteCell']):
            purpose += "- Excel İşleme\n"
        if 'ForEachRow' in str(activity_types):
            purpose += "- Toplu İşleme\n"
        
        return purpose
    
    def _extract_activities(self) -> List[Activity]:
        """Aktiviteleri çıkar"""
        activities = []
        xaml_activities = self.xaml_parser.get_activities()
        
        for act in xaml_activities:
            activity = Activity(
                name=act['name'],
                type=act['type'],
                purpose=self._get_activity_purpose(act['type'])
            )
            activities.append(activity)
        
        return activities
    
    def _get_activity_purpose(self, activity_type: str) -> str:
        """Aktivite türüne göre amacını açıkla"""
        purposes = {
            'Sequence': 'Adımları sırasıyla çalıştırır',
            'ForEachRow': 'Veri tablosunun her satırında döngü yapar',
            'NClick': 'UI elementine tıklar',
            'NTypeInto': 'UI elementine metin yazı',
            'NGetText': 'UI elementinden metin okur',
            'ReadRange': 'Excel alanını okur',
        }
        return purposes.get(activity_type, 'Bilinmeyen aktivite')
    
    def _extract_variables(self) -> List[str]:
        """Değişkenleri çıkar"""
        variables = self.xaml_parser.get_variables()
        return [f"{name} ({var_type})" for name, var_type in variables]
    
    def _detect_issues(self) -> List[Issue]:
        """Sorunları tespit et"""
        issues = []
        activities = self.xaml_parser.get_activities()
        
        if not any(act['type'] == 'TryCatch' for act in activities) and len(activities) > 5:
            issues.append(Issue(
                severity='High',
                category='Error Handling',
                title='Error Handler Eksikliği',
                description='İş akışında hiçbir "Try Catch" aktivitesi bulunmamaktadır. Bu durum, beklenmedik hataların süreci tamamen durdurmasına neden olabilir.',
                location='Genel İş Akışı',
                solution='Projenin ana adımlarını veya hata potansiyeli taşıyan (örn: UI etkileşimleri, API çağrıları) kısımları "Try Catch" blokları içine alarak hata yönetimini iyileştirin.'
            ))
        
        issues.extend(self._check_for_improper_error_logging())
        issues.extend(self._find_logic_flaws())
        
        return issues

    def _check_for_improper_error_logging(self) -> List[Issue]:
        """
        Hata yakalama blokları ('Catch') içindeki yanlış seviyede loglama
        (örn: 'Error' yerine 'Info' kullanma) aktivitelerini tespit eder.
        """
        issues = []
        root = self.xaml_parser.root
        if root is None:
            return issues
        
        # Find all TryCatch activities using a namespace-agnostic search
        for trycatch_element in root.findall('.//{*}TryCatch'):
            # Find the Catches section
            catches_element = trycatch_element.find('{*}TryCatch.Catches')
            if catches_element is None:
                continue

            # Iterate through each Catch block
            for catch_element in catches_element:
                if not catch_element.tag.endswith('Catch'):
                    continue
                
                # Find LogMessage activities within this Catch
                for log_message_element in catch_element.iterfind('.//{*}LogMessage'):
                    log_level = log_message_element.get('Level')
                    
                    # Default level is Info if not specified.
                    # We consider 'Info' and 'Trace' as incorrect for logging errors.
                    if log_level is None or any(level in str(log_level) for level in ['Info', 'Trace']):
                        log_name = log_message_element.get('DisplayName', 'Log Message')
                        try_catch_name = trycatch_element.get('DisplayName', 'Try Catch')
                        
                        issues.append(Issue(
                            severity='Medium',
                            category='Logging',
                            title='Hatalı Loglama Seviyesi',
                            description=f"'{try_catch_name}' aktivitesinin hata yakalama (Catch) bloğunda, bir hata durumu '{log_name}' aktivitesi ile 'Info' veya 'Trace' seviyesinde loglanıyor. Bu durum, gerçek hataların gözden kaçmasına neden olabilir.",
                            location=f"TryCatch: '{try_catch_name}' -> Catch bloğu",
                            solution=f"İlgili '{log_name}' aktivitesinin 'Level' özelliğini 'Warn' veya 'Error' olarak değiştirerek hatanın ciddiyetini doğru şekilde yansıtın."
                        ))
        return issues

    def _find_logic_flaws(self) -> List[Issue]:
        """İş akışındaki potansiyel mantık hatalarını tespit eder."""
        issues = []
        root = self.xaml_parser.root
        if root is None:
            return issues

        issues.extend(self._find_empty_blocks(root))
        issues.extend(self._find_unused_variables())

        return issues

    def _find_empty_blocks(self, root: ET.Element) -> List[Issue]:
        """Boş Try, Catch, If/Then/Else bloklarını bulur."""
        issues = []
        # Check for empty Try/Catch
        for trycatch_element in root.findall('.//{*}TryCatch'):
            tc_name = trycatch_element.get('DisplayName', 'Try Catch')
            
            try_element = trycatch_element.find('{*}TryCatch.Try')
            if try_element is None or len(try_element) == 0:
                issues.append(Issue(
                    severity='Medium', category='Logic Error', title='Boş Try Bloğu',
                    description=f"'{tc_name}' aktivitesinin 'Try' bölümü boş. İçinde aktivite olmayan bir 'Try' bloğu bir işe yaramaz.",
                    location=f"TryCatch: '{tc_name}'",
                    solution="'Try' bloğuna çalıştırılacak aktiviteleri ekleyin veya bu 'TryCatch' aktivitesini kaldırın."
                ))
                
            catches_element = trycatch_element.find('{*}TryCatch.Catches')
            if catches_element is not None:
                for catch_element in catches_element:
                    action = catch_element.find('{*}ActivityAction')
                    if action is None or len(action) == 0 or (len(action) == 1 and len(action[0]) == 0):
                         issues.append(Issue(
                            severity='High', category='Logic Error', title='Boş Catch Bloğu',
                            description=f"'{tc_name}' aktivitesindeki bir 'Catch' bloğu boş. Hataları sessizce yutmak, hata ayıklamayı imkansız hale getirir ve beklenmedik davranışlara yol açar.",
                            location=f"TryCatch: '{tc_name}'",
                            solution="Hata durumunda ne yapılması gerektiğini belirtin. En azından hatayı 'Log Message' (Error seviyesiyle) ile loglayın."
                        ))

        # Check for empty If/Then/Else
        for if_element in root.findall('.//{*}If'):
            if_name = if_element.get('DisplayName', 'If')
            
            then_element = if_element.find('{*}If.Then')
            if then_element is None or len(then_element) == 0 or (len(then_element) == 1 and len(then_element[0]) == 0):
                issues.append(Issue(
                    severity='Low', category='Logic Error', title='Boş Then Bloğu',
                    description=f"'{if_name}' aktivitesinin 'Then' (O zaman) bölümü boş. Bu, tamamlanmamış bir mantığa işaret ediyor olabilir.",
                    location=f"If: '{if_name}'",
                    solution="Koşul doğru olduğunda çalıştırılacak mantığı 'Then' bloğuna ekleyin veya 'If' koşulunu yeniden değerlendirin."
                ))
                
            else_element = if_element.find('{*}If.Else')
            if else_element is not None and len(else_element) == 0:
                 issues.append(Issue(
                    severity='Low', category='Logic Error', title='Boş Else Bloğu',
                    description=f"'{if_name}' aktivitesinin 'Else' (Değilse) bölümü boş. Bu bir hata olmasa da, genellikle gereksiz bir daldır.",
                    location=f"If: '{if_name}'",
                    solution="Eğer 'Else' durumu için bir mantık gerekmiyorsa, bu bloğu boş bırakmak yerine tamamen kaldırın."
                ))
        return issues
    
    def _find_unused_variables(self) -> List[Issue]:
        """Kullanılmayan değişkenleri bulur."""
        issues = []
        variables = self.xaml_parser.get_variables()
        xaml_content = self.xaml_parser.raw_content

        if not variables:
            return issues
            
        for var_name, var_type in variables:
            # The variable must appear at least twice: 1 for declaration, 1+ for usage.
            # We use regex with word boundaries (\b) to avoid matching substrings.
            occurrences = re.findall(r'\b' + re.escape(var_name) + r'\b', xaml_content)
            
            if len(occurrences) <= 1:
                issues.append(Issue(
                    severity='Low',
                    category='Code Smell',
                    title='Kullanılmayan Değişken',
                    description=f"'{var_name}' ({var_type}) değişkeni tanımlanmış ancak iş akışının hiçbir yerinde kullanılmamış.",
                    location='Değişkenler Paneli',
                    solution=f"Eğer bu değişkene gerçekten ihtiyaç yoksa, kodun daha temiz ve anlaşılır olması için kaldırın."
                ))
                
        return issues
    
    def _generate_recommendations(self) -> List[str]:
        """Detaylı iyileştirme önerileri üret"""
        recommendations = []
        activities = self.xaml_parser.get_activities()

        # 1. Error Handling Recommendation
        if not any(act['type'] == 'TryCatch' for act in activities) and len(activities) > 5:
            recommendations.append(
                "Global Error Handling Ekleyin: Projenin ana adımlarını bir 'Try Catch' aktivitesi içine alarak beklenmedik hatalara karşı (örn: uygulama çökmeleri, selektör bulunamaması) projenizi daha dayanıklı hale getirin. 'Catch' bölümünde hatayı loglayıp, süreci kontrollü bir şekilde sonlandırabilir veya alternatif bir akış başlatabilirsiniz."
            )

        # 2. Logging Recommendation
        if not any(act['type'] == 'LogMessage' for act in activities):
            recommendations.append(
                "Süreç Takibi için Loglama Yapın: İş akışının başlangıcına ve sonuna 'Log Message' (Level: Info) ekleyerek sürecin ne zaman başlayıp bittiğini ve ne kadar sürdüğünü takip edin. Ayrıca, önemli adımlardan (örn: bir dosyayı işledikten sonra, bir API çağrısından önce) sonra loglama yapmak, hata ayıklamayı büyük ölçüde kolaylaştırır."
            )
        elif len([act for act in activities if act['type'] == 'LogMessage']) < 3:
             recommendations.append(
                "Loglamayı Detaylandırın: Mevcut loglama yetersiz olabilir. 'Catch' blokları içinde hatanın detayını (Exception.Message, Exception.Source) 'Log Message' (Level: Error) ile logladığınızdan emin olun. Ayrıca, iş akışındaki kritik parametreleri ve karar noktalarını da loglayarak sürecin akışını daha şeffaf hale getirin."
            )

        # 3. Timeout Settings Recommendation
        ui_activity_types = ['Click', 'TypeInto', 'NClick', 'NTypeInto', 'NGetText', 'OpenBrowser', 'AttachBrowser', 'UseApplicationBrowser']
        activities_to_check = [act for act in activities if act['type'] in ui_activity_types]
        
        if activities_to_check:
            acts_without_timeout = []
            for act in activities_to_check:
                # Modern activities use TimeoutMS, classic may use Timeout.
                if 'TimeoutMS' not in act['attributes'] and 'Timeout' not in act['attributes']:
                    acts_without_timeout.append(f"'{act['name']}'")
            
            if acts_without_timeout:
                recommendations.append(
                    f"Zaman Aşımı (Timeout) Ayarlarını Belirtin: {', '.join(acts_without_timeout)} gibi UI etkileşim aktivitelerinde özel bir timeout değeri belirtilmemiş. Hedef uygulamanın yavaş yanıt vermesi durumunda robotun gereksiz yere uzun süre beklemesini veya erken hata vermesini önlemek için bu aktivitelere makul bir 'TimeoutMS' değeri (örn: 10000 for 10s) atayın."
                )
            else:
                 recommendations.append(
                    "Zaman Aşımı (Timeout) Ayarlarını Gözden Geçirin: Tüm UI aktivitelerinde timeout değeri belirtilmiş olsa da, bu değerlerin uygulamanın gerçek performansına uygun olup olmadığını kontrol edin. Çok kısa timeoutlar stabilite sorunlarına, çok uzun timeoutlar ise performans düşüşüne neden olabilir."
                )

        if not recommendations:
            return [
                "Genel bir iyileştirme önerisi bulunamadı. Kodunuz iyi görünüyor!",
            ]

        return recommendations
    
    def _calculate_health_score(self) -> float:
        """Workflow sağlık skorunu hesapla"""
        score = 100.0
        for issue in self.analysis.issues:
            if issue.severity == 'High':
                score -= 15
            elif issue.severity == 'Medium':
                score -= 10
        return max(0, score)


def analyze_workflow(xaml_path: str) -> WorkflowAnalysis:
    """
    Workflow'u analiz et ve sonuçları döndür
    
    Args:
        xaml_path: XAML dosyasının yolu
    
    Returns:
        WorkflowAnalysis: Analiz sonuçları
    """
    xaml_parser = XAMLParser(xaml_path)
    if not xaml_parser.parse():
        raise ValueError(f"XAML dosyası parse edilemedi: {xaml_path}")
    
    # JSON yapılandırması olmadan devam etmek için sahte bir JSON ayrıştırıcı oluştur
    json_parser = JSONConfigParser()
    json_parser.parse()
    
    analyzer = WorkflowAnalyzer(xaml_parser, json_parser)
    return analyzer.analyze()
