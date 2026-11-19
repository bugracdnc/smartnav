# SmartNav

[![CI](https://github.com/bugracdnc/smartnav/actions/workflows/ci.yml/badge.svg)](https://github.com/bugracdnc/smartnav/actions/workflows/ci.yml)

Pardus ve ETAP akıllı tahtalarda sunum, PDF ve web sayfalarında ileri/geri gitmek için **her zaman üstte duran ◀ ▶ düğmeleri**. Klavyeye uzanmadan, dokunarak slayt değiştirin.

*Always-on-top, touch-friendly ◀ ▶ buttons that send Left/Right key presses, for presentations on Pardus/ETAP smart boards.*

![SmartNav](docs/smartnav.png)

## Kurulum

**Yönetici şifresi gerekmez.** Uçbirimi (Terminal) açıp:

```sh
wget -qO- https://raw.githubusercontent.com/bugracdnc/smartnav/main/packaging/pardus/kur.sh | sh
```

- **İnternetsiz / USB ile:** [Sürümler](https://github.com/bugracdnc/smartnav/releases) sayfasından `smartnav-pardus.tar.gz` dosyasını indirin, USB'ye koyun. Tahtada açıp klasörün içindeki `kur.sh`'yi çalıştırın (`sh kur.sh`).
- **Paket olarak (yönetici varsa):** `.deb` dosyasını indirip çift tıklayın.
- **Kaldırmak:** `sh ~/.local/share/smartnav/kaldir.sh`

Güncellemek için kurulumu yeniden çalıştırın; ayarlarınız korunur.

## Kullanım

- **◀ / ▶** önceki / sonraki slayt (sol/sağ ok tuşu gönderir; LibreOffice Impress, PDF görüntüleyiciler ve tarayıcıda çalışır).
- Üst çubuktan tutup **sürükleyin**; konum hatırlanır.
- **⚙** ayar dosyasını açar, **✕** kapatır.

`~/.config/smartnav/config.ini`:

```ini
[Display]
scale = auto          ; auto = ekran yüksekliğine göre (4K tahtada 2x), ya da 1.5 gibi bir sayı
resolution = auto     ; ya da 300x120

[Keys]
previous = Left       ; bazı programlar için Prior / Next (Page Up / Page Down)
next = Right
```

## Gereksinimler

X11 masaüstü oturumu (Pardus XFCE bu bilgisayarda X11 ile çalışıyor; ETAP tahtasında `echo $XDG_SESSION_TYPE` ile kontrol edebilirsiniz). Wayland oturumlarında tuş gönderilemez; düğmelerin yerinde bunu söyleyen bir uyarı görünür. Hazır derlenmiş dosya Python gerektirmez. `.deb` paketi sistemdeki `python3-tk`'yı kullanır.

## Geliştirme

```sh
python3 smartnav.py                    # çalıştır
python3 -m unittest -v                 # testler
SMARTNAV_X_TEST=1 xvfb-run -a python3 -m unittest -v   # gerçek tuş gönderimi testi dahil
sh scripts/release.sh                  # release/: binary, .deb, USB paketi (podman/docker gerekir)
```

Sürüm yayınlamak: `smartnav.py` içindeki `__version__`'ı artırıp `git tag v1.0.0 && git push --tags`. CI dosyaları sürüme ekler.

---

İlk sürüm bir yapay zekâ aracıyla (Gemini) hazırlanıp bir insan tarafından denenmiştir; 1.0 sürümü Claude ile yeniden düzenlenip test edilmiştir. Kullanmadan önce okulunuzun BT sorumlusuna danışabilirsiniz.
