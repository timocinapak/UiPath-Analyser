# 📖 UiPath Workflow Analyzer - Detaylı Kullanım Kılavuzu

## 🎯 Amaç

Bu analyzer, UiPath iş akışlarını otomatik olarak analiz eder ve şunları sağlar:

1. **İş Akışı Amacının Tanımlanması**: Workflow'un ne yaptığını belirler
2. **Hata Tespiti**: Yaygın sorunları ve anti-pattern'leri bulur
3. **Kalite Değerlendirmesi**: 0-100 puan arasında sağlık skoru verir
4. **İyileştirme Önerileri**: Kod kalitesini artırmak için tavsiyelerde bulunur
5. **Detaylı Raporlama**: Markdown formatında kapsamlı rapor oluşturur

---

## 🚀 Başlangıç

### Seçenek 1: Jupyter Notebook Kullanarak

#### 1. Adım: Notebook'u Açın
```bash
cd /Users/timocinapak/Documents/Code\ Repository/UiPath_Code_Analyser
jupyter notebook workflow_analyzer.ipynb
```

#### 2. Adım: Hücreleri Sırasıyla Çalıştırın
- Tüm hücreleri sırasıyla çalıştırmak için: `Kernel → Restart & Run All`
- Veya ayrı ayrı çalıştırmak için: Her hücrede `Shift+Enter` tuşuna basın

#### 3. Adım: Sonuçları İnceleyin
- Analyser, otomatik olarak `workflow_analysis_report.md` raporunu oluşturur
- Jupyter notebook'ta inline sonuçları da görebilirsiniz

### Seçenek 2: Komut Satırı Aracı Kullanarak

```bash
# Temel kullanım (sadece analiz)
python analyze_workflow.py xaml_files/Main.xaml xaml_files/project.json

# Rapor dosyasını kaydet
python analyze_workflow.py xaml_files/Main.xaml xaml_files/project.json --output my_report.md
```

### Seçenek 3: Python Script'te Kullanarak

```python
from workflow_analyzer_module import analyze_workflow

# Workflow'u analiz et
analysis = analyze_workflow(
    xaml_path="xaml_files/Main.xaml",
    json_path="xaml_files/project.json"
)

# Sonuçlara eriş
print(f"Sağlık Skoru: {analysis.overall_health_score}")
print(f"Sorun Sayısı: {len(analysis.issues)}")

# Sorunları listele
for issue in analysis.issues:
    print(f"- [{issue.severity}] {issue.title}")
    print(f"  Çözüm: {issue.solution}")
```

---

## 📊 Rapor Detayları

### 1. Sağlık Skoru (Health Score)

**0-100** arasında bir puandır. Sorun sayısına ve şiddetine göre hesaplanır.

| Skor | Durum | Açıklama |
|------|-------|----------|
| 80-100 | 🟢 Mükemmel | Workflow iyi şekilde tasarlanmış |
| 60-79 | 🟡 İyi | Bazı küçük iyileştirmeler önerilir |
| 40-59 | 🟠 Orta | Ciddi iyileştirmelere ihtiyaç var |
| 0-39 | 🔴 Kötü | Acil iyileştirme gerekli |

### 2. İstatistikler

- **Aktivite Sayısı**: Workflow'ta kaç tane aktivite var
- **Değişken Sayısı**: Tanımlanan değişken sayısı
- **Sorun Sayısı**: Tespit edilen hata ve uyarı sayısı
- **İyileştirme Önerisi**: Verilen tavsiyelerin sayısı

### 3. Tespit Edilen Sorunlar

#### Sorun Seviyeleri

🔴 **Critical** (Kritik)
- Workflow'un hiç çalışmamasına veya çökmesine neden olabilir
- Örn: Yanlış syntax, kayıp referans
- Puanları: -25

🟠 **High** (Yüksek)
- Workflow çalışabilir ama ciddi sorunlar var
- Örn: Error handling yok, deadlock riski
- Puanları: -15

🟡 **Medium** (Orta)
- Workflow çalışıyor ama optimizasyon gerekli
- Örn: Yavaş performans, kötü practices
- Puanları: -10

🟢 **Low** (Düşük)
- Küçük sorunlar, temizlik gerekli
- Örn: Kullanılmayan değişkenler
- Puanları: -5

#### Sorun Kategorileri

1. **Error Handling**: Hata yönetimi ile ilgili sorunlar
2. **Performance**: Performans ve hız sorunları
3. **Code Quality**: Kod kalitesi sorunları
4. **Best Practice**: En iyi pratiklerin uygulanmaması
5. **Security**: Güvenlik sorunları

