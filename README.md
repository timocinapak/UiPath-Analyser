# 🚀 UiPath Workflow Analyzer - Complete Suite

Comprehensive UiPath workflow analysis tool with Jupyter Notebook, Python module, CLI tool, and **Streamlit web application**.

## 📦 What's Included

### 1. **Streamlit Web App** (`app.py`) ⭐ NEW
Interactive web interface with file upload, real-time analysis, and multi-format export:
- 🔍 Drag-and-drop file upload
- 📊 Real-time workflow analysis
- 📋 Multiple tabs (Overview, Activities, Issues, Recommendations, Export)
- 📥 Export to Markdown, PDF, JSON
- 💾 PDF reports with professional formatting
- 🎨 Interactive issue filtering and visualization

### 2. **Jupyter Notebook** (`workflow_analyzer.ipynb`)
Interactive analysis environment with 9 sections:
- XAML and JSON parsing
- Workflow analysis engine
- Report generation
- Interactive visualizations

### 3. **Python Module** (`workflow_analyzer_module.py`)
Reusable library for integration:
- XAMLParser class
- JSONConfigParser class
- WorkflowAnalyzer class
- analyze_workflow() function

### 4. **CLI Tool** (`analyze_workflow.py`)
Command-line interface for batch processing:
```bash
python analyze_workflow.py <xaml> <json> --output <report.md>
```

## ✨ Temel Özellikler

### 🌐 Streamlit Web Application
- 📤 Dosya yükleme (Sürükle-bırak desteği)
- 📊 Gerçek zamanlı analiz
- 🎨 5 sekmeli arayüz:
  - **Genel Bakış**: Sağlık skoru, amaç, değişkenler, bağımlılıklar
  - **Aktiviteler**: Aktivite türü dökümü, istatistikler
  - **Sorunlar**: Ciddilik filtreleme, renk kodlu gösterim
  - **Öneriler**: Eylem alınabilir iyileştirme önerileri
  - **Dışa Aktar**: Markdown, PDF, JSON indirme
- 📄 PDF rapor oluşturma (ReportLab)
- 💾 Verileri JSON/Markdown olarak dışa aktarma

### 🎯 Analiz Yetenekleri
✅ **XAML Parse Etme**: UiPath workflow dosyalarını ayrıştırır
✅ **JSON Konfigürasyon**: Proje ayarlarını ve dependency'leri okur
✅ **İş Akışı Analizi**: Workflow'un amacını ve işlevini açıklar
✅ **Hata Tespiti**: 4 kategoride sorun algılar (Hata Yönetimi, Performans, İyi Uygulamalar, Güvenlik)
✅ **Ciddilik Seviyeleri**: Düşük, Orta, Yüksek, Kritik
✅ **Sağlık Skoru**: 0-100 arası kalite puanı
✅ **İyileştirme Önerileri**: Eyleme dönüştürülebilir öneriler
✅ **Çoklu Rapor Formatları**: Markdown, PDF, JSON

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Run Streamlit App

**Option 1: Quick Start**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Option 2: Using Launcher Scripts**
```bash
# macOS/Linux
chmod +x run_streamlit.sh
./run_streamlit.sh

# Windows
run_streamlit.bat
```

**Option 3: Custom Port**
```bash
streamlit run app.py --server.port 8502
```

The app opens automatically at `http://localhost:8501`

## 📁 Proje Yapısı

```
UiPath_Code_Analyser/
├── app.py                          # Streamlit web application ⭐
├── workflow_analyzer.ipynb         # Jupyter notebook
├── workflow_analyzer_module.py     # Python module
├── analyze_workflow.py             # CLI tool
├── requirements.txt                # Dependencies
├── run_streamlit.sh               # macOS/Linux launcher
├── run_streamlit.bat              # Windows launcher
├── .streamlit/
│   └── config.toml                # Streamlit config
├── xaml_files/
│   ├── Main.xaml                  # Example workflow
│   └── project.json               # Example config
└── README.md                      # This file
```

## 🔍 Analiz Çıktısı

### Sağlık Skoru Kategorileri

| Skor | Durum | Renk |
|------|-------|------|
| 80-100 | Mükemmel | 🟢 |
| 60-79 | İyi | 🟡 |
| 0-59 | Kötü | 🔴 |

### Sorun Seviyeleri

- **🔴 Critical**: Workflow'un çalışmasını engeller (>25 puan)
- **🟠 High**: Ciddi sorunlar, düzeltilmesi şiddetle tavsiye edilir (15 puan)
- **🟡 Medium**: Orta düzey sorunlar, iyileştirme önerilir (10 puan)
- **🟢 Low**: Küçük sorunlar, temizlik amaçlı (5 puan)

## 📊 BMI Automation Analiz Sonuçları

### Özet
- **Workflow Adı**: BMI Automation
- **Sağlık Skoru**: 🟡 65.0/100
- **Toplam Aktivite**: 50
- **Toplam Değişken**: 3
- **Tespit Edilen Sorun**: 4

### Tespit Edilen Sorunlar

1. **🟠 Error Handler Eksikliği** (High)
   - Workflow'ta Try-Catch bloku yok
   - **Çözüm**: Try-Catch bloğu ekleyerek hata yönetimini iyileştirin

