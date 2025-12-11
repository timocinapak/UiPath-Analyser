# 📋 UiPath Workflow Analiz Raporu

**Oluşturma Tarihi**: 2025-12-11 15:00:38

---


## 📊 Özet

| Metrik | Değer |
|--------|-------|
| **Workflow Adı** | BMI Automation |
| **Sağlık Skoru** | 🟡 65.0/100 |
| **Toplam Aktivite** | 50 |
| **Toplam Değişken** | 3 |
| **Tespit Edilen Sorun** | 4 |
| **İyileştirme Önerisi** | 5 |


## 🎯 İş Akışı Amacı

Proje: BMI Automation
Açıklama: Blank Process
- **Web Automation**: Browser'da UI otomasyonu yapılıyor
- **Excel İşleme**: Excel dosyalarıyla veri işleme yapılıyor
- **Toplu İşleme**: Veri setinin her satırı üzerinde işlem yapılıyor
- **Koşullu İşleme**: Koşullara göre farklı işlemler uygulanıyor



## 📌 Aktiviteler

**Toplam: 50**

### Sequence (14)
- **Main Sequence**: Adımları sırasıyla çalıştırır
- **Fetch Data**: Adımları sırasıyla çalıştırır
- **Do**: Adımları sırasıyla çalıştırır
- **Do**: Adımları sırasıyla çalıştırır
- **Calculate**: Adımları sırasıyla çalıştırır
- **Do**: Adımları sırasıyla çalıştırır
- **Body**: Adımları sırasıyla çalıştırır
- **Do**: Adımları sırasıyla çalıştırır
- **CAlculate BMI**: Adımları sırasıyla çalıştırır
- **Then**: Adımları sırasıyla çalıştırır
- **Else**: Adımları sırasıyla çalıştırır
- **Do**: Adımları sırasıyla çalıştırır
- **Write output**: Adımları sırasıyla çalıştırır
- **Do**: Adımları sırasıyla çalıştırır

### Flowchart (1)
- **Unknown**: Flowchart mantığını kontrol eder

### ExcelProcessScopeX (2)
- **Excel Process Scope**: Bilinmeyen aktivite
- **Excel Process Scope**: Bilinmeyen aktivite

### ExcelProcessScopeX.Body (2)
- **Unknown**: Bilinmeyen aktivite
- **Unknown**: Bilinmeyen aktivite

### ExcelApplicationCard (2)
- **Use Excel File**: Excel dosyasını açar ve işler
- **Use Excel File**: Excel dosyasını açar ve işler

### ExcelApplicationCard.Body (2)
- **Unknown**: Bilinmeyen aktivite
- **Unknown**: Bilinmeyen aktivite

### WriteCellX (2)
- **Write Cell**: Bilinmeyen aktivite
- **Write Cell**: Bilinmeyen aktivite

### SaveExcelFileX (2)
- **Save Excel File**: Bilinmeyen aktivite
- **Save Excel File**: Bilinmeyen aktivite

### ReadRange (1)
- **Read Range Workbook**: Excel alanını okur

### ForEachRow (1)
- **For Each Row in Data Table**: Veri tablosunun her satırında döngü yapar

### NTypeInto (3)
- **Type Into 'Age'**: UI elementine metin yazı
- **Type Into 'Age'**: UI elementine metin yazı
- **Type Into 'Age'**: UI elementine metin yazı

### NTypeInto.Target (3)
- **Unknown**: Bilinmeyen aktivite
- **Unknown**: Bilinmeyen aktivite
- **Unknown**: Bilinmeyen aktivite

### NTypeInto.VerifyOptions (3)
- **Unknown**: Bilinmeyen aktivite
- **Unknown**: Bilinmeyen aktivite
- **Unknown**: Bilinmeyen aktivite

### If (1)
- **Unknown**: Koşullu branş oluşturur

### NClick (3)
- **Click 'SPAN'**: UI elementine tıklar
- **Click 'SPAN'**: UI elementine tıklar
- **Click 'Calculate'**: UI elementine tıklar

### NClick.Target (3)
- **Unknown**: Bilinmeyen aktivite
- **Unknown**: Bilinmeyen aktivite
- **Unknown**: Bilinmeyen aktivite

### NClick.VerifyOptions (3)
- **Unknown**: Bilinmeyen aktivite
- **Unknown**: Bilinmeyen aktivite
- **Unknown**: Bilinmeyen aktivite

### NGetText (1)
- **Get Text 'BMI ='**: UI elementinden metin okur

### NGetText.Target (1)
- **Unknown**: Bilinmeyen aktivite



## 🔤 Değişkenler

**Toplam: 3**

- `Unknown (Unknown)`
- `table (sd:DataTable)`
- `BMI_output (x:String)`


## ⚠️ Tespit Edilen Sorunlar

**Toplam: 4**

### 🟠 High (1)

**Error Handler Eksikliği**
- **Kategori**: Error Handling
- **Yer**: Ana Sequence
- **Problem**: Workflow'ta Try-Catch bloku bulunmamaktadır. Hata durumunda workflow başarısız olabilir.
- **Çözüm**: Try-Catch bloğu ekleyerek hata yönetimini iyileştirin.

### 🟡 Medium (1)

**Loop içinde UI Otomasyonu**
- **Kategori**: Performance
- **Yer**: Calculate Sequence
- **Problem**: ForEachRow döngüsü içinde UI otomasyonu yapılmaktadır. Bu, workflow'ün çok yavaş çalışmasına neden olabilir.
- **Çözüm**: Mümkünse UI işlemlerini optimize edin veya batch işleme kullanın.

### 🟢 Low (2)

**Kullanılmayan Değişken**
- **Kategori**: Code Quality
- **Yer**: Değişken Tanımı
- **Problem**: Değişken "Unknown" tanımlanmış ancak kullanılmamış.
- **Çözüm**: Kullanılmayan "Unknown" değişkenini silin veya kullanın.

**DisplayName Eksikliği**
- **Kategori**: Best Practice
- **Yer**: Çeşitli Aktiviteler
- **Problem**: 19 aktivitenin DisplayName özelliği ayarlanmamıştır.
- **Çözüm**: Tüm aktivitelere açıklayıcı DisplayName değerleri ekleyin.



## 💡 İyileştirme Önerileri

1. 🔧 **Error Handling Ekleyin**: Try-Catch bloğu kullanarak runtime hatalarını yakalayın.
2. 📝 **Logging Ekleyin**: İş akışının çalışma durumunu izlemek için Log Message aktiviteleri ekleyin.
3. 📌 **Variable Scoping**: Değişkenlerin sadece gerekli scope'ta tanımlanmasını sağlayın.
4. ⚙️ **Parametreleştirme**: Hardcoded değerler yerine config dosyası kullanın (Config File Activity).
5. 📊 **Monitoring**: Business Process Analytics (BPA) ile workflow performansını izleyin.


## 📦 Bağımlılıklar

- `UiPath.Excel.Activities`: [2.23.4]
- `UiPath.Mail.Activities`: [1.23.1]
- `UiPath.System.Activities`: [24.10.3]
- `UiPath.Testing.Activities`: [24.10.0]
- `UiPath.UIAutomation.Activities`: [24.10.0]