### 4. İyileştirme Önerileri

Analyzer tarafından otomatik olarak önerilen geliştirmeler:

#### 🔧 Error Handling
```
Try-Catch bloğu ekleyerek runtime hatalarını yakalayın.
Catch bloğunda detaylı log ve notification gönderin.
```

#### 📝 Logging
```
Kritik noktaların başında/sonunda Log Message ekleyin.
Log seviyelerini (Info, Warning, Error) doğru kullanın.
```

#### 📌 Variable Scoping
```
Değişkenleri sadece gerekli scope'ta tanımlayın.
Global değişkenlerin sayısını minimize edin.
```

#### ⚙️ Parametreleştirme
```
Hardcoded değerleri config dosyasına taşıyın.
Environment-specific ayarları dışarıdan geçirin.
```

#### 📊 Monitoring
```
Business Process Analytics (BPA) ile monitore edin.
Key Performance Indicators (KPI) belirleyin.
```

---

## 🔍 BMI Automation Örneği Analiz

### 📋 Proje Özeti

- **Adı**: BMI Automation
- **Amaç**: Excel dosyasından veri okuyup, Web'deki BMI Calculator'da işleme tabi tutmak
- **Teknoloji**: UiPath 24.10 + Excel + Web Automation

### 📊 Bulduğu Sorunlar

#### 1. ❌ Error Handler Eksikliği (High)
```
Problem: Workflow'ta try-catch bloğu yok
Etki: Hata durumunda workflow başarısız olur
Çözüm: Try-Catch bloğu ekleyin
Örnek:
  Try
    - Mevcut işlemler
  Catch (System.Exception)
    - Hata logla
    - Uyarı gönder
    - Gracefully exit
```

#### 2. ⚠️ Loop İçinde UI Otomasyonu (Medium)
```
Problem: ForEachRow içinde UI click/type işlemleri
Etki: Her satır için 2-3 saniye, 100 satır = 5-10 dakika
Çözüm: 
  - Web scraping kullanın
  - Batch işleme geçin
  - Modern API var mı kontrol edin
```

#### 3. 🔹 Kullanılmayan Değişkenler (Low)
```
Problem: Bir değişken tanımlanmış ama kullanılmamış
Çözüm: Temizlik için silin veya gerçekten gerekli mi kontrol edin
```

#### 4. 🔹 DisplayName Eksikliği (Low)
```
Problem: 19 aktivitenin isminin ayarlanmamış
Çözüm: Her aktiviteye açıklayıcı isim ekleyin
Örn: "Type Into 'Height'" yerine "Type Into 'Height (cm)'"
```

### 💡 Verilen Öneriler

1. ✅ Try-Catch bloğu ekleyin
2. ✅ Log Message aktiviteleri ekleyin (başlangıç, loop başı, loop sonu)
3. ✅ Timeout ayarlarını kontrol edin (Web elements için 30 saniye kafidir)
4. ✅ Config dosyası kullanın (URL, file path, timeout değerleri)
5. ✅ Notification gönderme (hata durumunda email veya Teams)

---

## 🛠️ Özel Durumlarda Kullanım

### Aynı Klasördeki Tüm Workflow'ları Analiz Et

```python
from pathlib import Path
from workflow_analyzer_module import analyze_workflow

results = {}
for xaml_file in Path("xaml_files").glob("*.xaml"):
    json_file = xaml_file.parent / "project.json"
    if json_file.exists():
        try:
            analysis = analyze_workflow(str(xaml_file), str(json_file))
            results[xaml_file.name] = analysis
        except:
            print(f"Hata: {xaml_file}")

# Sonuçları göster
for name, analysis in results.items():
    print(f"{name}: {analysis.overall_health_score}/100")
```

### Belirli Tür Sorunları Filtrele

```python
from workflow_analyzer_module import analyze_workflow

analysis = analyze_workflow("xaml_files/Main.xaml", "xaml_files/project.json")

# Sadece High ve Critical sorunları göster
critical_issues = [i for i in analysis.issues if i.severity in ['High', 'Critical']]

print(f"Kritik Sorunlar: {len(critical_issues)}")
for issue in critical_issues:
    print(f"- {issue.title}: {issue.solution}")
```

### Raporu Özel Formatta Oluştur

