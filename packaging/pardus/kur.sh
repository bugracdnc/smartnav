#!/bin/sh
# SmartNav — Pardus/ETAP kurulumu. Yönetici şifresi gerekmez; yalnızca bu kullanıcıya kurar:
#   ~/.local/share/smartnav/        program
#   ~/.local/share/applications/    uygulama menüsü
#   Masaüstü                        kısayol
# Güncellemek için yeniden çalıştırın; ayarlar (~/.config/smartnav) korunur.
#
#   wget -qO- https://raw.githubusercontent.com/bugracdnc/smartnav/main/packaging/pardus/kur.sh | sh
# İnternetsiz: release'teki smartnav-pardus.tar.gz'yi açıp içindeki kur.sh'yi çalıştırın.
set -eu

REPO="bugracdnc/smartnav"
APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/smartnav"
MENU_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"

fail() { echo "HATA: $1" >&2; exit 1; }
fetch() {
    if command -v wget >/dev/null 2>&1; then wget -q -O "$2" "$1"
    elif command -v curl >/dev/null 2>&1; then curl -fsSL -o "$2" "$1"
    else fail "wget ya da curl bulunamadı."
    fi
}

[ "$(uname -m)" = x86_64 ] || fail "Bu sürüm yalnızca 64-bit (x86_64) tahtalar içindir."

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

SRC=""
case "$0" in */*) SRC=$(dirname "$0") ;; esac
if [ -n "$SRC" ] && [ -f "$SRC/smartnav" ] && [ -f "$SRC/smartnav.desktop" ]; then
    echo "Yerel dosyalar kullanılıyor..."
    cp "$SRC/smartnav" "$SRC/smartnav.svg" "$SRC/smartnav.desktop" "$TMP/"
else
    echo "En yeni sürüm indiriliyor..."
    BASE="https://github.com/$REPO/releases/latest/download"
    fetch "$BASE/smartnav-x86_64" "$TMP/smartnav" || fail "İndirilemedi. İnternet bağlantısını kontrol edin."
    RAW="https://raw.githubusercontent.com/$REPO/main/packaging/pardus"
    fetch "$RAW/smartnav.svg" "$TMP/smartnav.svg"
    fetch "$RAW/smartnav.desktop" "$TMP/smartnav.desktop"
fi

mkdir -p "$APP_DIR" "$MENU_DIR"
cp "$TMP/smartnav" "$TMP/smartnav.svg" "$APP_DIR/"
chmod 755 "$APP_DIR/smartnav"
sed -e "s|@EXEC@|\"$APP_DIR/smartnav\"|" -e "s|@ICON@|$APP_DIR/smartnav.svg|" \
    "$TMP/smartnav.desktop" > "$MENU_DIR/smartnav.desktop"

DESKTOP=$(xdg-user-dir DESKTOP 2>/dev/null || true)
[ -n "$DESKTOP" ] && [ "$DESKTOP" != "$HOME" ] || DESKTOP="$HOME/Masaüstü"
if [ -d "$DESKTOP" ]; then
    cp "$MENU_DIR/smartnav.desktop" "$DESKTOP/smartnav.desktop"
    chmod 755 "$DESKTOP/smartnav.desktop"
    gio set "$DESKTOP/smartnav.desktop" metadata::trusted true 2>/dev/null || true  # GNOME/XFCE "güvenilir" işareti
fi
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$MENU_DIR" 2>/dev/null || true

echo "SmartNav kuruldu. Menüden ya da masaüstündeki simgeden açabilirsiniz."
echo "Kaldırmak için: sh \"$APP_DIR/kaldir.sh\""
[ -n "$SRC" ] && [ -f "$SRC/kaldir.sh" ] && cp "$SRC/kaldir.sh" "$APP_DIR/" || fetch "https://raw.githubusercontent.com/$REPO/main/packaging/pardus/kaldir.sh" "$APP_DIR/kaldir.sh" || true