2. **🟡 Loop içinde UI Otomasyonu** (Medium)
   - ForEachRow döngüsü içinde UI otomasyonu yapılıyor
   - **Çözüm**: UI işlemlerini optimize edin veya batch işleme kullanın

3. **🟢 Kullanılmayan Değişkenler** (Low)
   - Tanımlanmış ama kullanılmayan değişkenler var
   - **Çözüm**: Kullanılmayan değişkenleri silin

4. **🟢 DisplayName Eksikliği** (Low)
   - 19 aktivitenin DisplayName özelliği ayarlanmamış
   - **Çözüm**: Tüm aktivitelere açıklayıcı isimler ekleyin

### İyileştirme Önerileri

1. 🔧 **Error Handling Ekleyin**: Try-Catch bloğu kullanarak runtime hatalarını yakalayın
2. 📝 **Logging Ekleyin**: Log Message aktiviteleri ile çalışma durumunu izleyin
3. 📌 **Variable Scoping**: Değişkenleri sadece gerekli scope'ta tanımlayın
4. ⚙️ **Parametreleştirme**: Hardcoded değerler yerine config dosyası kullanın
5. 📊 **Monitoring**: Business Process Analytics (BPA) ile performansı izleyin

## 🛠️ Teknik Detaylar

### Kullanılan Kütüphaneler

- **xml.etree.ElementTree**: XAML dosyalarını parse etmek
- **json**: JSON konfigürasyon dosyalarını okumak
- **pathlib / os**: Dosya işlemleri
- **dataclasses**: Veri modelleri
- **collections**: Veri gruplandırma

### Sistem Mimarisi

```
XAML Dosyası (Main.xaml)
         ↓
    XAMLParser
         ↓
  Aktiviteler, Değişkenler, Error Handlers çıkar
         ↓
    WorkflowAnalyzer
         ↓
  İş akışı amacını belirle, sorunları tespit et, öneriler üret
         ↓
   ReportGenerator
         ↓
Markdown rapor oluştur ve kaydet
```

## 💻 Sistem Gereksinimleri

- Python 3.8+
- Jupyter Notebook (isteğe bağlı)
- Minimum 100MB disk alanı

## 📖 Kullanım Örnekleri

### 1️⃣ Streamlit Web Uygulaması (En Kolay)

```bash
streamlit run app.py
```

Açılan web tarayıcısında:
1. Workflow XAML dosyasını seçin veya sürükleyin
2. JSON dosyasını seçin
3. "Analiz Et" butonuna tıklayın
4. Sonuçları görüntüleyin
5. Markdown, PDF veya JSON olarak dışa aktarın

### 2️⃣ Python Modülü (Programmatic)

```python
from workflow_analyzer_module import analyze_workflow

# Analiz yap
analysis = analyze_workflow(
    xaml_path="xaml_files/Main.xaml",
    json_path="xaml_files/project.json"
)

# Sonuçlara eriş
print(f"Sağlık Skoru: {analysis.overall_health_score}")
print(f"Sorun Sayısı: {len(analysis.issues)}")
print(f"Tavsiye Sayısı: {len(analysis.recommendations)}")

# Aktiviteleri listele
for activity in analysis.activities[:5]:
    print(f"- {activity.name}: {activity.activity_type}")
```

### 3️⃣ Komut Satırı Aracı (Batch İşleme)

```bash
python analyze_workflow.py xaml_files/Main.xaml xaml_files/project.json --output report.md
```

### 4️⃣ Jupyter Notebook (Etkileşimli)

```bash
jupyter notebook workflow_analyzer.ipynb
```

## 🔧 Konfigürasyon

### Streamlit Ayarları (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
port = 8501
maxUploadSize = 200
```

### Özel Port Kullanma

```bash
streamlit run app.py --server.port 9000
```

### Maksimum Dosya Boyutunu Değiştirme

```bash
streamlit run app.py --server.maxUploadSize 500
```

## 🐛 Sorun Giderme

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### "ConnectionRefusedError" Port 8501'de
```bash
# Başka port kullanın
streamlit run app.py --server.port 8502
```

### PDF Export Çalışmıyor
```bash
pip install reportlab>=4.0.0
```

### Dosya Upload Sınırı
- Varsayılan maksimum: 200MB
- Değiştirmek için `.streamlit/config.toml`'da `maxUploadSize` değerini artırın

## 📚 Ek Kaynaklar

- [Streamlit Dokümantasyonu](https://docs.streamlit.io)
- [UiPath Aktiviteleri](https://docs.uipath.com/activities)
- [XAML Formatı Bilgisi](https://www.w3schools.com/xml/)

## 📝 Lisans

Bu proje MIT Lisansı altında sunulmaktadır.

## 👤 Yazar

UiPath Workflow Analyzer - Comprehensive Suite
Türkçe destek ve tamamlanmış Streamlit web uygulaması ile geliştirilen profesyonel analiz aracı.

## 🤝 Katkıda Bulunma

Bug raporları ve özellik istekleri için GitHub Issues'u kullanın.

---

**Son Güncelleme**: 11 Aralık 2025  
**Analyzer Sürümü**: 1.0.0  
**Streamlit App Sürümü**: 1.0.0
