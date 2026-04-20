# Pardus Akıllı Tahta Navigasyon Aracı

## Açıklama

Pardus ve ETAP (Etkileşimli Tahta Arayüzü Projesi) kurulu akıllı tahtalarda sunumlar, PDF belgeleri ve web sayfaları arasında geçiş yapmayı kolaylaştırmak amacıyla geliştirilmiş bir yardımcı araçtır. Ekranın en üstünde (always-on-top) sabitlenen küçük bir dikdörtgen widget aracılığıyla, fiziksel klavyeye ihtiyaç duymadan sol ve sağ yön tuşu komutları gönderilmesini sağlar. Dokunmatik ekranlarla tam uyumludur, çerçevesiz tasarımıyla dikkat dağıtmaz ve ekran üzerinde istenilen konuma sürüklenebilir.

## Kullanılan Teknolojiler

- **Python 3:** Uygulama mantığının geliştirilmesi.
- **Tkinter:** Hafif ve hızlı grafik kullanıcı arayüzü (GUI) oluşturma.
- **xdotool:** İşletim sistemi seviyesinde yerel klavye vuruşlarını simüle etme.

- **PyInstaller:** (İsteğe bağlı) Betiği tek bir çalıştırılabilir (binary) dosyaya dönüştürme.

## Kurulum Kılavuzu

Uygulamanın çalışması için sistemde Python 3'ün yanı sıra grafik arayüz kütüphanesi ve klavye simülasyon aracının yüklü olması gerekir.

### Kurulum Gereksinimleri

Pardus terminalini açarak aşağıdaki komutları çalıştırınız:

```bash
sudo apt update
sudo apt install python3 python3-tk xdotool
```

## Uygulamayı Çalıştırma

Kaynak kodu üzerinden çalıştırmak için:

```bash
python3 smartboard_nav.py
```

## PyInstaller ile Derleme (Binary) Kılavuzu

Uygulamayı Python yüklü olmayan veya kod dosyalarıyla uğraşılmak istenmeyen tahtalara taşımak için tek bir executable dosyası oluşturabilirsiniz.

Bağımlılıkları izole etmek için bir sanal ortam oluşturun ve aktif edin:

```bash
python3 -m venv build_env
source build_env/bin/activate
```

Gerekli paketleme aracını yükleyin:

```bash
pip install pyinstaller
```

ya da eğer Python paketleri sistem tarafından yönetiliyor ise, oluşturduğumuz sanal ortamdaki paketleri bağımsız şekilde pip ile yükleyebilmek için bunu kullanın:

```bash
pip install pyinstaller --break-system-packages
```

Uygulamayı, arka plan terminali açılmayacak ve tek dosya olacak şekilde derleyin:

```bash
pyinstaller --onefile --noconsole smartboard_nav.py
```

Derleme tamamlandığında dist/ dizini içerisinde smartboard_nav isimli tek bir dosya oluşacaktır. Bu dosyayı herhangi bir Pardus tahtasına taşıyıp doğrudan çalıştırabilirsiniz.

## Proje Notları ve Uyarılar

Bu projede bulunan kodlar bir yapay zeka aracı ile (Gemini 3.1 Pro) hazırlanmış olup, bir insan tarafından derlenip test edilmiştir.

Amacı, bir sanal klavye görevi görerek sunum esnasında slayt geçişlerini kolaylaştırmaktır.

Akıllı tahtalarda kullanmadan önce sistem yöneticinize danışınız.
