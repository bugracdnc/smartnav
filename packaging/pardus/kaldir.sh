#!/bin/sh
# SmartNav'ı kaldırır (kur.sh ile kurulduysa). Ayarlar ~/.config/smartnav içinde kalır.
set -u
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
DESKTOP=$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Masaüstü")
rm -f "$DATA/applications/smartnav.desktop" "$DESKTOP/smartnav.desktop"
rm -f "$DATA/smartnav/smartnav" "$DATA/smartnav/smartnav.svg" "$DATA/smartnav/kaldir.sh"
rmdir "$DATA/smartnav" 2>/dev/null || true
echo "SmartNav kaldırıldı."