```python
import json

analysis = analyze_workflow("xaml_files/Main.xaml", "xaml_files/project.json")

# JSON formatında kaydet
report_dict = {
    'name': analysis.workflow_name,
    'health_score': analysis.overall_health_score,
    'issues_count': len(analysis.issues),
    'issues': [
        {
            'title': i.title,
            'severity': i.severity,
            'solution': i.solution
        }
        for i in analysis.issues
    ]
}

with open('report.json', 'w') as f:
    json.dump(report_dict, f, ensure_ascii=False, indent=2)
```

---

## ⚙️ Teknik Detaylar

### Analyzer Mimarisi

```
┌─────────────────────────────┐
│   XAML Dosyası              │
│   (Workflow Tanımı)         │
└──────────────┬──────────────┘
               │
               ▼
        ┌──────────────┐
        │ XAMLParser   │
        │ - Parse      │
        │ - Activities │
        │ - Variables  │
        │ - Handlers   │
        └──────┬───────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌──────────────┐  ┌──────────────┐
│ JSON Parser  │  │WorkflowAnalyzer
│- Project Info│  │- Purpose      │
│- Dependencies│  │- Issues       │
└──────┬───────┘  │- Recommend.   │
       │          │- Score        │
       └────┬─────┘
            │
            ▼
    ┌──────────────────┐
    │ReportGenerator   │
    │- Markdown Report │
    │- Statistics      │
    │- Export          │
    └─────────┬────────┘
              │
              ▼
    ┌──────────────────┐
    │ Report.md        │
    │ (Çıkış)          │
    └──────────────────┘
```

### Tespit Mekanizması

#### 1. Aktivite Taraması
```python
# Tüm XML elementlerini iterate et
for element in root.iter():
    if "TryCatch" in tag:
        error_handlers += 1
    if "DisplayName" not in element.attrib:
        unnamed += 1
```

#### 2. Puan Hesabı
```
Health Score = 100.0
- Her Critical için: -25
- Her High için: -15
- Her Medium için: -10
- Her Low için: -5

Final Score = max(0, Health Score)
```

#### 3. Kategor Belirleme
```
- "Error" in tag → Error Handling
- "Performance" → Performance
- "DisplayName" eksik → Best Practice
- "Unused" → Code Quality
```

---

## 📞 Troubleshooting

### Sorun: "XAML parse hatası"
**Çözüm**: XAML dosyasının geçerli XML olduğunu kontrol edin
```bash
# Linux/Mac
xmllint --noout xaml_files/Main.xaml

# Windows
# NotePad++ ile açıp XML syntax check yapın
```

### Sorun: "JSON parse hatası"
**Çözüm**: JSON dosyası geçerli JSON olmalıdır
```bash
python -m json.tool xaml_files/project.json
```

### Sorun: Notebook'ta kernel hatası
**Çözüm**: Kernel'i restart edin
```
Kernel → Restart Kernel
```

---

## 📝 Best Practices

### Analyzer'ı Düzenli Olarak Çalıştırın
- Her sprint sonunda (agile çalışıyorsanız)
- Production'a geçmeden önce
- Major refactoring sonrası

### Sorunları Önceliklendir
1. **Kritik sorunları** hemen düzelt
2. **Yüksek sorunları** sprint'te planla
3. **Düşük sorunları** backlog'a koy

### Raporları Arşiv Et
```bash
# Workflow versiyonuna göre rapor kaydet
cp workflow_analysis_report.md "reports/v1.0_2025-12-11.md"
```

### Takım ile Paylaş
- Raporu versiyonla (Git, SharePoint, vs)
- Sorunları jira/Azure DevOps'ta açın
- Iyileştirmeleri sprint planning'de tartış

---

## 📚 Kaynaklar

### UiPath Resmi Dokumanlar
- [UiPath Studio Documentation](https://docs.uipath.com)
- [Best Practices Guide](https://docs.uipath.com/studio/docs)
- [Performance Tuning](https://docs.uipath.com/studio/docs)

### Faydalı Linkler
- UiPath Community Forums
- UiPath Academy (eğitim)
- GitHub UiPath örnekleri

---

## 📋 Sürüm Notları

### v1.0.0 (2025-12-11)
- ✅ Başlangıç sürümü
- ✅ XAML/JSON parsing
- ✅ 4 sorun kategorisi
- ✅ Sağlık skoru hesaplaması
- ✅ Markdown rapor generation
- ✅ CLI aracı

### Planlanan Özellikler (v2.0)
- 📋 Invocations analizi
- 🔄 Sub-workflow'lar
- 📊 Detaylı performans analizi
- 🎨 HTML rapor
- 🔗 Workflow dependencies grafiği

---

**Son Güncellenme**: 11 Aralık 2025  
**Sürüm**: 1.0.0  
**Durum**: Üretim Hazır ✅
